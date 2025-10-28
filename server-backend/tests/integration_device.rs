// API集成测试 - Device Management
// 测试设备的CRUD操作和状态管理

mod test_helpers;

use flow_farm_backend::models::{CreateDeviceRequest, Device};
use sqlx::SqlitePool;

#[cfg(test)]
mod device_integration_tests {
    use super::*;
    use test_helpers::*;

    async fn insert_test_device(
        pool: &SqlitePool,
        id: &str,
        device_name: &str,
        user_id: &str,
        status: &str,
    ) -> Result<(), sqlx::Error> {
        let now = chrono::Utc::now().format("%Y-%m-%d %H:%M:%S").to_string();

        sqlx::query(
            r#"
            INSERT INTO devices (
                id, device_name, device_type, adb_id, status, user_id,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            "#,
        )
        .bind(id)
        .bind(device_name)
        .bind("android")
        .bind(format!("adb-{}", id))
        .bind(status)
        .bind(user_id)
        .bind(&now)
        .bind(&now)
        .execute(pool)
        .await?;

        Ok(())
    }

    #[tokio::test]
    async fn test_device_list_by_user() {
        let database = create_test_database().await;

        // 创建测试用户
        let password_hash = bcrypt::hash("password123", bcrypt::DEFAULT_COST).unwrap();
        insert_test_user(&database.pool, "user-1", "testuser", &password_hash, "employee")
            .await
            .unwrap();

        // 插入测试设备
        insert_test_device(&database.pool, "device-1", "Device 1", "user-1", "connected")
            .await
            .unwrap();
        insert_test_device(&database.pool, "device-2", "Device 2", "user-1", "disconnected")
            .await
            .unwrap();
        insert_test_device(&database.pool, "device-3", "Device 3", "user-1", "connected")
            .await
            .unwrap();

        // 查询用户的设备列表
        let devices: Vec<Device> = sqlx::query_as(
            "SELECT * FROM devices WHERE user_id = ? ORDER BY created_at DESC",
        )
        .bind("user-1")
        .fetch_all(&database.pool)
        .await
        .unwrap();

        assert_eq!(devices.len(), 3, "用户应该有3个设备");
        assert_eq!(devices[0].device_name, "Device 3", "第一个设备应该是Device 3");
    }

    #[tokio::test]
    async fn test_device_status_filter() {
        let database = create_test_database().await;

        // 创建测试用户
        let password_hash = bcrypt::hash("password123", bcrypt::DEFAULT_COST).unwrap();
        insert_test_user(&database.pool, "user-1", "testuser", &password_hash, "employee")
            .await
            .unwrap();

        // 插入不同状态的设备
        insert_test_device(&database.pool, "device-1", "Device 1", "user-1", "connected")
            .await
            .unwrap();
        insert_test_device(&database.pool, "device-2", "Device 2", "user-1", "disconnected")
            .await
            .unwrap();
        insert_test_device(&database.pool, "device-3", "Device 3", "user-1", "connected")
            .await
            .unwrap();

        // 查询已连接的设备
        let connected_devices: Vec<Device> = sqlx::query_as(
            "SELECT * FROM devices WHERE user_id = ? AND status = ?",
        )
        .bind("user-1")
        .bind("connected")
        .fetch_all(&database.pool)
        .await
        .unwrap();

        assert_eq!(connected_devices.len(), 2, "应该有2个已连接的设备");

        // 查询未连接的设备
        let disconnected_devices: Vec<Device> = sqlx::query_as(
            "SELECT * FROM devices WHERE user_id = ? AND status = ?",
        )
        .bind("user-1")
        .bind("disconnected")
        .fetch_all(&database.pool)
        .await
        .unwrap();

        assert_eq!(disconnected_devices.len(), 1, "应该有1个未连接的设备");
    }

    #[tokio::test]
    async fn test_device_limit_per_user() {
        let database = create_test_database().await;

        // 创建测试用户（max_employees设置为10，代表最多10个设备）
        let password_hash = bcrypt::hash("password123", bcrypt::DEFAULT_COST).unwrap();
        insert_test_user(&database.pool, "user-1", "testuser", &password_hash, "employee")
            .await
            .unwrap();

        // 插入10个设备
        for i in 1..=10 {
            insert_test_device(
                &database.pool,
                &format!("device-{}", i),
                &format!("Device {}", i),
                "user-1",
                "connected",
            )
            .await
            .unwrap();
        }

        // 查询设备数量
        let count: (i64,) = sqlx::query_as("SELECT COUNT(*) FROM devices WHERE user_id = ?")
            .bind("user-1")
            .fetch_one(&database.pool)
            .await
            .unwrap();

        assert_eq!(count.0, 10, "用户应该有10个设备");

        // 尝试插入第11个设备应该被业务逻辑拒绝（在Service层实现）
        // 这里只验证数据库层面可以插入
        let result = insert_test_device(&database.pool, "device-11", "Device 11", "user-1", "connected")
            .await;

        assert!(result.is_ok(), "数据库层面允许插入第11个设备");
    }

    #[tokio::test]
    async fn test_device_update_status() {
        let database = create_test_database().await;

        // 创建测试用户和设备
        let password_hash = bcrypt::hash("password123", bcrypt::DEFAULT_COST).unwrap();
        insert_test_user(&database.pool, "user-1", "testuser", &password_hash, "employee")
            .await
            .unwrap();

        insert_test_device(&database.pool, "device-1", "Device 1", "user-1", "disconnected")
            .await
            .unwrap();

        // 更新设备状态
        let now = chrono::Utc::now().format("%Y-%m-%d %H:%M:%S").to_string();
        sqlx::query("UPDATE devices SET status = ?, updated_at = ? WHERE id = ?")
            .bind("connected")
            .bind(&now)
            .bind("device-1")
            .execute(&database.pool)
            .await
            .unwrap();

        // 验证状态已更新
        let device: Device = sqlx::query_as("SELECT * FROM devices WHERE id = ?")
            .bind("device-1")
            .fetch_one(&database.pool)
            .await
            .unwrap();

        assert_eq!(device.status, "connected", "设备状态应该已更新为connected");
    }

    #[tokio::test]
    async fn test_device_delete() {
        let database = create_test_database().await;

        // 创建测试用户和设备
        let password_hash = bcrypt::hash("password123", bcrypt::DEFAULT_COST).unwrap();
        insert_test_user(&database.pool, "user-1", "testuser", &password_hash, "employee")
            .await
            .unwrap();

        insert_test_device(&database.pool, "device-1", "Device 1", "user-1", "connected")
            .await
            .unwrap();

        // 删除设备
        sqlx::query("DELETE FROM devices WHERE id = ?")
            .bind("device-1")
            .execute(&database.pool)
            .await
            .unwrap();

        // 验证设备已删除
        let result: Option<Device> = sqlx::query_as("SELECT * FROM devices WHERE id = ?")
            .bind("device-1")
            .fetch_optional(&database.pool)
            .await
            .unwrap();

        assert!(result.is_none(), "设备应该已被删除");
    }

    #[tokio::test]
    async fn test_device_adb_id_format() {
        let database = create_test_database().await;

        // 创建测试用户
        let password_hash = bcrypt::hash("password123", bcrypt::DEFAULT_COST).unwrap();
        insert_test_user(&database.pool, "user-1", "testuser", &password_hash, "employee")
            .await
            .unwrap();

        // 测试不同格式的ADB ID
        let adb_id_formats = vec![
            "192.168.1.100:5555",
            "emulator-5554",
            "device-serial-number",
            "adb-test-123",
        ];

        for (i, adb_id) in adb_id_formats.iter().enumerate() {
            let device_id = format!("device-{}", i + 1);
            let now = chrono::Utc::now().format("%Y-%m-%d %H:%M:%S").to_string();

            sqlx::query(
                r#"
                INSERT INTO devices (
                    id, device_name, device_type, adb_id, status, user_id,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                "#,
            )
            .bind(&device_id)
            .bind(format!("Device {}", i + 1))
            .bind("android")
            .bind(adb_id)
            .bind("connected")
            .bind("user-1")
            .bind(&now)
            .bind(&now)
            .execute(&database.pool)
            .await
            .unwrap();

            // 验证ADB ID已保存
            let device: Device = sqlx::query_as("SELECT * FROM devices WHERE id = ?")
                .bind(&device_id)
                .fetch_one(&database.pool)
                .await
                .unwrap();

            assert_eq!(device.adb_id.as_deref(), Some(*adb_id), "ADB ID应该匹配");
        }
    }

    #[tokio::test]
    async fn test_device_type_validation() {
        let database = create_test_database().await;

        // 创建测试用户
        let password_hash = bcrypt::hash("password123", bcrypt::DEFAULT_COST).unwrap();
        insert_test_user(&database.pool, "user-1", "testuser", &password_hash, "employee")
            .await
            .unwrap();

        // 测试支持的设备类型
        let device_types = vec!["android", "ios", "emulator"];

        for (i, device_type) in device_types.iter().enumerate() {
            let device_id = format!("device-{}", i + 1);
            let now = chrono::Utc::now().format("%Y-%m-%d %H:%M:%S").to_string();

            sqlx::query(
                r#"
                INSERT INTO devices (
                    id, device_name, device_type, adb_id, status, user_id,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                "#,
            )
            .bind(&device_id)
            .bind(format!("Device {}", i + 1))
            .bind(device_type)
            .bind(Option::<String>::None)
            .bind("connected")
            .bind("user-1")
            .bind(&now)
            .bind(&now)
            .execute(&database.pool)
            .await
            .unwrap();

            // 验证设备类型
            let device: Device = sqlx::query_as("SELECT * FROM devices WHERE id = ?")
                .bind(&device_id)
                .fetch_one(&database.pool)
                .await
                .unwrap();

            assert_eq!(device.device_type, *device_type, "设备类型应该匹配");
        }
    }
}
