use serde::{Deserialize, Serialize};
use tauri::State;
use std::path::PathBuf;
use chrono::{DateTime, Utc};
use crate::auth_service::AuthService;
use crate::commands::visits::VisitService;

/// 多媒体录制类型
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MediaType {
    Photo,
    Audio,
    Video,
    Document,
}

/// 录制状态
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum RecordingStatus {
    Idle,
    Recording,
    Paused,
    Stopped,
}

/// 多媒体文件信息
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MediaFile {
    pub id: Option<i32>,
    pub file_path: String,
    pub file_name: String,
    pub file_size: u64,
    pub media_type: MediaType,
    pub mime_type: String,
    pub duration: Option<f64>, // 录音/录像时长（秒）
    pub created_at: DateTime<Utc>,
    pub uploaded: bool,
}

/// 录制配置
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RecordingConfig {
    pub audio_quality: AudioQuality,
    pub video_quality: VideoQuality,
    pub max_duration: u32, // 最大录制时长（秒）
    pub auto_upload: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum AudioQuality {
    Low,    // 8kHz, 64kbps
    Medium, // 16kHz, 128kbps  
    High,   // 44.1kHz, 256kbps
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum VideoQuality {
    Low,    // 480p
    Medium, // 720p
    High,   // 1080p
}

/// 录制服务状态
pub struct MediaService {
    pub recording_status: std::sync::Arc<std::sync::Mutex<RecordingStatus>>,
    pub current_recording: std::sync::Arc<std::sync::Mutex<Option<MediaFile>>>,
    pub config: std::sync::Arc<std::sync::Mutex<RecordingConfig>>,
    pub media_dir: PathBuf,
}

impl MediaService {
    pub fn new(media_dir: PathBuf) -> Self {
        let default_config = RecordingConfig {
            audio_quality: AudioQuality::Medium,
            video_quality: VideoQuality::Medium,
            max_duration: 300, // 5分钟
            auto_upload: true,
        };

        Self {
            recording_status: std::sync::Arc::new(std::sync::Mutex::new(RecordingStatus::Idle)),
            current_recording: std::sync::Arc::new(std::sync::Mutex::new(None)),
            config: std::sync::Arc::new(std::sync::Mutex::new(default_config)),
            media_dir,
        }
    }
}

/// 获取录制状态
#[tauri::command]
pub async fn get_recording_status(
    media_service: State<'_, MediaService>,
) -> Result<RecordingStatus, String> {
    let status = media_service.recording_status.lock()
        .map_err(|e| format!("Failed to lock recording_status: {}", e))?
        .clone();
    Ok(status)
}

/// 拍照
#[tauri::command]
pub async fn take_photo(
    visit_id: Option<i32>,
    media_service: State<'_, MediaService>,
) -> Result<MediaFile, String> {
    // 检查录制状态
    {
        let status = media_service.recording_status.lock()
            .map_err(|e| format!("Failed to lock recording_status: {}", e))?;
        
        match *status {
            RecordingStatus::Recording => {
                return Err("当前正在录制中，无法拍照".to_string());
            }
            _ => {}
        }
    }

    // 生成文件名
    let timestamp = Utc::now().format("%Y%m%d_%H%M%S").to_string();
    let file_name = format!("photo_{}_{}.jpg", 
        visit_id.map(|id| id.to_string()).unwrap_or_else(|| "general".to_string()),
        timestamp
    );
    
    let file_path = media_service.media_dir.join(&file_name);

    // 在实际实现中，这里会调用相机API拍照
    // 暂时创建一个模拟文件
    simulate_capture_photo(&file_path).await?;

    let file_size = std::fs::metadata(&file_path)
        .map_err(|e| format!("获取文件大小失败: {}", e))?
        .len();

    let media_file = MediaFile {
        id: None,
        file_path: file_path.to_string_lossy().to_string(),
        file_name,
        file_size,
        media_type: MediaType::Photo,
        mime_type: "image/jpeg".to_string(),
        duration: None,
        created_at: Utc::now(),
        uploaded: false,
    };

    Ok(media_file)
}

/// 开始录音
#[tauri::command]
pub async fn start_audio_recording(
    visit_id: Option<i32>,
    media_service: State<'_, MediaService>,
) -> Result<(), String> {
    // 检查当前状态
    {
        let status = media_service.recording_status.lock()
            .map_err(|e| format!("Failed to lock recording_status: {}", e))?;
        
        match *status {
            RecordingStatus::Recording => {
                return Err("已经在录制中".to_string());
            }
            _ => {}
        }
    }

    // 生成文件名
    let timestamp = Utc::now().format("%Y%m%d_%H%M%S").to_string();
    let file_name = format!("audio_{}_{}.wav", 
        visit_id.map(|id| id.to_string()).unwrap_or_else(|| "general".to_string()),
        timestamp
    );
    
    let file_path = media_service.media_dir.join(&file_name);

    // 在实际实现中，这里会启动音频录制
    simulate_start_audio_recording(&file_path).await?;

    let media_file = MediaFile {
        id: None,
        file_path: file_path.to_string_lossy().to_string(),
        file_name,
        file_size: 0, // 录制过程中会增长
        media_type: MediaType::Audio,
        mime_type: "audio/wav".to_string(),
        duration: Some(0.0),
        created_at: Utc::now(),
        uploaded: false,
    };

    // 更新状态
    {
        let mut status = media_service.recording_status.lock()
            .map_err(|e| format!("Failed to lock recording_status: {}", e))?;
        *status = RecordingStatus::Recording;
    }

    {
        let mut current_recording = media_service.current_recording.lock()
            .map_err(|e| format!("Failed to lock current_recording: {}", e))?;
        *current_recording = Some(media_file);
    }

    Ok(())
}

/// 停止录音
#[tauri::command]
pub async fn stop_audio_recording(
    media_service: State<'_, MediaService>,
) -> Result<MediaFile, String> {
    // 检查当前状态
    {
        let status = media_service.recording_status.lock()
            .map_err(|e| format!("Failed to lock recording_status: {}", e))?;
        
        match *status {
            RecordingStatus::Recording => {}
            _ => {
                return Err("当前没有在录制".to_string());
            }
        }
    }

    // 停止录制
    {
        let mut status = media_service.recording_status.lock()
            .map_err(|e| format!("Failed to lock recording_status: {}", e))?;
        *status = RecordingStatus::Stopped;
    }

    // 在实际实现中，这里会停止音频录制并保存文件
    simulate_stop_audio_recording().await?;

    let mut media_file = {
        let mut current_recording = media_service.current_recording.lock()
            .map_err(|e| format!("Failed to lock current_recording: {}", e))?;
        
        current_recording.take()
            .ok_or("没有当前录制")?
    };

    // 更新文件信息
    let file_size = std::fs::metadata(&media_file.file_path)
        .map_err(|e| format!("获取文件大小失败: {}", e))?
        .len();
    
    media_file.file_size = file_size;
    media_file.duration = Some(calculate_audio_duration(&media_file.file_path)?);

    // 重置状态
    {
        let mut status = media_service.recording_status.lock()
            .map_err(|e| format!("Failed to lock recording_status: {}", e))?;
        *status = RecordingStatus::Idle;
    }

    Ok(media_file)
}

/// 开始录像
#[tauri::command]
pub async fn start_video_recording(
    visit_id: Option<i32>,
    media_service: State<'_, MediaService>,
) -> Result<(), String> {
    // 检查当前状态
    {
        let status = media_service.recording_status.lock()
            .map_err(|e| format!("Failed to lock recording_status: {}", e))?;
        
        match *status {
            RecordingStatus::Recording => {
                return Err("已经在录制中".to_string());
            }
            _ => {}
        }
    }

    // 生成文件名
    let timestamp = Utc::now().format("%Y%m%d_%H%M%S").to_string();
    let file_name = format!("video_{}_{}.mp4", 
        visit_id.map(|id| id.to_string()).unwrap_or_else(|| "general".to_string()),
        timestamp
    );
    
    let file_path = media_service.media_dir.join(&file_name);

    // 在实际实现中，这里会启动视频录制
    simulate_start_video_recording(&file_path).await?;

    let media_file = MediaFile {
        id: None,
        file_path: file_path.to_string_lossy().to_string(),
        file_name,
        file_size: 0, // 录制过程中会增长
        media_type: MediaType::Video,
        mime_type: "video/mp4".to_string(),
        duration: Some(0.0),
        created_at: Utc::now(),
        uploaded: false,
    };

    // 更新状态
    {
        let mut status = media_service.recording_status.lock()
            .map_err(|e| format!("Failed to lock recording_status: {}", e))?;
        *status = RecordingStatus::Recording;
    }

    {
        let mut current_recording = media_service.current_recording.lock()
            .map_err(|e| format!("Failed to lock current_recording: {}", e))?;
        *current_recording = Some(media_file);
    }

    Ok(())
}

/// 停止录像
#[tauri::command]
pub async fn stop_video_recording(
    media_service: State<'_, MediaService>,
) -> Result<MediaFile, String> {
    // 检查当前状态
    {
        let status = media_service.recording_status.lock()
            .map_err(|e| format!("Failed to lock recording_status: {}", e))?;
        
        match *status {
            RecordingStatus::Recording => {}
            _ => {
                return Err("当前没有在录制".to_string());
            }
        }
    }

    // 停止录制
    {
        let mut status = media_service.recording_status.lock()
            .map_err(|e| format!("Failed to lock recording_status: {}", e))?;
        *status = RecordingStatus::Stopped;
    }

    // 在实际实现中，这里会停止视频录制并保存文件
    simulate_stop_video_recording().await?;

    let mut media_file = {
        let mut current_recording = media_service.current_recording.lock()
            .map_err(|e| format!("Failed to lock current_recording: {}", e))?;
        
        current_recording.take()
            .ok_or("没有当前录制")?
    };

    // 更新文件信息
    let file_size = std::fs::metadata(&media_file.file_path)
        .map_err(|e| format!("获取文件大小失败: {}", e))?
        .len();
    
    media_file.file_size = file_size;
    media_file.duration = Some(calculate_video_duration(&media_file.file_path)?);

    // 重置状态
    {
        let mut status = media_service.recording_status.lock()
            .map_err(|e| format!("Failed to lock recording_status: {}", e))?;
        *status = RecordingStatus::Idle;
    }

    Ok(media_file)
}

/// 上传媒体文件到服务器
#[tauri::command]
pub async fn upload_media_file(
    visit_id: i32,
    media_file: MediaFile,
    visit_service: State<'_, VisitService>,
    auth_service: State<'_, AuthService>,
) -> Result<i32, String> {
    let token = auth_service.get_token()
        .ok_or("用户未登录")?;

    // 读取文件
    let file_bytes = std::fs::read(&media_file.file_path)
        .map_err(|e| format!("读取文件失败: {}", e))?;

    // 创建 multipart form
    let form = reqwest::multipart::Form::new()
        .part("file", reqwest::multipart::Part::bytes(file_bytes)
            .file_name(media_file.file_name.clone())
            .mime_str(&media_file.mime_type)
            .map_err(|e| format!("设置MIME类型失败: {}", e))?);

    let client = reqwest::Client::new();
    let url = format!("{}/api/v1/visits/{}/attachments", visit_service.api_base_url, visit_id);

    let response = client
        .post(&url)
        .header("Authorization", format!("Bearer {}", token))
        .multipart(form)
        .send()
        .await
        .map_err(|e| format!("上传失败: {}", e))?;

    if !response.status().is_success() {
        return Err(format!("服务器错误: {}", response.status()));
    }

    #[derive(Deserialize)]
    struct UploadResponse {
        id: i32,
    }

    let upload_response: UploadResponse = response.json().await
        .map_err(|e| format!("解析响应失败: {}", e))?;

    Ok(upload_response.id)
}

/// 获取录制配置
#[tauri::command]
pub async fn get_recording_config(
    media_service: State<'_, MediaService>,
) -> Result<RecordingConfig, String> {
    let config = media_service.config.lock()
        .map_err(|e| format!("Failed to lock config: {}", e))?
        .clone();
    Ok(config)
}

/// 更新录制配置
#[tauri::command]
pub async fn update_recording_config(
    new_config: RecordingConfig,
    media_service: State<'_, MediaService>,
) -> Result<(), String> {
    let mut config = media_service.config.lock()
        .map_err(|e| format!("Failed to lock config: {}", e))?;
    *config = new_config;
    Ok(())
}

// 模拟函数（实际实现中需要替换为真实的多媒体API）

async fn simulate_capture_photo(file_path: &std::path::Path) -> Result<(), String> {
    // 创建模拟照片文件
    std::fs::create_dir_all(file_path.parent().unwrap())
        .map_err(|e| format!("创建目录失败: {}", e))?;
    
    std::fs::write(file_path, b"MOCK_PHOTO_DATA")
        .map_err(|e| format!("写入文件失败: {}", e))?;
    
    Ok(())
}

async fn simulate_start_audio_recording(_file_path: &std::path::Path) -> Result<(), String> {
    // 模拟开始录音
    Ok(())
}

async fn simulate_stop_audio_recording() -> Result<(), String> {
    // 模拟停止录音并保存文件
    Ok(())
}

async fn simulate_start_video_recording(_file_path: &std::path::Path) -> Result<(), String> {
    // 模拟开始录像
    Ok(())
}

async fn simulate_stop_video_recording() -> Result<(), String> {
    // 模拟停止录像并保存文件
    Ok(())
}

fn calculate_audio_duration(_file_path: &str) -> Result<f64, String> {
    // 在实际实现中，这里会读取音频文件的元数据获取时长
    // 暂时返回模拟时长
    Ok(30.0) // 30秒
}

fn calculate_video_duration(_file_path: &str) -> Result<f64, String> {
    // 在实际实现中，这里会读取视频文件的元数据获取时长
    // 暂时返回模拟时长
    Ok(60.0) // 60秒
}