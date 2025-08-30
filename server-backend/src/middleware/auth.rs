use axum::{
    extract::{Request, State},
    middleware::Next,
    response::Response,
    http::{StatusCode, HeaderMap},
};
use axum_extra::{
    headers::{authorization::Bearer, Authorization},
    TypedHeader,
};

use crate::{
    Database, Config,
    models::{UserInfo, UserRole},
    utils::jwt::{decode_jwt_token, Claims},
};

type AppState = (Database, Config);

#[derive(Clone)]
pub struct AuthLayer {
    jwt_secret: String,
}

impl AuthLayer {
    pub fn new(jwt_secret: String) -> Self {
        Self { jwt_secret }
    }

    pub async fn middleware(
        State((database, config)): State<AppState>,
        TypedHeader(authorization): TypedHeader<Authorization<Bearer>>,
        mut request: Request,
        next: Next,
    ) -> Result<Response, StatusCode> {
        let token = authorization.token();

        // 解码JWT token
        let claims = decode_jwt_token(token, &config.jwt_secret)
            .map_err(|_| StatusCode::UNAUTHORIZED)?;

        // 从数据库获取用户信息
        let user = sqlx::query_as::<_, crate::models::User>(
            "SELECT * FROM users WHERE id = ? AND is_active = true"
        )
        .bind(&claims.sub)
        .fetch_optional(&database.pool)
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?
        .ok_or(StatusCode::UNAUTHORIZED)?;

        // 创建认证上下文
        let auth_context = AuthContext {
            user: user.into(),
            claims,
        };

        // 将认证上下文添加到请求扩展中
        request.extensions_mut().insert(auth_context);

        Ok(next.run(request).await)
    }
}

#[derive(Clone, Debug)]
pub struct AuthContext {
    pub user: UserInfo,
    pub claims: Claims,
}

// 实现从请求扩展中提取认证上下文
#[axum::async_trait]
impl<S> axum::extract::FromRequestParts<S> for AuthContext
where
    S: Send + Sync,
{
    type Rejection = StatusCode;

    async fn from_request_parts(
        parts: &mut axum::http::request::Parts,
        _state: &S,
    ) -> Result<Self, Self::Rejection> {
        parts
            .extensions
            .get::<AuthContext>()
            .cloned()
            .ok_or(StatusCode::UNAUTHORIZED)
    }
}
