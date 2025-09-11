// 测试前端登录功能
async function testLogin() {
  const loginData = {
    username: "test_login@example.com",
    password: "123456",
  };

  try {
    console.log("🚀 开始登录测试...");
    console.log("📧 使用邮箱:", loginData.username);

    const response = await fetch("http://127.0.0.1:8000/api/v1/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(loginData),
    });

    console.log("📊 响应状态:", response.status, response.statusText);

    const result = await response.json();
    console.log("📄 响应内容:", result);

    if (result.success) {
      console.log("✅ 登录成功!");
      console.log("🔑 Token:", result.data.token);
      console.log("👤 用户信息:", result.data.user);
    } else {
      console.log("❌ 登录失败:", result.message);
    }
  } catch (error) {
    console.error("💥 网络错误:", error);
  }
}

// 执行测试
testLogin();
