// 测试删除用户功能的脚本
console.log("开始测试删除用户功能...");

// 检查后端是否运行
fetch("http://127.0.0.1:8000/health")
  .then((response) => response.json())
  .then((data) => {
    console.log("✅ 后端服务器状态:", data);
  })
  .catch((error) => {
    console.error("❌ 后端服务器不可用:", error);
  });

// 检查认证状态
const token = localStorage.getItem("token");
console.log("🔑 Token存在:", !!token);
if (token) {
  console.log("🔑 Token前几位:", token.substring(0, 20) + "...");
}

// 测试获取用户列表
fetch("http://127.0.0.1:8000/api/v1/users?page=1&limit=10&role=user_admin", {
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
})
  .then((response) => {
    console.log("📋 获取用户列表状态码:", response.status);
    return response.json();
  })
  .then((data) => {
    console.log("📋 用户列表数据:", data);

    // 如果有用户，测试删除第一个用户
    if (data.success && data.data && data.data.length > 0) {
      const testUserId = data.data[0].id;
      console.log(`🗑️ 尝试删除用户 ID: ${testUserId}`);

      // 测试删除请求
      fetch(`http://127.0.0.1:8000/api/v1/users/${testUserId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      })
        .then((response) => {
          console.log("🗑️ 删除请求状态码:", response.status);
          return response.json();
        })
        .then((deleteResult) => {
          console.log("🗑️ 删除结果:", deleteResult);
        })
        .catch((error) => {
          console.error("❌ 删除请求失败:", error);
        });
    }
  })
  .catch((error) => {
    console.error("❌ 获取用户列表失败:", error);
  });
