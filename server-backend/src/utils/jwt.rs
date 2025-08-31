use anyhow::{Result, anyhow};
use chrono::{Utc, Duration};
use jsonwebtoken::{encode, decode, Header, Validation, EncodingKey, DecodingKey};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Claims {
    pub sub: String, // 用户ID
    pub role: String, // 用户角色
    pub exp: i64,    // 过期时间
    pub iat: i64,    // 签发时间
}

pub fn create_jwt_token(
    user_id: &str,
    role: &str,  // 改为String引用
    secret: &str,
    expires_in: i64,
) -> Result<String> {
    let now = Utc::now();
    let exp = now + Duration::seconds(expires_in);

    let claims = Claims {
        sub: user_id.to_string(),
        role: role.to_string(),  // 直接转换为String
        exp: exp.timestamp(),
        iat: now.timestamp(),
    };

    let token = encode(
        &Header::default(),
        &claims,
        &EncodingKey::from_secret(secret.as_ref()),
    )?;

    Ok(token)
}

pub fn decode_jwt_token(token: &str, secret: &str) -> Result<Claims> {
    let token_data = decode::<Claims>(
        token,
        &DecodingKey::from_secret(secret.as_ref()),
        &Validation::default(),
    )?;

    Ok(token_data.claims)
}

pub fn verify_jwt_token(token: &str, secret: &str) -> Result<bool> {
    let claims = decode_jwt_token(token, secret)?;
    let now = Utc::now().timestamp();

    if claims.exp < now {
        return Err(anyhow!("Token已过期"));
    }

    Ok(true)
}
