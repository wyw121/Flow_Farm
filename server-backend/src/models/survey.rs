use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use validator::Validate;

/// 问卷主体结构
#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct Survey {
    pub id: i32,
    pub title: String,
    pub description: Option<String>,
    pub created_by: i32,  // research_manager ID
    pub company_id: i32,
    pub structure: serde_json::Value,  // 问卷JSON结构
    pub status: String,  // draft, published, closed
    pub target_sample_size: Option<i32>,
    pub current_responses: i32,
    pub start_date: Option<DateTime<Utc>>,
    pub end_date: Option<DateTime<Utc>>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// 问卷回答记录
#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct SurveyResponse {
    pub id: i32,
    pub survey_id: i32,
    pub respondent_info: serde_json::Value,  // 受访者信息
    pub answers: serde_json::Value,  // 回答JSON
    pub location: Option<String>,  // GPS位置
    pub submitted_at: DateTime<Utc>,
    pub device_info: Option<String>,
}

/// 问卷状态枚举
#[derive(Debug, Clone, Serialize, Deserialize, sqlx::Type)]
#[sqlx(type_name = "TEXT")]
#[sqlx(rename_all = "snake_case")]
pub enum SurveyStatus {
    Draft,     // 草稿
    Published, // 已发布
    Closed,    // 已关闭
}

impl std::fmt::Display for SurveyStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            SurveyStatus::Draft => write!(f, "draft"),
            SurveyStatus::Published => write!(f, "published"),
            SurveyStatus::Closed => write!(f, "closed"),
        }
    }
}

/// 创建问卷请求
#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct CreateSurveyRequest {
    #[validate(length(min = 1, max = 200))]
    pub title: String,
    #[validate(length(max = 1000))]
    pub description: Option<String>,
    pub structure: serde_json::Value,
    pub target_sample_size: Option<i32>,
    pub start_date: Option<String>,  // ISO 8601 date string
    pub end_date: Option<String>,    // ISO 8601 date string
}

/// 更新问卷请求
#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct UpdateSurveyRequest {
    #[validate(length(min = 1, max = 200))]
    pub title: Option<String>,
    #[validate(length(max = 1000))]
    pub description: Option<String>,
    pub structure: Option<serde_json::Value>,
    pub target_sample_size: Option<i32>,
    pub start_date: Option<String>,
    pub end_date: Option<String>,
}

/// 问卷回答提交请求
#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct SubmitSurveyResponseRequest {
    pub respondent_info: serde_json::Value,
    pub answers: serde_json::Value,
    pub location: Option<String>,
    pub device_info: Option<String>,
}

/// 问题类型枚举
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum QuestionType {
    SingleChoice,   // 单选题
    MultipleChoice, // 多选题
    Text,          // 文本题
    Number,        // 数字题
    Rating,        // 评分题
    YesNo,         // 是非题
    Date,          // 日期题
    Time,          // 时间题
    Matrix,        // 矩阵题
}

/// 问题结构
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Question {
    pub id: String,
    pub question_type: QuestionType,
    pub title: String,
    pub description: Option<String>,
    pub required: bool,
    pub options: Option<Vec<String>>,  // 选择题选项
    pub validation: Option<serde_json::Value>,  // 验证规则
    pub display_logic: Option<serde_json::Value>,  // 显示逻辑
}

/// 问卷分析数据
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SurveyAnalytics {
    pub survey_id: i32,
    pub total_responses: i32,
    pub completion_rate: f64,
    pub question_statistics: Vec<QuestionStatistic>,
    pub demographic_breakdown: HashMap<String, HashMap<String, f64>>,
    pub time_distribution: HashMap<String, i32>,
    pub geographic_distribution: HashMap<String, i32>,
    pub response_quality_score: f64,
    pub insights: Vec<String>,
}

/// 问题统计数据
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QuestionStatistic {
    pub question_id: String,
    pub question_text: String,
    pub question_type: QuestionType,
    pub total_responses: i32,
    pub answer_distribution: HashMap<String, f64>,
    pub average_rating: Option<f64>,
}

/// 趋势数据
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TrendData {
    pub date: String,
    pub responses: i32,
    pub completion_rate: f64,
}

/// 问卷统计数据
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SurveyStats {
    pub question_id: String,
    pub question_title: String,
    pub answer_counts: HashMap<String, i32>,
    pub total_answers: i32,
    pub skip_count: i32,
}

/// 问卷列表响应
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SurveyListResponse {
    pub surveys: Vec<Survey>,
    pub total: i32,
    pub page: i32,
    pub page_size: i32,
}

/// 问卷详情响应
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SurveyDetailResponse {
    pub survey: Survey,
    pub questions: Vec<Question>,
    pub response_count: i32,
    pub analytics: Option<SurveyAnalytics>,
}