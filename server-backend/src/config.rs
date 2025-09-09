use anyhow::Result;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    pub app_name: String,
    pub version: String,
    pub debug: bool,
    pub host: String,
    pub port: u16,
    pub database_url: String,
    pub jwt_secret: String,
    pub jwt_expires_in: i64,
    pub allowed_origins: Vec<String>,
    pub bcrypt_rounds: u32,
    pub static_dir: String,
    pub enable_tls: bool,
    pub tls_cert_path: Option<String>,
    pub tls_key_path: Option<String>,
}

impl Config {
    pub fn new() -> Result<Self> {
        let config = Self {
            app_name: std::env::var("APP_NAME")
                .unwrap_or_else(|_| "Flow Farm 服务器后端".to_string()),
            version: std::env::var("VERSION").unwrap_or_else(|_| "1.0.0".to_string()),
            debug: std::env::var("DEBUG")
                .unwrap_or_else(|_| "true".to_string())
                .parse()
                .unwrap_or(true),
            host: std::env::var("HOST").unwrap_or_else(|_| "0.0.0.0".to_string()),
            port: std::env::var("PORT")
                .unwrap_or_else(|_| "8000".to_string())
                .parse()
                .unwrap_or(8000),
            database_url: std::env::var("DATABASE_URL")
                .unwrap_or_else(|_| "sqlite:data/flow_farm.db".to_string()),
            jwt_secret: std::env::var("JWT_SECRET")
                .unwrap_or_else(|_| "your-secret-key-change-this-in-production".to_string()),
            jwt_expires_in: std::env::var("JWT_EXPIRES_IN")
                .unwrap_or_else(|_| "86400".to_string()) // 24小时
                .parse()
                .unwrap_or(86400),
            allowed_origins: std::env::var("ALLOWED_ORIGINS")
                .unwrap_or_else(|_| "*".to_string())
                .split(',')
                .map(|s| s.trim().to_string())
                .collect(),
            bcrypt_rounds: std::env::var("BCRYPT_ROUNDS")
                .unwrap_or_else(|_| "12".to_string())
                .parse()
                .unwrap_or(12),
            static_dir: std::env::var("STATIC_DIR")
                .unwrap_or_else(|_| "../server-frontend/dist".to_string()),
            enable_tls: std::env::var("ENABLE_TLS")
                .unwrap_or_else(|_| "false".to_string())
                .parse()
                .unwrap_or(false),
            tls_cert_path: std::env::var("TLS_CERT_PATH").ok(),
            tls_key_path: std::env::var("TLS_KEY_PATH").ok(),
        };

        Ok(config)
    }
}
