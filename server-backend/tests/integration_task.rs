// API集成测试 - Task Management
// 测试工作记录的CRUD操作和任务统计

mod test_helpers;

use flow_farm_backend::models::{CreateWorkRecordRequest, WorkRecord};
use sqlx::SqlitePool;

#[cfg(test)]
mod task_integration_tests {
    use super::*;
    use test_helpers::*;

    async fn insert_test_device(
        pool: &SqlitePool,
        id: &str,
        device_name: &str,
        user_id: &str,
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
        .bind(Option::<String>::None)
        .bind("connected")
        .bind(user_id)
        .bind(&now)
        .bind(&now)
        .execute(pool)
        .await?;

        Ok(())
    }

    async fn insert_test_work_record(
        pool: &SqlitePool,
        id: &str,
        user_id: &str,
        device_id: &str,
        platform: &str,
        target_count: i32,
        completed_count: i32,
        status: &str,
    ) -> Result<(), sqlx::Error> {
        let now = chrono::Utc::now().format("%Y-%m-%d %H:%M:%S").to_string();

        sqlx::query(
            r#"
            INSERT INTO work_records (
                id, user_id, device_id, platform, action_type,
                target_count, completed_count, status,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            "#,
        )
        .bind(id)
        .bind(user_id)
        .bind(device_id)
        .bind(platform)
        .bind("follow")
        .bind(target_count)
        .bind(completed_count)
        .bind(status)
        .bind(&now)
        .bind(&now)
        .execute(pool)
        .await?;

        Ok(())
    }

    #[tokio::test]
    async fn test_work_record_create() {
        let database = create_test_database().await;

        // 创建测试用户和设备
        let password_hash = bcrypt::hash("password123", bcrypt::DEFAULT_COST).unwrap();
        insert_test_user(&database.pool, "user-1", "testuser", &password_hash, "employee")
            .await
            .unwrap();

        insert_test_device(&database.pool, "device-1", "Device 1", "user-1")
            .await
            .unwrap();

        // 创建工作记录
        insert_test_work_record(
            &database.pool,
            "record-1",
            "user-1",
            "device-1",
            "xiaohongshu",
            100,
            0,
            "pending",
        )
        .await
        .unwrap();

        // 验证记录已创建
        let record: WorkRecord = sqlx::query_as("SELECT * FROM work_records WHERE id = ?")
            .bind("record-1")
            .fetch_one(&database.pool)
            .await
            .unwrap();

        assert_eq!(record.user_id, "user-1");
        assert_eq!(record.device_id, "device-1");
        assert_eq!(record.platform, "xiaohongshu");
        assert_eq!(record.target_count, 100);
        assert_eq!(record.completed_count, 0);
        assert_eq!(record.status, "pending");
    }

    #[tokio::test]
    async fn test_work_record_list_by_user() {
        let database = create_test_database().await;

        // 创建测试用户和设备
        let password_hash = bcrypt::hash("password123", bcrypt::DEFAULT_COST).unwrap();
        insert_test_user(&database.pool, "user-1", "testuser", &password_hash, "employee")
            .await
            .unwrap();

        insert_test_device(&database.pool, "device-1", "Device 1", "user-1")
            .await
            .unwrap();

        // 创建多个工作记录
        for i in 1..=5 {
            insert_test_work_record(
                &database.pool,
                &format!("record-{}", i),
                "user-1",
                "device-1",
                "xiaohongshu",
                100,
                i * 10,
                if i >= 5 { "completed" } else { "in_progress" },
            )
            .await
            .unwrap();
        }

        // 查询用户的工作记录
        let records: Vec<WorkRecord> = sqlx::query_as(
            "SELECT * FROM work_records WHERE user_id = ? ORDER BY created_at DESC",
        )
        .bind("user-1")
        .fetch_all(&database.pool)
        .await
        .unwrap();

        assert_eq!(records.len(), 5, "用户应该有5条工作记录");
    }

    #[tokio::test]
    async fn test_work_record_status_filter() {
        let database = create_test_database().await;

        // 创建测试用户和设备
        let password_hash = bcrypt::hash("password123", bcrypt::DEFAULT_COST).unwrap();
        insert_test_user(&database.pool, "user-1", "testuser", &password_hash, "employee")
            .await
            .unwrap();

        insert_test_device(&database.pool, "device-1", "Device 1", "user-1")
            .await
            .unwrap();

        // 创建不同状态的工作记录
        let statuses = vec!["pending", "in_progress", "completed", "failed"];
        for (i, status) in statuses.iter().enumerate() {
            insert_test_work_record(
                &database.pool,
                &format!("record-{}", i + 1),
                "user-1",
                "device-1",
                "xiaohongshu",
                100,
                50,
                status,
            )
            .await
            .unwrap();
        }

        // 查询已完成的记录
        let completed_records: Vec<WorkRecord> = sqlx::query_as(
            "SELECT * FROM work_records WHERE user_id = ? AND status = ?",
        )
        .bind("user-1")
        .bind("completed")
        .fetch_all(&database.pool)
        .await
        .unwrap();

        assert_eq!(completed_records.len(), 1, "应该有1条已完成的记录");

        // 查询进行中的记录
        let in_progress_records: Vec<WorkRecord> = sqlx::query_as(
            "SELECT * FROM work_records WHERE user_id = ? AND status = ?",
        )
        .bind("user-1")
        .bind("in_progress")
        .fetch_all(&database.pool)
        .await
        .unwrap();

        assert_eq!(in_progress_records.len(), 1, "应该有1条进行中的记录");
    }

    #[tokio::test]
    async fn test_work_record_platform_statistics() {
        let database = create_test_database().await;

        // 创建测试用户和设备
        let password_hash = bcrypt::hash("password123", bcrypt::DEFAULT_COST).unwrap();
        insert_test_user(&database.pool, "user-1", "testuser", &password_hash, "employee")
            .await
            .unwrap();

        insert_test_device(&database.pool, "device-1", "Device 1", "user-1")
            .await
            .unwrap();

        // 创建不同平台的工作记录
        insert_test_work_record(&database.pool, "record-1", "user-1", "device-1", "xiaohongshu", 100, 80, "completed").await.unwrap();
        insert_test_work_record(&database.pool, "record-2", "user-1", "device-1", "xiaohongshu", 100, 90, "completed").await.unwrap();
        insert_test_work_record(&database.pool, "record-3", "user-1", "device-1", "douyin", 100, 70, "completed").await.unwrap();
        insert_test_work_record(&database.pool, "record-4", "user-1", "device-1", "douyin", 100, 60, "in_progress").await.unwrap();

        // 按平台统计
        let xiaohongshu_count: (i64,) = sqlx::query_as(
            "SELECT COUNT(*) FROM work_records WHERE user_id = ? AND platform = ?",
        )
        .bind("user-1")
        .bind("xiaohongshu")
        .fetch_one(&database.pool)
        .await
        .unwrap();

        assert_eq!(xiaohongshu_count.0, 2, "小红书应该有2条记录");

        let douyin_count: (i64,) = sqlx::query_as(
            "SELECT COUNT(*) FROM work_records WHERE user_id = ? AND platform = ?",
        )
        .bind("user-1")
        .bind("douyin")
        .fetch_one(&database.pool)
        .await
        .unwrap();

        assert_eq!(douyin_count.0, 2, "抖音应该有2条记录");
    }

    #[tokio::test]
    async fn test_work_record_completion_statistics() {
        let database = create_test_database().await;

        // 创建测试用户和设备
        let password_hash = bcrypt::hash("password123", bcrypt::DEFAULT_COST).unwrap();
        insert_test_user(&database.pool, "user-1", "testuser", &password_hash, "employee")
            .await
            .unwrap();

        insert_test_device(&database.pool, "device-1", "Device 1", "user-1")
            .await
            .unwrap();

        // 创建不同完成度的工作记录
        insert_test_work_record(&database.pool, "record-1", "user-1", "device-1", "xiaohongshu", 100, 100, "completed").await.unwrap();
        insert_test_work_record(&database.pool, "record-2", "user-1", "device-1", "xiaohongshu", 100, 50, "in_progress").await.unwrap();
        insert_test_work_record(&database.pool, "record-3", "user-1", "device-1", "xiaohongshu", 100, 0, "pending").await.unwrap();

        // 计算总完成数
        let total_completed: (Option<i64>,) = sqlx::query_as(
            "SELECT SUM(completed_count) FROM work_records WHERE user_id = ?",
        )
        .bind("user-1")
        .fetch_one(&database.pool)
        .await
        .unwrap();

        assert_eq!(total_completed.0, Some(150), "总完成数应该是150");

        // 计算总目标数
        let total_target: (Option<i64>,) = sqlx::query_as(
            "SELECT SUM(target_count) FROM work_records WHERE user_id = ?",
        )
        .bind("user-1")
        .fetch_one(&database.pool)
        .await
        .unwrap();

        assert_eq!(total_target.0, Some(300), "总目标数应该是300");
    }

    #[tokio::test]
    async fn test_work_record_update_progress() {
        let database = create_test_database().await;

        // 创建测试用户和设备
        let password_hash = bcrypt::hash("password123", bcrypt::DEFAULT_COST).unwrap();
        insert_test_user(&database.pool, "user-1", "testuser", &password_hash, "employee")
            .await
            .unwrap();

        insert_test_device(&database.pool, "device-1", "Device 1", "user-1")
            .await
            .unwrap();

        // 创建工作记录
        insert_test_work_record(
            &database.pool,
            "record-1",
            "user-1",
            "device-1",
            "xiaohongshu",
            100,
            0,
            "pending",
        )
        .await
        .unwrap();

        // 更新进度
        let now = chrono::Utc::now().format("%Y-%m-%d %H:%M:%S").to_string();
        sqlx::query(
            "UPDATE work_records SET completed_count = ?, status = ?, updated_at = ? WHERE id = ?",
        )
        .bind(50)
        .bind("in_progress")
        .bind(&now)
        .bind("record-1")
        .execute(&database.pool)
        .await
        .unwrap();

        // 验证更新
        let record: WorkRecord = sqlx::query_as("SELECT * FROM work_records WHERE id = ?")
            .bind("record-1")
            .fetch_one(&database.pool)
            .await
            .unwrap();

        assert_eq!(record.completed_count, 50, "完成数应该是50");
        assert_eq!(record.status, "in_progress", "状态应该是in_progress");

        // 完成任务
        sqlx::query(
            "UPDATE work_records SET completed_count = ?, status = ?, updated_at = ? WHERE id = ?",
        )
        .bind(100)
        .bind("completed")
        .bind(&now)
        .bind("record-1")
        .execute(&database.pool)
        .await
        .unwrap();

        // 验证完成
        let completed_record: WorkRecord = sqlx::query_as("SELECT * FROM work_records WHERE id = ?")
            .bind("record-1")
            .fetch_one(&database.pool)
            .await
            .unwrap();

        assert_eq!(completed_record.completed_count, 100, "完成数应该是100");
        assert_eq!(completed_record.status, "completed", "状态应该是completed");
    }

    #[tokio::test]
    async fn test_work_record_device_performance() {
        let database = create_test_database().await;

        // 创建测试用户和多个设备
        let password_hash = bcrypt::hash("password123", bcrypt::DEFAULT_COST).unwrap();
        insert_test_user(&database.pool, "user-1", "testuser", &password_hash, "employee")
            .await
            .unwrap();

        for i in 1..=3 {
            insert_test_device(&database.pool, &format!("device-{}", i), &format!("Device {}", i), "user-1")
                .await
                .unwrap();
        }

        // 为每个设备创建工作记录
        insert_test_work_record(&database.pool, "record-1", "user-1", "device-1", "xiaohongshu", 100, 100, "completed").await.unwrap();
        insert_test_work_record(&database.pool, "record-2", "user-1", "device-2", "xiaohongshu", 100, 80, "completed").await.unwrap();
        insert_test_work_record(&database.pool, "record-3", "user-1", "device-3", "xiaohongshu", 100, 90, "completed").await.unwrap();

        // 按设备统计完成数
        for i in 1..=3 {
            let device_total: (Option<i64>,) = sqlx::query_as(
                "SELECT SUM(completed_count) FROM work_records WHERE device_id = ?",
            )
            .bind(&format!("device-{}", i))
            .fetch_one(&database.pool)
            .await
            .unwrap();

            let expected = match i {
                1 => 100,
                2 => 80,
                3 => 90,
                _ => 0,
            };

            assert_eq!(
                device_total.0,
                Some(expected),
                "设备{}的完成数应该是{}",
                i,
                expected
            );
        }
    }
}
