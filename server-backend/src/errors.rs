use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("数据库错误: {0}")]
    Database(#[from] sqlx::Error),

    #[error("认证错误: {0}")]
    Auth(String),

    #[error("权限不足")]
    Forbidden,

    #[error("资源未找到: {0}")]
    NotFound(String),

    #[error("验证错误: {0}")]
    Validation(String),

    #[error("内部服务器错误: {0}")]
    Internal(#[from] anyhow::Error),
}
