use axum::{body::Body, extract::Request, http::StatusCode, response::Response};
use std::path::Path;
use tower::Service;
use tower_http::services::ServeDir;

/// 自定义静态文件处理器
/// 提供更好的缓存控制和SPA路由支持
pub struct StaticFileHandler {
    serve_dir: ServeDir,
    spa_mode: bool,
}

impl StaticFileHandler {
    pub fn new<P: AsRef<Path>>(assets_dir: P) -> Self {
        let serve_dir = ServeDir::new(assets_dir)
            .precompressed_gzip()
            .precompressed_br()
            .append_index_html_on_directories(true);

        Self {
            serve_dir,
            spa_mode: true,
        }
    }

    pub fn with_spa_mode(mut self, spa_mode: bool) -> Self {
        self.spa_mode = spa_mode;
        self
    }
}

impl tower::Service<Request> for StaticFileHandler {
    type Response = Response;
    type Error = std::convert::Infallible;
    type Future = std::pin::Pin<
        Box<dyn std::future::Future<Output = Result<Self::Response, Self::Error>> + Send>,
    >;

    fn poll_ready(
        &mut self,
        cx: &mut std::task::Context<'_>,
    ) -> std::task::Poll<Result<(), Self::Error>> {
        Service::<Request>::poll_ready(&mut self.serve_dir, cx).map_err(|_| unreachable!())
    }

    fn call(&mut self, req: Request) -> Self::Future {
        let mut serve_dir = self.serve_dir.clone();
        let spa_mode = self.spa_mode;

        Box::pin(async move {
            let uri = req.uri().clone();
            let path = uri.path();

            // 如果是API路径，返回404
            if path.starts_with("/api") {
                return Ok(not_found_response());
            }

            // 尝试提供静态文件
            match Service::<Request>::call(&mut serve_dir, req).await {
                Ok(response) => {
                    let status = response.status();

                    if status == StatusCode::NOT_FOUND && spa_mode {
                        // SPA模式：返回index.html用于客户端路由
                        return Ok(serve_index_html().await);
                    }

                    // 添加缓存头并转换响应体
                    Ok(add_cache_headers_and_convert(response, path))
                }
                Err(_) => {
                    if spa_mode {
                        Ok(serve_index_html().await)
                    } else {
                        Ok(not_found_response())
                    }
                }
            }
        })
    }
}

/// 服务index.html文件 (SPA路由支持)
async fn serve_index_html() -> Response {
    let index_path = "../server-frontend/dist/index.html";

    match tokio::fs::read_to_string(index_path).await {
        Ok(content) => Response::builder()
            .status(StatusCode::OK)
            .header("content-type", "text/html; charset=utf-8")
            .header("cache-control", "no-cache, no-store, must-revalidate")
            .body(Body::from(content))
            .unwrap(),
        Err(_) => {
            tracing::error!("无法读取 index.html 文件");
            Response::builder()
                .status(StatusCode::NOT_FOUND)
                .header("content-type", "text/html; charset=utf-8")
                .body(Body::from(include_str!("../templates/fallback.html")))
                .unwrap()
        }
    }
}

/// 返回404响应
fn not_found_response() -> Response {
    Response::builder()
        .status(StatusCode::NOT_FOUND)
        .header("content-type", "text/html; charset=utf-8")
        .body(Body::from(include_str!("../templates/404.html")))
        .unwrap()
}

/// 根据文件类型添加缓存头并转换响应体类型
fn add_cache_headers_and_convert<B>(mut response: Response<B>, path: &str) -> Response
where
    B: Into<Body>,
{
    let headers = response.headers_mut();

    // 不同类型文件的缓存策略
    let cache_control = if path.ends_with(".html") {
        // HTML文件不缓存，确保更新及时
        "no-cache, no-store, must-revalidate"
    } else if path.contains(".")
        && (path.ends_with(".js")
            || path.ends_with(".css")
            || path.ends_with(".woff")
            || path.ends_with(".woff2"))
    {
        // 静态资源长期缓存 (1年)
        "public, max-age=31536000, immutable"
    } else if path.ends_with(".json") {
        // JSON文件短期缓存 (1小时)
        "public, max-age=3600"
    } else {
        // 其他文件中期缓存 (1天)
        "public, max-age=86400"
    };

    headers.insert(
        "cache-control",
        axum::http::HeaderValue::from_static(cache_control),
    );

    // 安全头
    headers.insert(
        "x-content-type-options",
        axum::http::HeaderValue::from_static("nosniff"),
    );

    headers.insert(
        "x-frame-options",
        axum::http::HeaderValue::from_static("DENY"),
    );

    // 转换响应体类型
    let (parts, body) = response.into_parts();
    Response::from_parts(parts, body.into())
}

impl Clone for StaticFileHandler {
    fn clone(&self) -> Self {
        Self {
            serve_dir: self.serve_dir.clone(),
            spa_mode: self.spa_mode,
        }
    }
}
