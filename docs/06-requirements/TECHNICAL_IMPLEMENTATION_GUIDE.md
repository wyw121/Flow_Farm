# Flow Farm 垂直行业技术实现指南

**项目定位**: 市场调研与客户拜访管理平台  
**技术架构**: Rust + React + Tauri  
**创建时间**: 2025年10月28日  
**文档版本**: v1.0

---

## 📚 文档概览

本文档详细说明 Flow Farm 从**社交媒体自动化工具**转型为**市场调研与客户拜访管理平台**的技术实现方案。

### 核心转变对比

| 维度 | 转变前（社交媒体自动化） | 转变后（市场调研与客户拜访） |
|------|------------------------|----------------------------|
| **核心业务** | 多平台自动关注、精准获客 | 问卷设计、拜访跟踪、数据分析 |
| **主要用户** | 社媒运营人员 | 调研经理、外勤销售 |
| **数据类型** | 社交用户信息、关注统计 | 调研数据、客户档案、拜访记录 |
| **移动端需求** | 设备管理、任务监控 | 实地拜访、离线记录、GPS定位 |
| **分析重点** | 关注转化率、用户画像 | 市场洞察、客户画像、商机预测 |

---

## 1. 数据库模型重新设计

### 1.1 废弃的社交媒体相关表

```sql
-- 以下表将被废弃或重新设计用途
DROP TABLE IF EXISTS social_accounts;      -- 社交账号管理
DROP TABLE IF EXISTS follow_tasks;         -- 关注任务
DROP TABLE IF EXISTS contact_imports;      -- 通讯录导入 
DROP TABLE IF EXISTS platform_automations; -- 平台自动化脚本
DROP TABLE IF EXISTS device_connections;   -- ADB设备连接
```

### 1.2 新增的市场调研业务表

#### 问卷相关表结构

```sql
-- 问卷模板表
CREATE TABLE surveys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,                    -- 问卷标题
    description TEXT,                       -- 问卷描述
    structure JSON NOT NULL,                -- 问卷结构（题目、选项、逻辑跳转）
    status TEXT NOT NULL DEFAULT 'draft',   -- draft/published/closed/archived
    target_sample_size INTEGER DEFAULT 100, -- 目标样本数
    start_date DATE,                        -- 开始时间
    end_date DATE,                          -- 结束时间
    created_by INTEGER NOT NULL,            -- 创建人（调研经理）
    company_id INTEGER NOT NULL,            -- 所属公司
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- 问卷回答表
CREATE TABLE survey_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    survey_id INTEGER NOT NULL,
    respondent_type TEXT NOT NULL,          -- 'anonymous'/'customer'/'employee'
    respondent_info JSON,                   -- 答题人信息（可匿名）
    answers JSON NOT NULL,                  -- 答案数据
    completion_status TEXT DEFAULT 'partial', -- partial/completed/invalid
    submission_source TEXT,                 -- 'web'/'mobile'/'field_worker'
    ip_address TEXT,                        -- IP地址（匿名统计用）
    user_agent TEXT,                        -- 浏览器信息
    location_lat REAL,                      -- GPS纬度（现场填写）
    location_lng REAL,                      -- GPS经度（现场填写）
    field_worker_id INTEGER,                -- 外勤人员ID（协助填写时）
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (survey_id) REFERENCES surveys(id),
    FOREIGN KEY (field_worker_id) REFERENCES users(id)
);
```

#### 客户管理相关表

```sql
-- 客户档案表（替代原social_accounts表）
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,             -- 客户公司名称
    industry TEXT,                          -- 行业分类
    company_size TEXT,                      -- 公司规模（small/medium/large）
    annual_revenue DECIMAL(15,2),           -- 年营收（万元）
    employee_count INTEGER,                 -- 员工数量
    
    -- 联系信息
    contact_person TEXT,                    -- 联系人姓名
    contact_title TEXT,                     -- 联系人职位
    contact_phone TEXT,                     -- 联系电话
    contact_email TEXT,                     -- 联系邮箱
    contact_wechat TEXT,                    -- 微信号
    
    -- 地址信息
    address TEXT,                           -- 详细地址
    city TEXT,                              -- 城市
    province TEXT,                          -- 省份
    postal_code TEXT,                       -- 邮编
    latitude REAL,                          -- GPS纬度
    longitude REAL,                         -- GPS经度
    
    -- 业务信息
    customer_level TEXT DEFAULT 'C',        -- A/B/C级客户
    customer_status TEXT DEFAULT 'potential', -- potential/interested/negotiating/deal/lost
    source TEXT,                            -- 客户来源（exhibition/referral/cold_call/website）
    assigned_sales_id INTEGER,             -- 分配的销售人员
    
    -- 元数据
    company_id INTEGER NOT NULL,           -- 所属公司
    created_by INTEGER NOT NULL,           -- 创建人
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (assigned_sales_id) REFERENCES users(id),
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 拜访记录表（核心新功能）
CREATE TABLE visit_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,          -- 客户ID
    field_worker_id INTEGER NOT NULL,      -- 外勤人员ID
    
    -- 计划信息
    planned_date DATE,                      -- 计划拜访日期
    planned_start_time TIME,                -- 计划开始时间
    planned_duration INTEGER,               -- 计划时长（分钟）
    visit_purpose TEXT,                     -- 拜访目的
    
    -- 实际执行
    actual_start_time TIMESTAMP,           -- 实际开始时间
    actual_end_time TIMESTAMP,             -- 实际结束时间
    arrival_location_lat REAL,             -- 到达位置纬度
    arrival_location_lng REAL,             -- 到达位置经度
    location_accuracy REAL,                -- GPS精度（米）
    
    -- 拜访内容
    visit_summary TEXT,                     -- 拜访总结
    customer_feedback JSON,                 -- 客户反馈（结构化）
    business_opportunities JSON,            -- 商机信息
    competitor_info JSON,                   -- 竞品信息
    follow_up_plan TEXT,                    -- 后续跟进计划
    
    -- 多媒体记录
    photos JSON,                            -- 照片URL数组
    audio_recording TEXT,                   -- 录音文件URL
    voice_to_text TEXT,                     -- 语音转文字内容
    
    -- 状态和评分
    visit_status TEXT DEFAULT 'planned',   -- planned/in_progress/completed/cancelled
    visit_rating INTEGER,                  -- 拜访效果评分（1-5）
    customer_satisfaction INTEGER,         -- 客户满意度（1-5）
    
    -- 元数据
    company_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (field_worker_id) REFERENCES users(id),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- 商机跟踪表
CREATE TABLE business_opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    visit_record_id INTEGER,               -- 来源拜访记录
    
    -- 商机基本信息
    opportunity_name TEXT NOT NULL,        -- 商机名称
    description TEXT,                      -- 商机描述
    estimated_value DECIMAL(12,2),         -- 预估金额（万元）
    estimated_close_date DATE,             -- 预计成交时间
    probability DECIMAL(5,2),              -- 成交概率（0-100%）
    
    -- 商机阶段
    stage TEXT DEFAULT 'initial',          -- initial/requirement/proposal/negotiation/closed_won/closed_lost
    stage_updated_at TIMESTAMP,            -- 阶段更新时间
    
    -- 产品信息
    product_interest JSON,                  -- 感兴趣的产品
    quantity_needed INTEGER,               -- 需求数量
    budget_range TEXT,                     -- 预算范围
    decision_timeline TEXT,                -- 决策时间线
    
    -- 关键联系人
    decision_makers JSON,                   -- 决策人信息
    influencers JSON,                       -- 影响者信息
    
    -- 竞争分析
    competitors JSON,                       -- 竞争对手情况
    our_advantages TEXT,                    -- 我方优势
    risk_factors TEXT,                      -- 风险因素
    
    -- 跟进记录
    follow_up_actions JSON,                 -- 后续行动计划
    next_contact_date DATE,                 -- 下次联系日期
    
    -- 责任人
    assigned_sales_id INTEGER NOT NULL,    -- 负责销售
    
    -- 元数据
    company_id INTEGER NOT NULL,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (visit_record_id) REFERENCES visit_records(id),
    FOREIGN KEY (assigned_sales_id) REFERENCES users(id),
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

#### 费用管理相关表

```sql
-- 费用报销表（重新设计）
CREATE TABLE expense_claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,          -- 报销人
    visit_record_id INTEGER,               -- 关联拜访记录（可选）
    
    -- 费用基本信息
    expense_type TEXT NOT NULL,            -- transportation/meals/accommodation/communication/entertainment/other
    amount DECIMAL(10,2) NOT NULL,         -- 报销金额
    currency TEXT DEFAULT 'CNY',           -- 币种
    expense_date DATE NOT NULL,            -- 费用发生日期
    description TEXT,                      -- 费用说明
    
    -- 发票信息
    invoice_number TEXT,                   -- 发票号码
    invoice_photo_url TEXT,                -- 发票照片URL
    invoice_verification_status TEXT DEFAULT 'pending', -- pending/verified/invalid
    invoice_verification_details JSON,     -- 发票验证详情
    
    -- 地理信息
    expense_location TEXT,                 -- 费用发生地点
    expense_lat REAL,                      -- 费用发生位置纬度
    expense_lng REAL,                      -- 费用发生位置经度
    
    -- 审批流程
    status TEXT DEFAULT 'submitted',       -- submitted/approved/rejected/paid/cancelled
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_by INTEGER,                   -- 审批人
    approved_at TIMESTAMP,                 -- 审批时间
    approval_comments TEXT,                -- 审批意见
    
    -- 支付信息
    payment_method TEXT,                   -- bank_transfer/cash/corporate_card
    payment_status TEXT DEFAULT 'pending', -- pending/paid/failed
    payment_date DATE,                     -- 支付日期
    payment_reference TEXT,               -- 支付凭证号
    
    -- 预算控制
    budget_category TEXT,                  -- 预算类别
    budget_period TEXT,                    -- 预算期间（月度/季度/年度）
    
    -- 元数据
    company_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (employee_id) REFERENCES users(id),
    FOREIGN KEY (visit_record_id) REFERENCES visit_records(id),
    FOREIGN KEY (approved_by) REFERENCES users(id),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- 预算管理表
CREATE TABLE budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    budget_name TEXT NOT NULL,             -- 预算名称
    budget_type TEXT NOT NULL,             -- department/project/employee/category
    budget_period TEXT NOT NULL,           -- monthly/quarterly/yearly
    budget_year INTEGER NOT NULL,          -- 预算年度
    budget_period_number INTEGER,          -- 期间号（月份/季度）
    
    -- 预算分配
    total_budget DECIMAL(12,2) NOT NULL,   -- 总预算金额
    allocated_budget DECIMAL(12,2) DEFAULT 0, -- 已分配预算
    used_budget DECIMAL(12,2) DEFAULT 0,   -- 已使用预算
    remaining_budget DECIMAL(12,2) DEFAULT 0, -- 剩余预算
    
    -- 预算维度
    department_id INTEGER,                 -- 部门ID（如果是部门预算）
    employee_id INTEGER,                   -- 员工ID（如果是个人预算）
    expense_category TEXT,                 -- 费用类别（如果是类别预算）
    
    -- 预警设置
    warning_threshold DECIMAL(5,2) DEFAULT 80, -- 预警阈值（百分比）
    alert_threshold DECIMAL(5,2) DEFAULT 95,   -- 告警阈值（百分比）
    
    -- 状态
    status TEXT DEFAULT 'active',          -- active/frozen/closed
    
    -- 元数据
    company_id INTEGER NOT NULL,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (employee_id) REFERENCES users(id),
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

---

## 2. API 端点重新设计

### 2.1 废弃的社交媒体 API 端点

```rust
// 以下 API 端点将被移除或重新设计
// src/handlers/social_automation.rs - 删除整个文件
// src/handlers/device_management.rs - 删除整个文件
// src/handlers/follow_tasks.rs - 删除整个文件
```

### 2.2 新增的市场调研 API 端点

#### 问卷管理 API（src/handlers/surveys.rs）

```rust
use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::Json,
    routing::{get, post, put, delete},
    Router,
};
use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateSurveyRequest {
    pub title: String,
    pub description: Option<String>,
    pub structure: serde_json::Value,  // 问卷结构JSON
    pub target_sample_size: Option<i32>,
    pub start_date: Option<String>,
    pub end_date: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SurveyResponse {
    pub id: i32,
    pub title: String,
    pub description: Option<String>,
    pub structure: serde_json::Value,
    pub status: String,
    pub target_sample_size: Option<i32>,
    pub current_responses: i32,
    pub completion_rate: f64,
    pub start_date: Option<String>,
    pub end_date: Option<String>,
    pub created_at: String,
    pub updated_at: String,
}

// 创建问卷
pub async fn create_survey(
    State(pool): State<SqlitePool>,
    Json(request): Json<CreateSurveyRequest>,
) -> Result<Json<SurveyResponse>, StatusCode> {
    // 实现创建问卷逻辑
    // 1. 验证问卷结构JSON格式
    // 2. 检查用户权限（只有调研经理可以创建）
    // 3. 插入数据库
    // 4. 返回创建的问卷信息
    todo!()
}

// 获取问卷列表
pub async fn list_surveys(
    State(pool): State<SqlitePool>,
    Query(params): Query<SurveyListParams>,
) -> Result<Json<Vec<SurveyResponse>>, StatusCode> {
    // 支持分页、筛选、排序
    todo!()
}

// 获取问卷详情
pub async fn get_survey(
    State(pool): State<SqlitePool>,
    Path(survey_id): Path<i32>,
) -> Result<Json<SurveyResponse>, StatusCode> {
    todo!()
}

// 发布问卷
pub async fn publish_survey(
    State(pool): State<SqlitePool>,
    Path(survey_id): Path<i32>,
) -> Result<StatusCode, StatusCode> {
    // 1. 检查问卷状态
    // 2. 验证问卷结构完整性
    // 3. 更新状态为 published
    // 4. 生成问卷链接和二维码
    todo!()
}

// 问卷统计分析
pub async fn survey_analytics(
    State(pool): State<SqlitePool>,
    Path(survey_id): Path<i32>,
) -> Result<Json<SurveyAnalytics>, StatusCode> {
    // 返回问卷的统计分析结果
    todo!()
}

pub fn survey_routes() -> Router<SqlitePool> {
    Router::new()
        .route("/surveys", post(create_survey).get(list_surveys))
        .route("/surveys/:id", get(get_survey).put(update_survey).delete(delete_survey))
        .route("/surveys/:id/publish", post(publish_survey))
        .route("/surveys/:id/analytics", get(survey_analytics))
        .route("/surveys/:id/responses", get(list_survey_responses))
}
```

#### 客户拜访 API（src/handlers/visits.rs）

```rust
use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::Json,
    routing::{get, post, put},
    Router,
};

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateVisitRequest {
    pub customer_id: i32,
    pub planned_date: String,
    pub planned_start_time: String,
    pub planned_duration: i32,  // 分钟
    pub visit_purpose: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct StartVisitRequest {
    pub arrival_lat: f64,
    pub arrival_lng: f64,
    pub location_accuracy: f64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct VisitUpdateRequest {
    pub visit_summary: Option<String>,
    pub customer_feedback: Option<serde_json::Value>,
    pub business_opportunities: Option<serde_json::Value>,
    pub competitor_info: Option<serde_json::Value>,
    pub follow_up_plan: Option<String>,
    pub visit_rating: Option<i32>,
    pub customer_satisfaction: Option<i32>,
}

// 创建拜访计划
pub async fn create_visit_plan(
    State(pool): State<SqlitePool>,
    Json(request): Json<CreateVisitRequest>,
) -> Result<Json<VisitRecord>, StatusCode> {
    // 1. 验证客户存在
    // 2. 检查时间冲突
    // 3. 创建拜访记录
    todo!()
}

// 开始拜访（GPS签到）
pub async fn start_visit(
    State(pool): State<SqlitePool>,
    Path(visit_id): Path<i32>,
    Json(request): Json<StartVisitRequest>,
) -> Result<StatusCode, StatusCode> {
    // 1. 验证GPS位置与客户地址匹配
    // 2. 更新拜访状态为进行中
    // 3. 记录实际开始时间和位置
    todo!()
}

// 上传拜访照片
pub async fn upload_visit_photos(
    State(pool): State<SqlitePool>,
    Path(visit_id): Path<i32>,
    // 多part文件上传处理
) -> Result<Json<Vec<String>>, StatusCode> {
    // 1. 验证文件格式（JPEG/PNG）
    // 2. 添加水印（时间+GPS+版权）
    // 3. 上传到对象存储
    // 4. 更新拜访记录
    todo!()
}

// 语音录制上传
pub async fn upload_visit_audio(
    State(pool): State<SqlitePool>,
    Path(visit_id): Path<i32>,
    // 音频文件上传
) -> Result<Json<AudioUploadResponse>, StatusCode> {
    // 1. 验证音频格式
    // 2. 调用语音转文字API（科大讯飞/百度）
    // 3. 存储音频文件和转录文本
    // 4. AI分析提取关键信息
    todo!()
}

// 结束拜访
pub async fn end_visit(
    State(pool): State<SqlitePool>,
    Path(visit_id): Path<i32>,
    Json(request): Json<VisitUpdateRequest>,
) -> Result<StatusCode, StatusCode> {
    // 1. 更新拜访总结信息
    // 2. 记录结束时间
    // 3. 计算拜访时长
    // 4. 更新状态为已完成
    // 5. 自动通知调研经理
    todo!()
}

pub fn visit_routes() -> Router<SqlitePool> {
    Router::new()
        .route("/visits", post(create_visit_plan).get(list_visits))
        .route("/visits/:id/start", post(start_visit))
        .route("/visits/:id/photos", post(upload_visit_photos))
        .route("/visits/:id/audio", post(upload_visit_audio))
        .route("/visits/:id/end", post(end_visit))
        .route("/visits/:id", get(get_visit_detail).put(update_visit))
}
```

---

## 3. 前端组件重新设计

### 3.1 废弃的社交媒体相关组件

```typescript
// 以下组件将被删除或重构
// src/components/DeviceManagement/ - 设备管理组件
// src/components/SocialPlatforms/ - 社交平台组件  
// src/components/FollowTasks/ - 关注任务组件
// src/components/ContactImport/ - 通讯录导入组件
```

### 3.2 新增的市场调研组件

#### 问卷设计器组件（src/components/SurveyDesigner/）

```typescript
// SurveyDesigner.tsx - 主设计器组件
import React, { useState } from 'react';
import { Card, Button, Form, Input, Select, Space, Divider } from 'antd';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';

interface QuestionItem {
  id: string;
  type: 'single_choice' | 'multiple_choice' | 'text' | 'scale' | 'matrix' | 'ranking';
  title: string;
  description?: string;
  required: boolean;
  options?: string[];
  validation?: {
    minLength?: number;
    maxLength?: number;
    pattern?: string;
  };
  logic?: {
    jumpTo?: string;
    condition?: string;
  };
}

const SurveyDesigner: React.FC = () => {
  const [questions, setQuestions] = useState<QuestionItem[]>([]);
  const [selectedQuestion, setSelectedQuestion] = useState<string | null>(null);

  // 拖拽重排序
  const handleDragEnd = (result: any) => {
    if (!result.destination) return;
    
    const items = Array.from(questions);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);
    
    setQuestions(items);
  };

  // 添加题目
  const addQuestion = (type: QuestionItem['type']) => {
    const newQuestion: QuestionItem = {
      id: `q_${Date.now()}`,
      type,
      title: getDefaultTitle(type),
      required: false,
      options: type.includes('choice') ? ['选项1', '选项2'] : undefined,
    };
    setQuestions([...questions, newQuestion]);
    setSelectedQuestion(newQuestion.id);
  };

  return (
    <div className="survey-designer">
      <div className="designer-header">
        <h2>问卷设计器</h2>
        <Space>
          <Button onClick={() => saveDraft()}>保存草稿</Button>
          <Button type="primary" onClick={() => publishSurvey()}>
            发布问卷
          </Button>
        </Space>
      </div>

      <div className="designer-content">
        {/* 左侧题型工具栏 */}
        <div className="question-types-panel">
          <Card title="题型选择" size="small">
            <div className="question-type-grid">
              <Button 
                block 
                onClick={() => addQuestion('single_choice')}
                icon={<RadioIcon />}
              >
                单选题
              </Button>
              <Button 
                block 
                onClick={() => addQuestion('multiple_choice')}
                icon={<CheckboxIcon />}
              >
                多选题
              </Button>
              <Button 
                block 
                onClick={() => addQuestion('text')}
                icon={<TextIcon />}
              >
                填空题
              </Button>
              <Button 
                block 
                onClick={() => addQuestion('scale')}
                icon={<SliderIcon />}
              >
                量表题
              </Button>
              <Button 
                block 
                onClick={() => addQuestion('matrix')}
                icon={<TableIcon />}
              >
                矩阵题
              </Button>
              <Button 
                block 
                onClick={() => addQuestion('ranking')}
                icon={<SortIcon />}
              >
                排序题
              </Button>
            </div>
          </Card>
        </div>

        {/* 中间问卷预览区 */}
        <div className="survey-preview">
          <Card title="问卷预览" extra={<PreviewModeSwitch />}>
            <DragDropContext onDragEnd={handleDragEnd}>
              <Droppable droppableId="questions">
                {(provided) => (
                  <div {...provided.droppableProps} ref={provided.innerRef}>
                    {questions.map((question, index) => (
                      <Draggable 
                        key={question.id} 
                        draggableId={question.id} 
                        index={index}
                      >
                        {(provided, snapshot) => (
                          <div
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            className={`question-item ${
                              selectedQuestion === question.id ? 'selected' : ''
                            } ${snapshot.isDragging ? 'dragging' : ''}`}
                            onClick={() => setSelectedQuestion(question.id)}
                          >
                            <QuestionRenderer question={question} />
                          </div>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            </DragDropContext>
          </Card>
        </div>

        {/* 右侧属性配置面板 */}
        <div className="question-properties">
          {selectedQuestion && (
            <QuestionPropertiesPanel 
              question={questions.find(q => q.id === selectedQuestion)!}
              onUpdate={(updatedQuestion) => {
                setQuestions(questions.map(q => 
                  q.id === selectedQuestion ? updatedQuestion : q
                ));
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
};
```

#### 移动端拜访记录组件

```typescript
// VisitRecorder.tsx - 移动端拜访记录
import React, { useState, useEffect } from 'react';
import { Card, Button, Input, Upload, message, Timeline, Tag } from 'antd';
import { 
  CameraOutlined, 
  AudioOutlined, 
  EnvironmentOutlined,
  ClockCircleOutlined 
} from '@ant-design/icons';

interface VisitRecorderProps {
  visitId: number;
  customerInfo: Customer;
}

const VisitRecorder: React.FC<VisitRecorderProps> = ({ visitId, customerInfo }) => {
  const [visitStatus, setVisitStatus] = useState<'planned' | 'in_progress' | 'completed'>('planned');
  const [location, setLocation] = useState<{lat: number, lng: number} | null>(null);
  const [photos, setPhotos] = useState<string[]>([]);
  const [audioRecording, setAudioRecording] = useState<boolean>(false);
  const [visitSummary, setVisitSummary] = useState<string>('');

  // GPS定位
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude
          });
        },
        (error) => {
          message.error('无法获取位置信息，请检查GPS权限');
        }
      );
    }
  }, []);

  // 开始拜访
  const startVisit = async () => {
    if (!location) {
      message.error('请先获取位置信息');
      return;
    }

    try {
      await api.post(`/visits/${visitId}/start`, {
        arrival_lat: location.lat,
        arrival_lng: location.lng,
        location_accuracy: 10 // 假设10米精度
      });
      
      setVisitStatus('in_progress');
      message.success('拜访已开始');
    } catch (error) {
      message.error('开始拜访失败');
    }
  };

  // 拍照上传
  const handlePhotoUpload = async (file: File) => {
    const formData = new FormData();
    formData.append('photo', file);
    
    try {
      const response = await api.post(`/visits/${visitId}/photos`, formData);
      setPhotos([...photos, response.data.url]);
      message.success('照片上传成功');
    } catch (error) {
      message.error('照片上传失败');
    }
  };

  // 录音功能
  const toggleAudioRecording = () => {
    if (audioRecording) {
      // 停止录音并上传
      stopRecordingAndUpload();
    } else {
      // 开始录音
      startRecording();
    }
    setAudioRecording(!audioRecording);
  };

  // 结束拜访
  const endVisit = async () => {
    try {
      await api.post(`/visits/${visitId}/end`, {
        visit_summary: visitSummary,
        visit_rating: 5, // 从UI获取
        customer_satisfaction: 5 // 从UI获取
      });
      
      setVisitStatus('completed');
      message.success('拜访记录已保存');
    } catch (error) {
      message.error('保存拜访记录失败');
    }
  };

  return (
    <div className="visit-recorder">
      {/* 客户信息卡片 */}
      <Card 
        title={customerInfo.company_name}
        extra={<Tag color={getStatusColor(visitStatus)}>{getStatusText(visitStatus)}</Tag>}
      >
        <p><EnvironmentOutlined /> {customerInfo.address}</p>
        <p>联系人：{customerInfo.contact_person} ({customerInfo.contact_phone})</p>
        
        {location && (
          <p>
            <EnvironmentOutlined /> 
            当前位置：{location.lat.toFixed(6)}, {location.lng.toFixed(6)}
          </p>
        )}
      </Card>

      {/* 拜访控制 */}
      <Card title="拜访控制" style={{ marginTop: 16 }}>
        {visitStatus === 'planned' && (
          <Button 
            type="primary" 
            size="large" 
            block
            onClick={startVisit}
            disabled={!location}
          >
            开始拜访
          </Button>
        )}

        {visitStatus === 'in_progress' && (
          <div className="visit-actions">
            {/* 拍照按钮 */}
            <Upload
              customRequest={({ file }) => handlePhotoUpload(file as File)}
              showUploadList={false}
              accept="image/*"
            >
              <Button icon={<CameraOutlined />} size="large">
                拍照记录
              </Button>
            </Upload>

            {/* 录音按钮 */}
            <Button 
              icon={<AudioOutlined />}
              type={audioRecording ? 'danger' : 'default'}
              size="large"
              onClick={toggleAudioRecording}
            >
              {audioRecording ? '停止录音' : '开始录音'}
            </Button>

            {/* 结束拜访按钮 */}
            <Button 
              type="primary" 
              size="large"
              onClick={endVisit}
              style={{ marginTop: 16 }}
              block
            >
              结束拜访
            </Button>
          </div>
        )}
      </Card>

      {/* 拜访记录 */}
      <Card title="拜访记录" style={{ marginTop: 16 }}>
        <Timeline>
          <Timeline.Item color="green">
            <ClockCircleOutlined /> 计划拜访时间：09:00-11:00
          </Timeline.Item>
          
          {visitStatus !== 'planned' && (
            <Timeline.Item color="blue">
              <ClockCircleOutlined /> 实际开始：{formatTime(new Date())}
            </Timeline.Item>
          )}

          {photos.length > 0 && (
            <Timeline.Item>
              <CameraOutlined /> 已拍摄照片：{photos.length}张
            </Timeline.Item>
          )}

          {audioRecording && (
            <Timeline.Item color="red">
              <AudioOutlined /> 正在录音...
            </Timeline.Item>
          )}
        </Timeline>

        {/* 拜访总结输入 */}
        <Input.TextArea
          placeholder="请输入拜访总结..."
          value={visitSummary}
          onChange={(e) => setVisitSummary(e.target.value)}
          rows={4}
          style={{ marginTop: 16 }}
        />
      </Card>
    </div>
  );
};
```

---

## 4. Tauri 外勤客户端架构

### 4.1 主要功能模块重新设计

```rust
// src-tauri/src/main.rs - 主入口重构
use tauri::Manager;

mod visit_recorder;     // 拜访记录模块（新）
mod gps_tracker;        // GPS定位模块（新）
mod photo_handler;      // 照片处理模块（新）
mod audio_recorder;     // 录音模块（新）
mod offline_sync;       // 离线同步模块（新）
mod expense_manager;    // 费用管理模块（新）

// 删除的模块
// mod adb_manager;     // ADB设备管理（删除）
// mod automation;      // 自动化脚本（删除）

#[tauri::command]
async fn start_visit_recording(visit_id: i32, customer_lat: f64, customer_lng: f64) -> Result<String, String> {
    // 1. 获取当前GPS位置
    let current_location = gps_tracker::get_current_location().await?;
    
    // 2. 验证位置是否匹配（允许100米误差）
    let distance = gps_tracker::calculate_distance(
        current_location.lat, current_location.lng,
        customer_lat, customer_lng
    );
    
    if distance > 100.0 {
        return Err("当前位置与客户地址不匹配，请确认您在正确的位置".to_string());
    }
    
    // 3. 开始拜访记录
    visit_recorder::start_visit(visit_id, current_location).await?;
    
    Ok("拜访记录已开始".to_string())
}

#[tauri::command]
async fn capture_visit_photo(visit_id: i32) -> Result<String, String> {
    // 1. 调用系统相机
    let photo_path = photo_handler::capture_photo().await?;
    
    // 2. 添加水印（时间+GPS+版权信息）
    let watermarked_path = photo_handler::add_watermark(
        &photo_path, 
        &get_current_time(),
        &get_current_location().await?,
        "©Flow Farm 拜访记录"
    ).await?;
    
    // 3. 上传到服务器（如果有网络）
    if offline_sync::is_online().await {
        photo_handler::upload_photo(visit_id, &watermarked_path).await?;
    } else {
        // 离线模式：添加到同步队列
        offline_sync::queue_photo_upload(visit_id, watermarked_path).await?;
    }
    
    Ok("照片已记录".to_string())
}

#[tauri::command]
async fn start_audio_recording(visit_id: i32) -> Result<String, String> {
    audio_recorder::start_recording(visit_id).await?;
    Ok("录音已开始".to_string())
}

#[tauri::command]
async fn stop_audio_recording(visit_id: i32) -> Result<String, String> {
    // 1. 停止录音
    let audio_file = audio_recorder::stop_recording(visit_id).await?;
    
    // 2. 语音转文字（离线引擎）
    let transcript = audio_recorder::speech_to_text(&audio_file).await?;
    
    // 3. 上传音频和文本
    if offline_sync::is_online().await {
        audio_recorder::upload_audio_and_text(visit_id, &audio_file, &transcript).await?;
    } else {
        offline_sync::queue_audio_upload(visit_id, audio_file, transcript).await?;
    }
    
    Ok("录音已保存".to_string())
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            start_visit_recording,
            capture_visit_photo,
            start_audio_recording,
            stop_audio_recording,
            sync_offline_data,
            get_customer_info,
            submit_expense_claim
        ])
        .setup(|app| {
            // 初始化本地数据库
            let app_handle = app.handle();
            tauri::async_runtime::spawn(async move {
                offline_sync::init_local_database(&app_handle).await.unwrap();
            });
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### 4.2 离线同步机制

```rust
// src-tauri/src/offline_sync.rs
use sqlx::{SqlitePool, sqlite::SqliteConnectOptions};
use serde::{Serialize, Deserialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct PendingUpload {
    pub id: i32,
    pub upload_type: String,  // "photo", "audio", "visit_record", "expense"
    pub data: serde_json::Value,
    pub file_path: Option<String>,
    pub created_at: String,
    pub retry_count: i32,
}

pub async fn init_local_database(app_handle: &tauri::AppHandle) -> Result<SqlitePool, sqlx::Error> {
    let app_dir = app_handle.path_resolver()
        .app_data_dir()
        .expect("failed to resolve app data dir");
    
    std::fs::create_dir_all(&app_dir).expect("failed to create app data dir");
    
    let database_url = format!("sqlite:///{}/offline.db", app_dir.to_str().unwrap());
    
    let options = SqliteConnectOptions::new()
        .filename(&database_url)
        .create_if_missing(true);
    
    let pool = SqlitePool::connect_with(options).await?;
    
    // 创建离线数据表
    sqlx::query(r#"
        CREATE TABLE IF NOT EXISTS pending_uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            upload_type TEXT NOT NULL,
            data TEXT NOT NULL,
            file_path TEXT,
            created_at TEXT NOT NULL,
            retry_count INTEGER DEFAULT 0
        )
    "#).execute(&pool).await?;
    
    sqlx::query(r#"
        CREATE TABLE IF NOT EXISTS cached_customers (
            id INTEGER PRIMARY KEY,
            data TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    "#).execute(&pool).await?;
    
    Ok(pool)
}

pub async fn queue_photo_upload(visit_id: i32, photo_path: String) -> Result<(), String> {
    let pool = get_local_pool().await?;
    
    let upload_data = serde_json::json!({
        "visit_id": visit_id,
        "photo_path": photo_path
    });
    
    sqlx::query(r#"
        INSERT INTO pending_uploads (upload_type, data, file_path, created_at)
        VALUES (?, ?, ?, ?)
    "#)
    .bind("photo")
    .bind(upload_data.to_string())
    .bind(&photo_path)
    .bind(chrono::Utc::now().to_rfc3339())
    .execute(&pool)
    .await
    .map_err(|e| e.to_string())?;
    
    Ok(())
}

pub async fn sync_pending_uploads() -> Result<i32, String> {
    let pool = get_local_pool().await?;
    
    let pending_uploads: Vec<PendingUpload> = sqlx::query_as!(
        PendingUpload,
        "SELECT * FROM pending_uploads ORDER BY created_at"
    )
    .fetch_all(&pool)
    .await
    .map_err(|e| e.to_string())?;
    
    let mut synced_count = 0;
    
    for upload in pending_uploads {
        match upload.upload_type.as_str() {
            "photo" => {
                if let Ok(_) = sync_photo_upload(&upload).await {
                    delete_pending_upload(upload.id).await?;
                    synced_count += 1;
                }
            },
            "audio" => {
                if let Ok(_) = sync_audio_upload(&upload).await {
                    delete_pending_upload(upload.id).await?;
                    synced_count += 1;
                }
            },
            "visit_record" => {
                if let Ok(_) = sync_visit_record(&upload).await {
                    delete_pending_upload(upload.id).await?;
                    synced_count += 1;
                }
            },
            _ => {}
        }
    }
    
    Ok(synced_count)
}
```

---

## 5. 配置文件更新

### 5.1 Cargo.toml 依赖更新

```toml
# server-backend/Cargo.toml
[dependencies]
# 保留的核心依赖
axum = "0.7"
tokio = { version = "1.0", features = ["full"] }
sqlx = { version = "0.7", features = ["runtime-tokio-rustls", "sqlite", "chrono", "json"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
anyhow = "1.0"
thiserror = "1.0"
tracing = "0.1"
tower = "0.4"
tower-http = { version = "0.5", features = ["cors", "fs"] }

# 新增的市场调研相关依赖
reqwest = { version = "0.11", features = ["json", "multipart"] }  # HTTP客户端（API调用）
image = "0.24"                                                   # 图像处理（水印）
uuid = { version = "1.0", features = ["v4"] }                   # UUID生成
chrono = { version = "0.4", features = ["serde"] }              # 时间处理
geo = "0.26"                                                     # 地理位置计算
base64 = "0.21"                                                  # Base64编码
mime_guess = "2.0"                                               # MIME类型检测

# 移除的社交媒体相关依赖
# adb_client = "0.8"       # ADB设备连接（删除）
# selenium = "0.1"         # 浏览器自动化（删除）
# webscraper = "0.3"       # 网页抓取（删除）
```

### 5.2 前端 package.json 更新

```json
{
  "name": "flow-farm-frontend",
  "version": "1.0.0",
  "description": "Flow Farm 市场调研与客户拜访管理平台 - 管理后台",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "antd": "^5.12.0",
    "react-router-dom": "^6.8.0",
    "@reduxjs/toolkit": "^1.9.0",
    "react-redux": "^8.0.0",
    "axios": "^1.6.0",
    
    // 新增的市场调研功能依赖
    "react-beautiful-dnd": "^13.1.0",          // 拖拽排序（问卷设计）
    "echarts": "^5.4.0",                       // 图表库（数据可视化）
    "echarts-for-react": "^3.0.0",             // ECharts React封装
    "react-quill": "^2.0.0",                   // 富文本编辑器
    "dayjs": "^1.11.0",                        // 日期处理
    "lodash": "^4.17.0",                       // 工具函数
    "react-hook-form": "^7.48.0",              // 表单处理
    "qrcode.react": "^3.1.0",                  // 二维码生成
    "@ant-design/pro-components": "^2.6.0",    // 高级组件（表格、表单）
    "react-map-gl": "^7.1.0",                  // 地图组件
    "mapbox-gl": "^2.15.0",                    // 地图引擎
    
    // 移除的社交媒体相关依赖
    // "adb-utils": "^2.1.0"                   // ADB工具（删除）
    // "social-platform-apis": "^1.0.0"       // 社交平台API（删除）
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@types/lodash": "^4.14.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.0.0",
    "vite": "^5.0.0"
  }
}
```

### 5.3 Tauri 配置更新

```json
// employee-client/src-tauri/tauri.conf.json
{
  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "devPath": "http://localhost:1420",
    "distDir": "../dist",
    "withGlobalTauri": false
  },
  "package": {
    "productName": "Flow Farm 外勤客户端",
    "version": "1.0.0"
  },
  "tauri": {
    "allowlist": {
      "all": false,
      "shell": {
        "all": false,
        "open": true
      },
      "dialog": {
        "all": false,
        "open": true,
        "save": true
      },
      "fs": {
        "all": false,
        "readFile": true,
        "writeFile": true,
        "createDir": true,
        "removeFile": true,
        "exists": true,
        "scope": ["$APPDATA/*", "$TEMP/*"]
      },
      "http": {
        "all": false,
        "request": true,
        "scope": ["https://api.flowfarm.com/*"]
      },
      "notification": {
        "all": true
      },
      "globalShortcut": {
        "all": true
      },
      "os": {
        "all": false,
        "platform": true,
        "version": true
      },
      // 新增的权限（市场调研功能需要）
      "camera": {
        "all": true  // 拍照功能
      },
      "microphone": {
        "all": true  // 录音功能
      },
      "geolocation": {
        "all": true  // GPS定位
      }
    },
    "bundle": {
      "active": true,
      "targets": "all",
      "identifier": "com.flowfarm.fieldclient",
      "icon": [
        "icons/32x32.png",
        "icons/128x128.png",
        "icons/128x128@2x.png",
        "icons/icon.icns",
        "icons/icon.ico"
      ]
    },
    "security": {
      "csp": null
    },
    "windows": [
      {
        "fullscreen": false,
        "resizable": true,
        "title": "Flow Farm 外勤客户端",
        "width": 1200,
        "height": 800,
        "minWidth": 800,
        "minHeight": 600
      }
    ],
    "systemTray": {
      "iconPath": "icons/icon.png",
      "iconAsTemplate": true,
      "menuOnLeftClick": false
    },
    "updater": {
      "active": true,
      "endpoints": [
        "https://api.flowfarm.com/updates/{{target}}/{{arch}}/{{current_version}}"
      ],
      "dialog": true,
      "pubkey": "your-public-key-here"
    }
  }
}
```

---

## 6. 部署和环境配置

### 6.1 Docker 配置更新

```dockerfile
# server-backend/Dockerfile
FROM rust:1.75 as builder

WORKDIR /app
COPY Cargo.toml Cargo.lock ./
COPY src ./src

# 构建生产版本
RUN cargo build --release

FROM debian:bookworm-slim

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl3 \
    sqlite3 \
    imagemagick \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制编译好的二进制文件
COPY --from=builder /app/target/release/server-backend ./

# 创建必要的目录
RUN mkdir -p uploads photos audio data

# 设置环境变量
ENV RUST_LOG=info
ENV DATABASE_URL=sqlite:data/flowfarm.db
ENV UPLOAD_DIR=/app/uploads
ENV PHOTO_DIR=/app/photos
ENV AUDIO_DIR=/app/audio

EXPOSE 8000

CMD ["./server-backend"]
```

### 6.2 环境变量配置

```bash
# .env.production
# 数据库配置
DATABASE_URL=sqlite:data/flowfarm.db

# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
CORS_ORIGIN=https://flowfarm.com

# 文件存储配置
UPLOAD_DIR=./uploads
PHOTO_STORAGE_TYPE=local  # local/s3/cos
MAX_PHOTO_SIZE=10485760   # 10MB
MAX_AUDIO_SIZE=52428800   # 50MB

# 第三方服务配置
# 语音转文字服务
SPEECH_TO_TEXT_PROVIDER=xfyun  # xfyun/baidu/tencent
XFYUN_APP_ID=your_xfyun_app_id
XFYUN_API_SECRET=your_xfyun_api_secret
XFYUN_API_KEY=your_xfyun_api_key

# 发票验证服务
INVOICE_VERIFICATION_PROVIDER=baidu
BAIDU_OCR_API_KEY=your_baidu_api_key
BAIDU_OCR_SECRET_KEY=your_baidu_secret_key

# 地图服务
MAP_PROVIDER=amap  # amap/baidu/tencent
AMAP_API_KEY=your_amap_api_key

# 邮件服务
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_USERNAME=noreply@flowfarm.com
SMTP_PASSWORD=your_smtp_password

# JWT配置
JWT_SECRET=your_jwt_secret_key
JWT_EXPIRES_IN=7d

# 系统配置
MAX_COMPANIES=1000
MAX_USERS_PER_COMPANY=100
DEFAULT_TIMEZONE=Asia/Shanghai
```

---

## 7. 迁移脚本

### 7.1 数据库迁移脚本

```sql
-- migrations/001_transform_to_market_research.sql
-- 数据迁移：从社交媒体自动化转换为市场调研

BEGIN TRANSACTION;

-- 1. 备份现有数据
CREATE TABLE IF NOT EXISTS backup_users AS SELECT * FROM users;
CREATE TABLE IF NOT EXISTS backup_companies AS SELECT * FROM companies;

-- 2. 删除社交媒体相关表
DROP TABLE IF EXISTS social_accounts;
DROP TABLE IF EXISTS follow_tasks;
DROP TABLE IF EXISTS contact_imports;
DROP TABLE IF EXISTS platform_automations;
DROP TABLE IF EXISTS device_connections;

-- 3. 更新用户角色
UPDATE users SET role = 'research_manager' WHERE role = 'user_admin';
UPDATE users SET role = 'field_worker' WHERE role = 'employee';
-- system_admin 保持不变

-- 4. 创建新的市场调研业务表
-- (使用前面定义的表结构)

-- 5. 迁移work_records表数据到visit_records
INSERT INTO visit_records (
    customer_id, field_worker_id, actual_start_time, actual_end_time,
    visit_summary, company_id, created_at, updated_at
)
SELECT 
    1 as customer_id,  -- 默认客户，需要手动更新
    employee_id as field_worker_id,
    start_time as actual_start_time,
    end_time as actual_end_time,
    task_description as visit_summary,
    company_id,
    created_at,
    updated_at
FROM work_records 
WHERE task_type = 'field_work';

-- 6. 更新配置表
UPDATE system_configs 
SET config_value = 'market_research' 
WHERE config_key = 'business_type';

INSERT OR REPLACE INTO system_configs (config_key, config_value) VALUES
('max_visit_duration_hours', '8'),
('gps_accuracy_threshold_meters', '100'),
('photo_watermark_enabled', 'true'),
('voice_to_text_enabled', 'true'),
('offline_sync_enabled', 'true'),
('expense_approval_required', 'true');

COMMIT;
```

### 7.2 数据清理脚本

```rust
// scripts/cleanup_social_media_data.rs
use sqlx::SqlitePool;
use std::fs;
use std::path::Path;

pub async fn cleanup_legacy_data(pool: &SqlitePool) -> Result<(), Box<dyn std::error::Error>> {
    println!("开始清理社交媒体相关的遗留数据...");
    
    // 1. 清理设备管理相关文件
    let device_data_dir = "./data/devices";
    if Path::new(device_data_dir).exists() {
        fs::remove_dir_all(device_data_dir)?;
        println!("✓ 已删除设备数据目录");
    }
    
    // 2. 清理自动化脚本文件
    let scripts_dir = "./data/automation_scripts";
    if Path::new(scripts_dir).exists() {
        fs::remove_dir_all(scripts_dir)?;
        println!("✓ 已删除自动化脚本目录");
    }
    
    // 3. 清理社交平台配置文件
    let platform_configs = ["./config/xiaohongshu.json", "./config/douyin.json", "./config/kuaishou.json"];
    for config_file in platform_configs.iter() {
        if Path::new(config_file).exists() {
            fs::remove_file(config_file)?;
            println!("✓ 已删除平台配置文件: {}", config_file);
        }
    }
    
    // 4. 清理数据库中的遗留配置
    sqlx::query("DELETE FROM system_configs WHERE config_key LIKE 'social_%'")
        .execute(pool)
        .await?;
    
    sqlx::query("DELETE FROM system_configs WHERE config_key LIKE 'device_%'")
        .execute(pool)
        .await?;
    
    sqlx::query("DELETE FROM system_configs WHERE config_key LIKE 'automation_%'")
        .execute(pool)
        .await?;
    
    println!("✓ 已清理数据库中的遗留配置");
    
    // 5. 创建市场调研相关目录
    let new_dirs = [
        "./data/surveys",
        "./uploads/photos",
        "./uploads/audio", 
        "./uploads/invoices",
        "./exports/reports"
    ];
    
    for dir in new_dirs.iter() {
        fs::create_dir_all(dir)?;
        println!("✓ 已创建目录: {}", dir);
    }
    
    println!("数据清理完成！");
    Ok(())
}
```

---

## 8. 测试策略

### 8.1 业务功能测试用例

```rust
// tests/market_research_integration_tests.rs
use super::*;

#[tokio::test]
async fn test_survey_lifecycle() {
    let app = create_test_app().await;
    
    // 1. 创建问卷
    let survey_request = CreateSurveyRequest {
        title: "工业机器人市场调研".to_string(),
        description: Some("了解客户需求和竞品情况".to_string()),
        structure: serde_json::json!({
            "questions": [
                {
                    "id": "q1",
                    "type": "single_choice",
                    "title": "您公司是否使用工业机器人？",
                    "options": ["是", "否", "计划购买"]
                }
            ]
        }),
        target_sample_size: Some(100),
        start_date: Some("2025-11-01".to_string()),
        end_date: Some("2025-12-31".to_string()),
    };
    
    let response = app.post("/api/surveys")
        .json(&survey_request)
        .send()
        .await;
    
    assert_eq!(response.status(), 201);
    let survey: SurveyResponse = response.json().await;
    assert_eq!(survey.title, "工业机器人市场调研");
    
    // 2. 发布问卷
    let response = app.post(&format!("/api/surveys/{}/publish", survey.id))
        .send()
        .await;
    assert_eq!(response.status(), 200);
    
    // 3. 提交问卷回答
    let answer_request = serde_json::json!({
        "answers": {
            "q1": "是"
        },
        "respondent_info": {
            "company": "测试公司",
            "industry": "制造业"
        }
    });
    
    let response = app.post(&format!("/api/surveys/{}/responses", survey.id))
        .json(&answer_request)
        .send()
        .await;
    assert_eq!(response.status(), 201);
    
    // 4. 获取问卷统计
    let response = app.get(&format!("/api/surveys/{}/analytics", survey.id))
        .send()
        .await;
    assert_eq!(response.status(), 200);
    
    let analytics: SurveyAnalytics = response.json().await;
    assert_eq!(analytics.total_responses, 1);
}

#[tokio::test]
async fn test_visit_recording_workflow() {
    let app = create_test_app().await;
    
    // 1. 创建客户
    let customer = create_test_customer(&app).await;
    
    // 2. 创建拜访计划
    let visit_request = CreateVisitRequest {
        customer_id: customer.id,
        planned_date: "2025-11-01".to_string(),
        planned_start_time: "09:00".to_string(),
        planned_duration: 120,
        visit_purpose: "产品演示和需求了解".to_string(),
    };
    
    let response = app.post("/api/visits")
        .json(&visit_request)
        .send()
        .await;
    
    assert_eq!(response.status(), 201);
    let visit: VisitRecord = response.json().await;
    
    // 3. 开始拜访
    let start_request = StartVisitRequest {
        arrival_lat: 31.2304,
        arrival_lng: 121.4737,
        location_accuracy: 10.0,
    };
    
    let response = app.post(&format!("/api/visits/{}/start", visit.id))
        .json(&start_request)
        .send()
        .await;
    assert_eq!(response.status(), 200);
    
    // 4. 结束拜访
    let end_request = VisitUpdateRequest {
        visit_summary: Some("客户对产品很感兴趣，预计Q1采购".to_string()),
        customer_feedback: Some(serde_json::json!({
            "satisfaction": 5,
            "interest_level": "high"
        })),
        business_opportunities: Some(serde_json::json!({
            "estimated_value": 2500000,
            "probability": 75
        })),
        competitor_info: None,
        follow_up_plan: Some("一周内提供详细方案".to_string()),
        visit_rating: Some(5),
        customer_satisfaction: Some(5),
    };
    
    let response = app.post(&format!("/api/visits/{}/end", visit.id))
        .json(&end_request)
        .send()
        .await;
    assert_eq!(response.status(), 200);
}
```

---

## 9. 总结

### 9.1 转型影响评估

| 影响维度 | 评估结果 | 风险等级 |
|---------|----------|----------|
| **数据库结构** | 需要重大重构，75%的表需要替换 | 🔴 高 |
| **API 接口** | 60%的接口需要重新设计 | 🟡 中 |
| **前端组件** | 70%的组件需要重写 | 🟡 中 |
| **移动端功能** | 功能重点完全转变，需要全面重构 | 🔴 高 |
| **第三方集成** | 从社交平台API转为地图/语音/OCR服务 | 🟡 中 |
| **用户体验** | 完全不同的业务流程，需要重新设计 | 🔴 高 |

### 9.2 开发工作量评估

```
总工作量估算：6-8个月（3-4人团队）

Phase 1: 数据库和后端API重构 (6-8周)
- 数据库迁移脚本开发
- 新API端点实现  
- 核心业务逻辑开发

Phase 2: 前端管理后台重构 (4-6周)
- 问卷设计器开发
- 拜访管理界面
- 数据分析报表

Phase 3: 移动端客户端重构 (6-8周)
- Tauri应用重新设计
- GPS定位和拍照功能
- 离线同步机制

Phase 4: 集成测试和优化 (4-6周)
- 端到端测试
- 性能优化
- 安全加固

Phase 5: 部署和上线 (2-3周)
- 生产环境部署
- 用户培训
- 监控和运维
```

### 9.3 技术风险和缓解措施

**高风险项**:
1. **数据迁移风险**: 制定详细的备份和回滚方案
2. **GPS定位精度**: 多重验证机制，允许手动校正
3. **离线同步复杂性**: 分阶段实现，优先保证核心功能
4. **第三方服务依赖**: 准备备用方案，避免单点故障

**缓解措施**:
- 建立完整的测试环境
- 实施渐进式迁移策略
- 保留原系统作为备份
- 建立用户反馈和快速响应机制

---

**文档状态**: ✅ 已完成  
**审核状态**: 待技术评审  
**实施时间**: 预计2025年11月开始

本技术实现指南为 Flow Farm 从社交媒体自动化工具成功转型为市场调研与客户拜访管理平台提供了详细的技术路线图。

现在完成最后一个内容块：
