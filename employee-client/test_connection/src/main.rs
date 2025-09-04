use reqwest;
use serde::{Deserialize, Serialize};

#[derive(Serialize)]
struct LoginRequest {
    username: String,
    password: String,
}

#[derive(Deserialize, Debug)]
struct LoginResponse {
    token: String,
    user: UserInfo,
}

#[derive(Deserialize, Debug)]
struct UserInfo {
    id: i32,
    username: String,
    email: Option<String>,
    full_name: Option<String>,
    phone: Option<String>,
    company: Option<String>,
    role: String,
    is_active: bool,
    is_verified: bool,
    current_employees: i32,
    max_employees: i32,
    parent_id: Option<i32>,
    created_at: String,
    last_login: Option<String>,
}

#[derive(Deserialize, Debug)]
struct ApiResponse<T> {
    success: bool,
    message: String,
    data: Option<T>,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🚀 测试客户端与服务器后端的连接");
    
    let client = reqwest::Client::new();
    
    // 测试登录
    let login_request = LoginRequest {
        username: "client_test".to_string(),
        password: "test123".to_string(),
    };
    
    let response = client
        .post("http://localhost:8000/api/v1/auth/login")
        .header("Content-Type", "application/json")
        .json(&login_request)
        .send()
        .await?;
    
    let status = response.status();
    println!("📡 服务器响应状态: {}", status);
    
    if status.is_success() {
        let api_response: ApiResponse<LoginResponse> = response.json().await?;
        
        if api_response.success {
            println!("✅ 登录成功!");
            if let Some(login_data) = api_response.data {
                println!("👤 用户信息:");
                println!("   ID: {}", login_data.user.id);
                println!("   用户名: {}", login_data.user.username);
                println!("   角色: {}", login_data.user.role);
                println!("   邮箱: {:?}", login_data.user.email);
                println!("   全名: {:?}", login_data.user.full_name);
                println!("   公司: {:?}", login_data.user.company);
                println!("🔑 Token: {}", &login_data.token[0..50.min(login_data.token.len())]); // 只显示前50字符
                
                // 测试用token获取当前用户信息
                println!("\n🔍 测试获取当前用户信息:");
                let auth_response = client
                    .get("http://localhost:8000/api/v1/auth/me")
                    .header("Authorization", format!("Bearer {}", login_data.token))
                    .send()
                    .await?;
                
                if auth_response.status().is_success() {
                    let user_response: ApiResponse<UserInfo> = auth_response.json().await?;
                    if user_response.success {
                        println!("✅ 成功获取用户信息");
                        if let Some(user) = user_response.data {
                            println!("   验证用户名: {}", user.username);
                        }
                    } else {
                        println!("❌ 获取用户信息失败: {}", user_response.message);
                    }
                } else {
                    println!("❌ 获取用户信息请求失败: {}", auth_response.status());
                }
            }
        } else {
            println!("❌ 登录失败: {}", api_response.message);
        }
    } else {
        let error_text = response.text().await?;
        println!("❌ 服务器错误: {}", error_text);
    }
    
    println!("\n🎉 测试完成！客户端可以成功连接到服务器后端数据库。");
    
    Ok(())
}
