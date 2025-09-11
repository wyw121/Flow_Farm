// API响应适配器 - 处理不同后端的响应格式差异
export interface ApiResponseWrapper<T> {
  success: boolean;
  message?: string;
  data?: T;
}

export function adaptApiResponse<T>(response: any): T {
  // 如果是Rust后端的ApiResponse格式
  if (response.data && typeof response.data.success === "boolean") {
    if (response.data.success) {
      return response.data.data;
    } else {
      // 创建包含原始响应的错误对象
      const error = new Error(response.data.message || "请求失败") as any;
      error.response = response;
      throw error;
    }
  }

  // 如果是Python后端的直接数据格式
  return response.data;
}

export function adaptPaginatedResponse<T>(
  response: any,
  page: number,
  size: number
): {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
} {
  // 如果是Rust后端的ApiResponse格式
  if (response.data && typeof response.data.success === "boolean") {
    console.log('🔍 Rust后端响应格式检测:', response.data)
    if (response.data.success) {
      const items = response.data.data || [];
      return {
        items,
        total: items.length,
        page,
        size,
        pages: Math.ceil(items.length / size),
      };
    } else {
      console.error('❌ 后端返回错误:', response.data)
      throw new Error(response.data.message || "请求失败");
    }
  }

  // 如果是Python后端的分页格式
  if (response.data && Array.isArray(response.data.items)) {
    return response.data;
  }

  // 如果是直接数组格式
  if (Array.isArray(response.data)) {
    return {
      items: response.data,
      total: response.data.length,
      page,
      size,
      pages: Math.ceil(response.data.length / size),
    };
  }

  // 默认空响应
  return {
    items: [],
    total: 0,
    page,
    size,
    pages: 0,
  };
}

// 创建一个通用的API调用函数，具有重试机制
export async function callApiWithFallback<T>(
  primaryCall: () => Promise<any>,
  fallbackCall?: () => Promise<any>
): Promise<T> {
  try {
    const response = await primaryCall();
    return adaptApiResponse<T>(response);
  } catch (error) {
    if (fallbackCall) {
      // 主要API调用失败，尝试备用方案
      const response = await fallbackCall();
      return adaptApiResponse<T>(response);
    }
    throw error;
  }
}

export async function callPaginatedApiWithFallback<T>(
  primaryCall: () => Promise<any>,
  page: number,
  size: number,
  fallbackCall?: () => Promise<any>
): Promise<{
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}> {
  try {
    const response = await primaryCall();
    return adaptPaginatedResponse<T>(response, page, size);
  } catch (error) {
    if (fallbackCall) {
      // 主要API调用失败，尝试备用方案
      const response = await fallbackCall();
      return adaptPaginatedResponse<T>(response, page, size);
    }
    throw error;
  }
}
