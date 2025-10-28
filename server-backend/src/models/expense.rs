use chrono::{DateTime, NaiveDate, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;

/// 费用记录主表
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct ExpenseRecord {
    pub id: i32,
    pub visit_id: Option<i32>,        // 关联拜访记录
    pub employee_id: i32,             // 提交员工ID
    pub expense_category_id: i32,     // 费用类别ID
    pub amount: f64,                  // 费用金额
    pub currency: String,             // 货币类型 (CNY, USD等)
    pub receipt_path: Option<String>, // 发票文件路径
    pub invoice_number: Option<String>, // 发票号码
    pub vendor_name: Option<String>,  // 商家名称
    pub description: String,          // 费用描述
    pub expense_date: NaiveDate,      // 费用发生日期
    pub location: Option<String>,     // 费用发生地点
    pub status: ExpenseStatus,        // 审批状态
    pub submitted_at: Option<DateTime<Utc>>, // 提交时间
    pub approved_by: Option<i32>,     // 审批人ID
    pub approved_at: Option<DateTime<Utc>>, // 审批时间
    pub rejection_reason: Option<String>, // 拒绝原因
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// 费用状态枚举
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, sqlx::Type)]
#[sqlx(type_name = "expense_status", rename_all = "lowercase")]
pub enum ExpenseStatus {
    Draft,      // 草稿
    Submitted,  // 已提交
    Approved,   // 已批准
    Rejected,   // 已拒绝
    Paid,       // 已支付
}

impl std::fmt::Display for ExpenseStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ExpenseStatus::Draft => write!(f, "draft"),
            ExpenseStatus::Submitted => write!(f, "submitted"),
            ExpenseStatus::Approved => write!(f, "approved"),
            ExpenseStatus::Rejected => write!(f, "rejected"),
            ExpenseStatus::Paid => write!(f, "paid"),
        }
    }
}

/// 费用类别
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct ExpenseCategory {
    pub id: i32,
    pub name: String,              // 类别名称 (交通费、餐费、住宿费等)
    pub code: String,              // 类别代码 (TRANSPORT, MEAL, ACCOMMODATION等)
    pub description: Option<String>, // 类别描述
    pub max_amount: Option<f64>,   // 单次最大金额限制
    pub requires_receipt: bool,    // 是否必须提供发票
    pub is_active: bool,           // 是否启用
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// 发票信息 (OCR识别结果)
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct InvoiceInfo {
    pub id: i32,
    pub expense_id: i32,           // 关联费用记录
    pub invoice_number: String,    // 发票号码
    pub invoice_code: Option<String>, // 发票代码
    pub total_amount: f64,         // 发票总金额
    pub tax_amount: Option<f64>,   // 税额
    pub invoice_date: NaiveDate,   // 发票日期
    pub seller_name: String,       // 销售方名称
    pub seller_tax_id: Option<String>, // 销售方税号
    pub buyer_name: Option<String>, // 购买方名称
    pub buyer_tax_id: Option<String>, // 购买方税号
    pub ocr_confidence: f64,       // OCR识别置信度
    pub validation_status: InvoiceValidationStatus, // 验证状态
    pub validation_message: Option<String>, // 验证消息
    pub raw_ocr_data: Option<String>, // 原始OCR数据 (JSON)
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// 发票验证状态
#[derive(Debug, Clone, Serialize, Deserialize, sqlx::Type)]
#[sqlx(type_name = "invoice_validation_status", rename_all = "lowercase")]
pub enum InvoiceValidationStatus {
    Pending,    // 待验证
    Valid,      // 有效
    Invalid,    // 无效
    Error,      // 验证错误
}

/// 创建费用记录请求
#[derive(Debug, Deserialize)]
pub struct CreateExpenseRequest {
    pub visit_id: Option<i32>,
    pub expense_category_id: i32,
    pub amount: f64,
    pub currency: String,
    pub description: String,
    pub expense_date: NaiveDate,
    pub location: Option<String>,
    pub vendor_name: Option<String>,
}

/// 更新费用记录请求
#[derive(Debug, Deserialize)]
pub struct UpdateExpenseRequest {
    pub expense_category_id: Option<i32>,
    pub amount: Option<f64>,
    pub currency: Option<String>,
    pub description: Option<String>,
    pub expense_date: Option<NaiveDate>,
    pub location: Option<String>,
    pub vendor_name: Option<String>,
}

/// 提交费用审批请求
#[derive(Debug, Deserialize)]
pub struct SubmitExpenseRequest {
    pub expense_ids: Vec<i32>,  // 支持批量提交
}

/// 审批费用请求
#[derive(Debug, Deserialize)]
pub struct ApproveExpenseRequest {
    pub expense_ids: Vec<i32>,
    pub action: ApprovalAction,
    pub comment: Option<String>,
}

/// 审批操作枚举
#[derive(Debug, Deserialize)]
pub enum ApprovalAction {
    Approve,
    Reject,
}

/// 费用统计信息
#[derive(Debug, Serialize)]
pub struct ExpenseStatistics {
    pub total_amount: f64,
    pub pending_amount: f64,
    pub approved_amount: f64,
    pub rejected_amount: f64,
    pub total_count: i32,
    pub pending_count: i32,
    pub approved_count: i32,
    pub rejected_count: i32,
    pub by_category: Vec<CategoryExpense>,
    pub by_month: Vec<MonthlyExpense>,
}

/// 按类别统计
#[derive(Debug, Serialize)]
pub struct CategoryExpense {
    pub category_name: String,
    pub total_amount: f64,
    pub count: i32,
}

/// 按月份统计
#[derive(Debug, Serialize)]
pub struct MonthlyExpense {
    pub year: i32,
    pub month: i32,
    pub total_amount: f64,
    pub count: i32,
}

/// 费用列表查询参数
#[derive(Debug, Deserialize)]
pub struct ExpenseListQuery {
    pub employee_id: Option<i32>,
    pub status: Option<ExpenseStatus>,
    pub category_id: Option<i32>,
    pub start_date: Option<NaiveDate>,
    pub end_date: Option<NaiveDate>,
    pub min_amount: Option<f64>,
    pub max_amount: Option<f64>,
    pub page: Option<u32>,
    pub limit: Option<u32>,
}

/// 费用详情响应
#[derive(Debug, Serialize)]
pub struct ExpenseDetailResponse {
    pub expense: ExpenseRecord,
    pub category: ExpenseCategory,
    pub invoice_info: Option<InvoiceInfo>,
    pub employee_name: String,
    pub approver_name: Option<String>,
    pub visit_info: Option<VisitBasicInfo>,
}

/// 拜访基础信息
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct VisitBasicInfo {
    pub id: i32,
    pub customer_name: String,
    pub planned_start_time: Option<DateTime<Utc>>,
    pub actual_start_time: Option<DateTime<Utc>>,
}

/// OCR识别请求
#[derive(Debug, Deserialize)]
pub struct OCRRequest {
    pub image_data: String, // Base64编码的图片数据
    pub provider: OCRProvider,
}

/// OCR服务提供商
#[derive(Debug, Deserialize)]
pub enum OCRProvider {
    Baidu,
    Tencent,
    Xfyun,  // 讯飞
}

/// OCR识别结果
#[derive(Debug, Serialize)]
pub struct OCRResult {
    pub invoice_number: Option<String>,
    pub total_amount: Option<f64>,
    pub invoice_date: Option<NaiveDate>,
    pub seller_name: Option<String>,
    pub confidence: f64,
    pub raw_data: serde_json::Value,
}

/// 发票验证请求
#[derive(Debug, Deserialize)]
pub struct InvoiceValidationRequest {
    pub invoice_number: String,
    pub invoice_code: Option<String>,
    pub total_amount: f64,
    pub invoice_date: NaiveDate,
}

/// 发票验证结果
#[derive(Debug, Serialize)]
pub struct InvoiceValidationResult {
    pub is_valid: bool,
    pub status: InvoiceValidationStatus,
    pub message: String,
    pub details: Option<serde_json::Value>,
}

/// 费用报表数据
#[derive(Debug, Serialize)]
pub struct ExpenseReport {
    pub title: String,
    pub generated_at: DateTime<Utc>,
    pub period: ReportPeriod,
    pub summary: ExpenseStatistics,
    pub details: Vec<ExpenseReportItem>,
}

/// 报表周期
#[derive(Debug, Serialize, Deserialize)]
pub enum ReportPeriod {
    Daily { date: NaiveDate },
    Weekly { year: i32, week: u32 },
    Monthly { year: i32, month: u32 },
    Quarterly { year: i32, quarter: u32 },
    Yearly { year: i32 },
    Custom { start_date: NaiveDate, end_date: NaiveDate },
}

/// 费用报表项目
#[derive(Debug, Serialize)]
pub struct ExpenseReportItem {
    pub expense: ExpenseRecord,
    pub category_name: String,
    pub employee_name: String,
    pub approver_name: Option<String>,
}

impl Default for ExpenseCategory {
    fn default() -> Self {
        Self {
            id: 0,
            name: String::new(),
            code: String::new(),
            description: None,
            max_amount: None,
            requires_receipt: true,
            is_active: true,
            created_at: Utc::now(),
            updated_at: Utc::now(),
        }
    }
}

impl ExpenseCategory {
    /// 创建预设的费用类别
    pub fn create_default_categories() -> Vec<CreateExpenseCategoryRequest> {
        vec![
            CreateExpenseCategoryRequest {
                name: "交通费".to_string(),
                code: "TRANSPORT".to_string(),
                description: Some("出租车、地铁、公交、火车、飞机等交通费用".to_string()),
                max_amount: Some(1000.0),
                requires_receipt: true,
            },
            CreateExpenseCategoryRequest {
                name: "餐饮费".to_string(),
                code: "MEAL".to_string(),
                description: Some("工作餐、商务宴请等餐饮费用".to_string()),
                max_amount: Some(500.0),
                requires_receipt: true,
            },
            CreateExpenseCategoryRequest {
                name: "住宿费".to_string(),
                code: "ACCOMMODATION".to_string(),
                description: Some("酒店、民宿等住宿费用".to_string()),
                max_amount: Some(800.0),
                requires_receipt: true,
            },
            CreateExpenseCategoryRequest {
                name: "通讯费".to_string(),
                code: "COMMUNICATION".to_string(),
                description: Some("电话费、网络费等通讯费用".to_string()),
                max_amount: Some(200.0),
                requires_receipt: false,
            },
            CreateExpenseCategoryRequest {
                name: "办公用品".to_string(),
                code: "OFFICE_SUPPLIES".to_string(),
                description: Some("文具、打印、复印等办公用品费用".to_string()),
                max_amount: Some(300.0),
                requires_receipt: true,
            },
            CreateExpenseCategoryRequest {
                name: "其他费用".to_string(),
                code: "OTHER".to_string(),
                description: Some("其他工作相关费用".to_string()),
                max_amount: None,
                requires_receipt: true,
            },
        ]
    }
}

/// 创建费用类别请求
#[derive(Debug, Deserialize)]
pub struct CreateExpenseCategoryRequest {
    pub name: String,
    pub code: String,
    pub description: Option<String>,
    pub max_amount: Option<f64>,
    pub requires_receipt: bool,
}

/// 费用审批历史
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct ExpenseApprovalHistory {
    pub id: i32,
    pub expense_id: i32,
    pub action: String,  // submitted, approved, rejected, paid
    pub actor_id: i32,   // 操作人ID
    pub comment: Option<String>,
    pub previous_status: String,
    pub new_status: String,
    pub created_at: DateTime<Utc>,
}