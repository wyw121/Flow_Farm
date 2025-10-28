use axum::{
    extract::{Multipart, Path, State},
    http::StatusCode,
    Json,
};
use chrono::Utc;
use std::fs;
use std::path::{Path as StdPath, PathBuf};
use uuid::Uuid;

use crate::{
    database::Database,
    errors::AppError,
    middleware::auth::AuthContext,
    models::customer::*,
};

/// 上传拜访附件
pub async fn upload_visit_attachment(
    auth_context: AuthContext,
    Path(visit_id): Path<i32>,
    State((database, config)): State<(Database, crate::Config)>,
    mut multipart: Multipart,
) -> Result<Json<VisitAttachment>, AppError> {
    // 检查拜访记录是否存在并验证权限
    let visit: VisitRecord = sqlx::query_as(
        "SELECT * FROM visit_records WHERE id = ?"
    )
    .bind(visit_id)
    .fetch_one(&database.pool)
    .await
    .map_err(|e| match e {
        sqlx::Error::RowNotFound => AppError::NotFound("拜访记录不存在".to_string()),
        _ => AppError::DatabaseError(format!("查询拜访记录失败: {}", e)),
    })?;

    // 权限检查：只有拜访人员或管理员可以上传附件
    if visit.field_worker_id != auth_context.user.id 
        && auth_context.user.role != "research_manager" 
        && auth_context.user.role != "system_admin" {
        return Err(AppError::PermissionDenied("无权上传此拜访的附件".to_string()));
    }

    // 创建上传目录
    let upload_dir = format!("uploads/visits/{}", visit_id);
    let upload_path = PathBuf::from(&upload_dir);
    if !upload_path.exists() {
        fs::create_dir_all(&upload_path)
            .map_err(|e| AppError::InternalServerError(format!("创建上传目录失败: {}", e)))?;
    }

    let mut saved_files = Vec::new();

    // 处理多文件上传
    while let Some(field) = multipart
        .next_field()
        .await
        .map_err(|e| AppError::BadRequest(format!("处理上传文件失败: {}", e)))?
    {
        let name = field.name().unwrap_or("file").to_string();
        let filename = field.file_name().unwrap_or("unknown").to_string();
        let content_type = field.content_type().unwrap_or("application/octet-stream").to_string();

        // 验证文件类型
        let allowed_types = [
            "image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp",
            "audio/mpeg", "audio/wav", "audio/aac", "audio/ogg", "audio/mp4",
            "video/mp4", "video/avi", "video/mov", "video/wmv",
            "application/pdf", "text/plain", "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ];

        if !allowed_types.contains(&content_type.as_str()) {
            return Err(AppError::BadRequest(format!("不支持的文件类型: {}", content_type)));
        }

        // 生成唯一文件名
        let file_extension = StdPath::new(&filename)
            .extension()
            .and_then(|ext| ext.to_str())
            .unwrap_or("tmp");
        let unique_filename = format!("{}_{}.{}", 
            Uuid::new_v4().to_string(), 
            chrono::Utc::now().timestamp(), 
            file_extension
        );
        let file_path = upload_path.join(&unique_filename);

        // 读取文件数据
        let data = field.bytes().await
            .map_err(|e| AppError::BadRequest(format!("读取文件数据失败: {}", e)))?;

        // 检查文件大小（限制为 10MB）
        if data.len() > 10 * 1024 * 1024 {
            return Err(AppError::BadRequest("文件大小超过 10MB 限制".to_string()));
        }

        // 保存文件
        fs::write(&file_path, &data)
            .map_err(|e| AppError::InternalServerError(format!("保存文件失败: {}", e)))?;

        // 确定附件类型
        let attachment_type = match content_type.split('/').next().unwrap_or("") {
            "image" => "image",
            "audio" => "audio", 
            "video" => "video",
            _ => "document",
        }.to_string();

        // 保存附件记录到数据库
        let attachment = sqlx::query_as::<_, VisitAttachment>(
            r#"
            INSERT INTO visit_attachments (
                visit_id, attachment_type, file_name, file_path, file_size,
                mime_type, uploaded_by, upload_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING *
            "#,
        )
        .bind(visit_id)
        .bind(&attachment_type)
        .bind(&filename)
        .bind(file_path.to_string_lossy().to_string())
        .bind(data.len() as i64)
        .bind(&content_type)
        .bind(auth_context.user.id)
        .bind(Utc::now())
        .fetch_one(&database.pool)
        .await
        .map_err(|e| AppError::DatabaseError(format!("保存附件记录失败: {}", e)))?;

        saved_files.push(attachment);
    }

    if saved_files.is_empty() {
        return Err(AppError::BadRequest("没有找到有效的上传文件".to_string()));
    }

    // 返回第一个上传的文件信息（如果是多文件上传，可以返回列表）
    Ok(Json(saved_files.into_iter().next().unwrap()))
}

/// 删除拜访附件
pub async fn delete_visit_attachment(
    auth_context: AuthContext,
    Path((visit_id, attachment_id)): Path<(i32, i32)>,
    State((database, _config)): State<(Database, crate::Config)>,
) -> Result<StatusCode, AppError> {
    // 检查附件是否存在
    let attachment: VisitAttachment = sqlx::query_as(
        "SELECT * FROM visit_attachments WHERE id = ? AND visit_id = ?"
    )
    .bind(attachment_id)
    .bind(visit_id)
    .fetch_one(&database.pool)
    .await
    .map_err(|e| match e {
        sqlx::Error::RowNotFound => AppError::NotFound("附件不存在".to_string()),
        _ => AppError::DatabaseError(format!("查询附件失败: {}", e)),
    })?;

    // 检查拜访记录权限
    let visit: VisitRecord = sqlx::query_as(
        "SELECT * FROM visit_records WHERE id = ?"
    )
    .bind(visit_id)
    .fetch_one(&database.pool)
    .await
    .map_err(|e| AppError::DatabaseError(format!("查询拜访记录失败: {}", e)))?;

    // 权限检查：只有上传者、拜访人员或管理员可以删除附件
    if attachment.uploaded_by != auth_context.user.id 
        && visit.field_worker_id != auth_context.user.id
        && auth_context.user.role != "research_manager" 
        && auth_context.user.role != "system_admin" {
        return Err(AppError::PermissionDenied("无权删除此附件".to_string()));
    }

    // 删除文件
    if let Err(e) = fs::remove_file(&attachment.file_path) {
        eprintln!("删除文件失败: {} ({})", attachment.file_path, e);
        // 不阻止数据库记录的删除
    }

    // 删除数据库记录
    sqlx::query("DELETE FROM visit_attachments WHERE id = ?")
        .bind(attachment_id)
        .execute(&database.pool)
        .await
        .map_err(|e| AppError::DatabaseError(format!("删除附件记录失败: {}", e)))?;

    Ok(StatusCode::NO_CONTENT)
}

/// 获取拜访附件列表
pub async fn get_visit_attachments(
    auth_context: AuthContext,
    Path(visit_id): Path<i32>,
    State((database, _config)): State<(Database, crate::Config)>,
) -> Result<Json<Vec<VisitAttachment>>, AppError> {
    // 检查拜访记录是否存在并验证权限
    let visit: VisitRecord = sqlx::query_as(
        "SELECT * FROM visit_records WHERE id = ?"
    )
    .bind(visit_id)
    .fetch_one(&database.pool)
    .await
    .map_err(|e| match e {
        sqlx::Error::RowNotFound => AppError::NotFound("拜访记录不存在".to_string()),
        _ => AppError::DatabaseError(format!("查询拜访记录失败: {}", e)),
    })?;

    // 验证客户是否属于当前公司
    let _customer: Customer = sqlx::query_as(
        "SELECT * FROM customers WHERE id = ? AND company_id = ?"
    )
    .bind(visit.customer_id)
    .bind(auth_context.user.company_id.unwrap_or(1))
    .fetch_one(&database.pool)
    .await
    .map_err(|e| match e {
        sqlx::Error::RowNotFound => AppError::NotFound("客户不存在或无权访问".to_string()),
        _ => AppError::DatabaseError(format!("查询客户失败: {}", e)),
    })?;

    // 查询附件列表
    let attachments: Vec<VisitAttachment> = sqlx::query_as(
        r#"
        SELECT * FROM visit_attachments 
        WHERE visit_id = ? 
        ORDER BY upload_time DESC
        "#
    )
    .bind(visit_id)
    .fetch_all(&database.pool)
    .await
    .map_err(|e| AppError::DatabaseError(format!("查询附件列表失败: {}", e)))?;

    Ok(Json(attachments))
}

/// 下载拜访附件
pub async fn download_visit_attachment(
    auth_context: AuthContext,
    Path((visit_id, attachment_id)): Path<(i32, i32)>,
    State((database, _config)): State<(Database, crate::Config)>,
) -> Result<Vec<u8>, AppError> {
    // 检查附件是否存在
    let attachment: VisitAttachment = sqlx::query_as(
        "SELECT * FROM visit_attachments WHERE id = ? AND visit_id = ?"
    )
    .bind(attachment_id)
    .bind(visit_id)
    .fetch_one(&database.pool)
    .await
    .map_err(|e| match e {
        sqlx::Error::RowNotFound => AppError::NotFound("附件不存在".to_string()),
        _ => AppError::DatabaseError(format!("查询附件失败: {}", e)),
    })?;

    // 验证访问权限（通过检查拜访记录的客户是否属于当前公司）
    let visit: VisitRecord = sqlx::query_as(
        "SELECT * FROM visit_records WHERE id = ?"
    )
    .bind(visit_id)
    .fetch_one(&database.pool)
    .await
    .map_err(|e| AppError::DatabaseError(format!("查询拜访记录失败: {}", e)))?;

    let _customer: Customer = sqlx::query_as(
        "SELECT * FROM customers WHERE id = ? AND company_id = ?"
    )
    .bind(visit.customer_id)
    .bind(auth_context.user.company_id.unwrap_or(1))
    .fetch_one(&database.pool)
    .await
    .map_err(|e| match e {
        sqlx::Error::RowNotFound => AppError::NotFound("客户不存在或无权访问".to_string()),
        _ => AppError::DatabaseError(format!("查询客户失败: {}", e)),
    })?;

    // 读取文件
    let file_data = fs::read(&attachment.file_path)
        .map_err(|e| AppError::NotFound(format!("文件不存在或读取失败: {}", e)))?;

    Ok(file_data)
}