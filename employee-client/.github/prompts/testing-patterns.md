# Testing and Validation Prompts

## Unit Testing Patterns

### Rust Backend Testing
```prompt
创建 Rust 单元测试，遵循以下模式：
```rust
#[cfg(test)]
mod tests {
    use super::*;
    use tokio_test;

    #[tokio::test]
    async fn test_device_connection() {
        // Arrange
        let device_manager = DeviceManager::new();
        let device_id = 1;

        // Act
        let result = device_manager.connect_device(device_id).await;

        // Assert
        assert!(result.is_ok());
        assert!(device_manager.is_connected(device_id));
    }

    #[test]
    fn test_task_distribution() {
        // 测试任务分配算法
        let connected_devices = vec![1, 2, 3];
        let total_tasks = 100;

        let distribution = distribute_tasks(total_tasks, &connected_devices);

        assert_eq!(distribution.len(), connected_devices.len());
        assert_eq!(distribution.values().sum::<usize>(), total_tasks);
    }
}
```

要求：
1. 每个模块都要有对应的测试
2. 异步函数使用 tokio::test
3. 包含正常和异常情况测试
4. Mock 外部依赖（数据库、API）
```

### Tauri Command Testing
```prompt
测试 Tauri 命令功能：
```rust
#[cfg(test)]
mod command_tests {
    use super::*;

    #[tokio::test]
    async fn test_get_devices_command() {
        let result = get_devices().await;
        assert!(result.is_ok());

        let devices = result.unwrap();
        assert!(devices.len() <= 10); // 最多10台设备
    }

    #[tokio::test]
    async fn test_upload_contacts_command() {
        let file_path = "test_contacts.csv";
        let result = upload_contacts_file(file_path.to_string()).await;

        match result {
            Ok(count) => assert!(count > 0),
            Err(e) => panic!("Upload failed: {}", e),
        }
    }
}
```
```

## Integration Testing

### API Communication Testing
```prompt
测试与服务器的 API 通信：
```rust
#[cfg(test)]
mod integration_tests {
    use super::*;
    use wiremock::{MockServer, Mock, ResponseTemplate};
    use wiremock::matchers::{method, path};

    #[tokio::test]
    async fn test_balance_check_api() {
        // 设置 Mock 服务器
        let mock_server = MockServer::start().await;

        Mock::given(method("GET"))
            .and(path("/api/balance"))
            .respond_with(ResponseTemplate::new(200)
                .set_body_json(json!({
                    "balance": 100.0,
                    "currency": "CNY"
                })))
            .mount(&mock_server)
            .await;

        // 测试 API 调用
        let api_client = ApiClient::new(&mock_server.uri());
        let balance = api_client.get_balance("user123").await;

        assert!(balance.is_ok());
        assert_eq!(balance.unwrap(), 100.0);
    }
}
```
```

## UI Testing Patterns

### Frontend JavaScript Testing
```prompt
创建前端交互测试：
```javascript
// 测试设备连接 UI
async function testDeviceConnectionUI() {
    const deviceList = document.getElementById('device-list');
    const connectButton = document.querySelector('[data-device="1"] .connect-btn');

    // 模拟点击连接
    connectButton.click();

    // 等待状态更新
    await new Promise(resolve => setTimeout(resolve, 100));

    // 验证 UI 状态
    const statusIndicator = document.querySelector('[data-device="1"] .status');
    assert(statusIndicator.classList.contains('connected'), 'Device should show as connected');
}

// 测试文件上传
async function testFileUpload() {
    const fileInput = document.getElementById('file-input');
    const uploadButton = document.getElementById('upload-btn');

    // 创建测试文件
    const testFile = new File(['name,phone\nJohn,123456'], 'test.csv', { type: 'text/csv' });

    // 设置文件输入
    Object.defineProperty(fileInput, 'files', {
        value: [testFile],
        writable: false,
    });

    // 触发上传
    uploadButton.click();

    // 验证上传结果
    // 检查进度显示、成功消息等
}
```
```

## Performance Testing

### Load Testing Patterns
```prompt
创建性能测试：
```rust
#[cfg(test)]
mod performance_tests {
    use super::*;
    use std::time::Instant;

    #[tokio::test]
    async fn test_bulk_task_processing() {
        let start = Instant::now();

        // 创建大量任务
        let tasks: Vec<FollowTask> = (0..1000).map(|i|
            FollowTask {
                user_id: format!("user_{}", i),
                platform: Platform::Xiaohongshu,
                // ...
            }
        ).collect();

        // 处理任务
        let results = process_tasks_batch(tasks).await;

        let duration = start.elapsed();

        // 性能断言
        assert!(duration.as_secs() < 30, "Batch processing took too long");
        assert!(results.len() == 1000, "Not all tasks were processed");

        let success_rate = results.iter().filter(|r| r.is_ok()).count() as f64 / results.len() as f64;
        assert!(success_rate > 0.9, "Success rate too low");
    }

    #[test]
    fn test_memory_usage() {
        // 测试内存使用是否在合理范围内
        let initial_memory = get_memory_usage();

        // 执行操作
        let _large_data = create_large_dataset();

        let final_memory = get_memory_usage();
        let memory_increase = final_memory - initial_memory;

        assert!(memory_increase < 100_000_000, "Memory usage increased too much"); // 100MB
    }
}
```
```

## Error Handling Testing

### Error Scenarios
```prompt
测试错误处理场景：
```rust
#[cfg(test)]
mod error_tests {
    use super::*;

    #[tokio::test]
    async fn test_device_disconnect_during_task() {
        let mut device_manager = DeviceManager::new();
        device_manager.connect_device(1).await.unwrap();

        // 开始任务
        let task_handle = tokio::spawn(async move {
            device_manager.execute_task(1, create_test_task()).await
        });

        // 模拟设备断开
        tokio::time::sleep(Duration::from_millis(100)).await;
        disconnect_device(1).await;

        // 验证错误处理
        let result = task_handle.await.unwrap();
        assert!(result.is_err());
        assert!(matches!(result.unwrap_err(), AppError::DeviceDisconnected(_)));
    }

    #[tokio::test]
    async fn test_insufficient_balance_error() {
        let api_client = create_test_api_client();

        // 模拟余额不足
        mock_balance_response(0.0).await;

        let result = api_client.start_follow_task(create_large_task()).await;

        assert!(result.is_err());
        assert!(matches!(result.unwrap_err(), AppError::InsufficientBalance(_)));
    }
}
```
```
