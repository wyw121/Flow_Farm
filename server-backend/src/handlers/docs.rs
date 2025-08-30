use axum::{http::StatusCode, response::Html};

pub async fn api_docs() -> Result<Html<String>, StatusCode> {
    let html = r#"
<!DOCTYPE html>
<html>
<head>
    <title>Flow Farm API 文档</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
        .endpoint { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .method { font-weight: bold; padding: 2px 8px; border-radius: 3px; color: white; }
        .get { background-color: #61affe; }
        .post { background-color: #49cc90; }
        .put { background-color: #fca130; }
        .delete { background-color: #f93e3e; }
        code { background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }
    </style>
</head>
<body>
    <h1>Flow Farm API 文档</h1>
    <p>欢迎使用 Flow Farm 服务器后端 API</p>

    <h2>认证接口</h2>
    <div class="endpoint">
        <span class="method post">POST</span>
        <code>/api/v1/auth/login</code>
        <p>用户登录</p>
    </div>

    <div class="endpoint">
        <span class="method post">POST</span>
        <code>/api/v1/auth/register</code>
        <p>用户注册</p>
    </div>

    <div class="endpoint">
        <span class="method get">GET</span>
        <code>/api/v1/auth/me</code>
        <p>获取当前用户信息</p>
    </div>

    <h2>用户管理</h2>
    <div class="endpoint">
        <span class="method get">GET</span>
        <code>/api/v1/users</code>
        <p>获取用户列表</p>
    </div>

    <div class="endpoint">
        <span class="method post">POST</span>
        <code>/api/v1/users</code>
        <p>创建用户</p>
    </div>

    <h2>工作记录</h2>
    <div class="endpoint">
        <span class="method get">GET</span>
        <code>/api/v1/work-records</code>
        <p>获取工作记录</p>
    </div>

    <div class="endpoint">
        <span class="method post">POST</span>
        <code>/api/v1/work-records</code>
        <p>创建工作记录</p>
    </div>

    <h2>设备管理</h2>
    <div class="endpoint">
        <span class="method get">GET</span>
        <code>/api/v1/devices</code>
        <p>获取设备列表</p>
    </div>

    <h2>KPI统计</h2>
    <div class="endpoint">
        <span class="method get">GET</span>
        <code>/api/v1/kpi/stats</code>
        <p>获取KPI统计数据</p>
    </div>

    <p><strong>注意:</strong> 大部分接口需要在请求头中包含 Authorization: Bearer &lt;token&gt;</p>
</body>
</html>
    "#;

    Ok(Html(html.to_string()))
}
