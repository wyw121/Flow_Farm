import {
  CompanyStatistics,
  PaginatedResponse,
  User,
  UserCreate,
  UserUpdate,
  UserWithStats,
} from "../types";
import { apiClient } from "./api";
import {
  adaptApiResponse,
  callApiWithFallback,
  callPaginatedApiWithFallback,
} from "./apiAdapter";

export interface AdminUserUpdateRequest {
  username?: string;
  email?: string;
  phone?: string;
  password?: string;
  full_name?: string;
  company?: string;
  is_active?: boolean;
  max_employees?: number;
  role?: string;
}

export const userService = {
  // 创建用户
  async createUser(userData: UserCreate): Promise<User> {
    const response = await apiClient.post("/api/v1/users", userData);
    return adaptApiResponse<User>(response);
  },

  // 系统管理员更新用户信息（包括密码）
  async adminUpdateUser(
    userId: number,
    userData: AdminUserUpdateRequest
  ): Promise<User> {
    const response = await apiClient.put(`/api/v1/users/${userId}`, userData);
    return response.data;
  },

  // 获取用户列表
  async getUsers(
    page: number = 1,
    size: number = 10,
    role?: string
  ): Promise<PaginatedResponse<UserWithStats>> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: size.toString(), // 使用limit参数（适配Rust后端）
    });
    if (role) {
      params.append("role", role);
    }

    console.log("🌐 API调用详情:", {
      url: `/api/v1/users?${params}`,
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });

    return callPaginatedApiWithFallback<UserWithStats>(
      async () => {
        console.log("🚀 主要API调用开始");
        const response = await apiClient.get(`/api/v1/users?${params}`);
        console.log("✅ 主要API调用响应:", response);
        return response;
      },
      page,
      size,
      async () => {
        console.log("🔄 备用API调用开始");
        // 备用调用：改用limit参数并移除多余斜杠
        const params2 = new URLSearchParams({
          page: page.toString(),
          limit: size.toString(), // 保持使用limit参数
        });
        if (role) {
          params2.append("role", role);
        }
        const response = await apiClient.get(`/api/v1/users?${params2}`);
        console.log("✅ 备用API调用响应:", response);
        return response;
      }
    );
  },

  // 获取用户详情
  async getUser(userId: number): Promise<UserWithStats> {
    return callApiWithFallback<UserWithStats>(() =>
      apiClient.get(`/api/v1/users/${userId}`)
    );
  },

  // 更新用户
  async updateUser(userId: number, userData: UserUpdate): Promise<User> {
    const response = await apiClient.put(`/api/v1/users/${userId}`, userData);
    return response.data;
  },

  // 删除用户
  async deleteUser(userId: number): Promise<void> {
    await apiClient.delete(`/api/v1/users/${userId}`);
  },

  // 获取公司统计信息（系统管理员使用）
  async getCompanyStatistics(): Promise<CompanyStatistics[]> {
    return callApiWithFallback<CompanyStatistics[]>(() =>
      apiClient.get("/api/v1/users/companies/statistics")
    );
  },

  // 切换用户状态
  async toggleUserStatus(userId: number): Promise<User> {
    const response = await apiClient.post(
      `/api/v1/users/${userId}/toggle-status`
    );
    return response.data;
  },

  // 获取公司名称列表（用于下拉选择）
  async getCompanyNames(): Promise<string[]> {
    const response = await apiClient.get("/api/v1/users/companies/names");
    return adaptApiResponse<string[]>(response);
  },
};
