use axum::{
    extract::{Path, Query, State},
    Json,
};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

use crate::{
    database::Database,
    errors::AppError,
    middleware::auth::AuthContext,
    models::{
        survey::*,
        SurveyAnalytics,
    },
};

/// 查询参数
#[derive(Debug, Deserialize)]
pub struct AnalyticsQuery {
    pub start_date: Option<String>,
    pub end_date: Option<String>,
    pub demographic_filter: Option<String>,
}

/// 获取问卷分析数据
pub async fn get_survey_analytics(
    auth_context: AuthContext,
    Path(survey_id): Path<i32>,
    Query(query): Query<AnalyticsQuery>,
    State((database, _config)): State<(Database, crate::Config)>,
) -> Result<Json<SurveyAnalytics>, AppError> {
    // 检查问卷是否存在和权限
    let survey: Survey = sqlx::query_as(
        "SELECT * FROM surveys WHERE id = ? AND company_id = ?"
    )
    .bind(survey_id)
    .bind(auth_context.user.company_id.unwrap_or(1))
    .fetch_one(&database.pool)
    .await
    .map_err(|e| match e {
        sqlx::Error::RowNotFound => AppError::NotFound("问卷不存在".to_string()),
        _ => AppError::DatabaseError(format!("查询问卷失败: {}", e)),
    })?;

    // 构建时间过滤条件
    let mut time_filter = String::new();
    let mut params: Vec<String> = vec![survey_id.to_string()];

    if let Some(start_date) = &query.start_date {
        time_filter.push_str(" AND submitted_at >= ?");
        params.push(start_date.clone());
    }

    if let Some(end_date) = &query.end_date {
        time_filter.push_str(" AND submitted_at <= ?");
        params.push(end_date.clone());
    }

    // 获取基础统计数据
    let total_responses: (i32,) = sqlx::query_as(&format!(
        "SELECT COUNT(*) as count FROM survey_responses WHERE survey_id = ?{}", 
        time_filter
    ))
    .bind(survey_id)
    .fetch_one(&database.pool)
    .await
    .unwrap_or((0,));

    // 获取完成率（基于必填题完成情况）
    let completion_rate = calculate_completion_rate(&database, survey_id, &time_filter).await?;

    // 获取问题回答统计
    let question_stats = calculate_question_statistics(&database, survey_id, &survey, &time_filter).await?;

    // 获取人口统计学分析
    let demographic_breakdown = calculate_demographic_breakdown(&database, survey_id, &time_filter).await?;

    // 获取时间分布
    let time_distribution = calculate_time_distribution(&database, survey_id, &time_filter).await?;

    // 获取地理分布
    let geographic_distribution = calculate_geographic_distribution(&database, survey_id, &time_filter).await?;

    // 构建分析结果
    let analytics = SurveyAnalytics {
        survey_id,
        total_responses: total_responses.0,
        completion_rate,
        question_statistics: question_stats,
        demographic_breakdown,
        time_distribution,
        geographic_distribution,
        response_quality_score: calculate_quality_score(total_responses.0, completion_rate),
        insights: generate_insights(&survey, total_responses.0, completion_rate),
    };

    Ok(Json(analytics))
}

/// 计算完成率
async fn calculate_completion_rate(
    database: &Database,
    survey_id: i32,
    time_filter: &str,
) -> Result<f64, AppError> {
    let total_responses: (i32,) = sqlx::query_as(&format!(
        "SELECT COUNT(*) as count FROM survey_responses WHERE survey_id = ?{}", 
        time_filter
    ))
    .bind(survey_id)
    .fetch_one(&database.pool)
    .await
    .unwrap_or((0,));

    if total_responses.0 == 0 {
        return Ok(0.0);
    }

    // 简化的完成率计算 - 假设所有提交的回答都是完整的
    // 在实际应用中，应该根据必填题的完成情况来计算
    Ok(100.0)
}

/// 计算问题统计数据
async fn calculate_question_statistics(
    database: &Database,
    survey_id: i32,
    survey: &Survey,
    time_filter: &str,
) -> Result<Vec<QuestionStatistic>, AppError> {
    // 获取所有回答
    let responses: Vec<SurveyResponse> = sqlx::query_as(&format!(
        "SELECT * FROM survey_responses WHERE survey_id = ?{}", 
        time_filter
    ))
    .bind(survey_id)
    .fetch_all(&database.pool)
    .await
    .map_err(|e| AppError::DatabaseError(format!("查询回答失败: {}", e)))?;

    // 解析问卷结构
    let questions: Vec<Question> = serde_json::from_value(survey.structure.clone())
        .unwrap_or_default();

    let mut statistics = Vec::new();

    for (index, question) in questions.iter().enumerate() {
        let mut answer_counts = HashMap::new();
        let mut total_answers = 0;

        // 统计每个问题的回答
        for response in &responses {
            if let Ok(answers) = serde_json::from_value::<HashMap<String, serde_json::Value>>(response.answers.clone()) {
                if let Some(answer) = answers.get(&index.to_string()) {
                    let answer_str = match answer {
                        serde_json::Value::String(s) => s.clone(),
                        serde_json::Value::Array(arr) => {
                            // 多选题处理
                            arr.iter()
                                .filter_map(|v| v.as_str())
                                .collect::<Vec<_>>()
                                .join(", ")
                        },
                        serde_json::Value::Number(n) => n.to_string(),
                        serde_json::Value::Bool(b) => b.to_string(),
                        _ => "其他".to_string(),
                    };

                    *answer_counts.entry(answer_str).or_insert(0) += 1;
                    total_answers += 1;
                }
            }
        }

        // 计算百分比
        let answer_distribution: HashMap<String, f64> = answer_counts
            .iter()
            .map(|(answer, count)| {
                let percentage = if total_answers > 0 {
                    (*count as f64 / total_answers as f64) * 100.0
                } else {
                    0.0
                };
                (answer.clone(), percentage)
            })
            .collect();

        statistics.push(QuestionStatistic {
            question_id: index.to_string(),
            question_text: question.title.clone(),
            question_type: question.question_type.clone(),
            total_responses: total_answers,
            answer_distribution,
            average_rating: calculate_average_rating(&answer_counts, &question.question_type),
        });
    }

    Ok(statistics)
}

/// 计算人口统计学分布
async fn calculate_demographic_breakdown(
    database: &Database,
    survey_id: i32,
    time_filter: &str,
) -> Result<HashMap<String, HashMap<String, f64>>, AppError> {
    let responses: Vec<SurveyResponse> = sqlx::query_as(&format!(
        "SELECT * FROM survey_responses WHERE survey_id = ?{}", 
        time_filter
    ))
    .bind(survey_id)
    .fetch_all(&database.pool)
    .await
    .map_err(|e| AppError::DatabaseError(format!("查询回答失败: {}", e)))?;

    let mut demographics = HashMap::new();
    let total_responses = responses.len() as f64;

    if total_responses == 0.0 {
        return Ok(demographics);
    }

    // 统计年龄分布
    let mut age_groups = HashMap::new();
    // 统计性别分布
    let mut gender_groups = HashMap::new();
    // 统计地区分布
    let mut region_groups = HashMap::new();

    for response in &responses {
        if let Ok(respondent_info) = serde_json::from_value::<HashMap<String, serde_json::Value>>(response.respondent_info.clone()) {
            // 年龄分组
            if let Some(age) = respondent_info.get("age").and_then(|v| v.as_i64()) {
                let age_group = match age {
                    0..=17 => "18岁以下",
                    18..=24 => "18-24岁",
                    25..=34 => "25-34岁",
                    35..=44 => "35-44岁",
                    45..=54 => "45-54岁",
                    55..=64 => "55-64岁",
                    _ => "65岁以上",
                };
                *age_groups.entry(age_group.to_string()).or_insert(0) += 1;
            }

            // 性别分组
            if let Some(gender) = respondent_info.get("gender").and_then(|v| v.as_str()) {
                *gender_groups.entry(gender.to_string()).or_insert(0) += 1;
            }

            // 地区分组
            if let Some(region) = respondent_info.get("region").and_then(|v| v.as_str()) {
                *region_groups.entry(region.to_string()).or_insert(0) += 1;
            }
        }
    }

    // 转换为百分比
    demographics.insert("age".to_string(), 
        age_groups.iter().map(|(k, v)| (k.clone(), (*v as f64 / total_responses) * 100.0)).collect()
    );
    demographics.insert("gender".to_string(), 
        gender_groups.iter().map(|(k, v)| (k.clone(), (*v as f64 / total_responses) * 100.0)).collect()
    );
    demographics.insert("region".to_string(), 
        region_groups.iter().map(|(k, v)| (k.clone(), (*v as f64 / total_responses) * 100.0)).collect()
    );

    Ok(demographics)
}

/// 计算时间分布
async fn calculate_time_distribution(
    database: &Database,
    survey_id: i32,
    time_filter: &str,
) -> Result<HashMap<String, i32>, AppError> {
    let responses: Vec<SurveyResponse> = sqlx::query_as(&format!(
        "SELECT * FROM survey_responses WHERE survey_id = ?{}", 
        time_filter
    ))
    .bind(survey_id)
    .fetch_all(&database.pool)
    .await
    .map_err(|e| AppError::DatabaseError(format!("查询回答失败: {}", e)))?;

    let mut time_distribution = HashMap::new();

    for response in &responses {
        if let Ok(submitted_at) = chrono::DateTime::parse_from_rfc3339(&response.submitted_at.to_rfc3339()) {
            let date_str = submitted_at.format("%Y-%m-%d").to_string();
            *time_distribution.entry(date_str).or_insert(0) += 1;
        }
    }

    Ok(time_distribution)
}

/// 计算地理分布
async fn calculate_geographic_distribution(
    database: &Database,
    survey_id: i32,
    time_filter: &str,
) -> Result<HashMap<String, i32>, AppError> {
    let responses: Vec<SurveyResponse> = sqlx::query_as(&format!(
        "SELECT location FROM survey_responses WHERE survey_id = ? AND location IS NOT NULL{}", 
        time_filter
    ))
    .bind(survey_id)
    .fetch_all(&database.pool)
    .await
    .map_err(|e| AppError::DatabaseError(format!("查询回答失败: {}", e)))?;

    let mut geographic_distribution = HashMap::new();

    for response in &responses {
        if let Some(location) = &response.location {
            // 简化的地理位置处理 - 可以集成地理编码服务
            if let Ok(location_data) = serde_json::from_str::<HashMap<String, serde_json::Value>>(location) {
                if let Some(city) = location_data.get("city").and_then(|v| v.as_str()) {
                    *geographic_distribution.entry(city.to_string()).or_insert(0) += 1;
                }
            }
        }
    }

    Ok(geographic_distribution)
}

/// 计算平均评分（仅对评分类问题）
fn calculate_average_rating(answer_counts: &HashMap<String, i32>, question_type: &QuestionType) -> Option<f64> {
    match question_type {
        QuestionType::Rating => {
            let mut total_score = 0.0;
            let mut total_count = 0;

            for (answer, count) in answer_counts {
                if let Ok(rating) = answer.parse::<f64>() {
                    total_score += rating * (*count as f64);
                    total_count += count;
                }
            }

            if total_count > 0 {
                Some(total_score / (total_count as f64))
            } else {
                None
            }
        },
        _ => None,
    }
}

/// 计算回答质量分数
fn calculate_quality_score(total_responses: i32, completion_rate: f64) -> f64 {
    // 简化的质量分数计算
    let response_score = if total_responses >= 100 { 40.0 } else { (total_responses as f64 / 100.0) * 40.0 };
    let completion_score = completion_rate * 0.6;
    
    response_score + completion_score
}

/// 生成洞察建议
fn generate_insights(survey: &Survey, total_responses: i32, completion_rate: f64) -> Vec<String> {
    let mut insights = Vec::new();

    // 样本量分析
    if let Some(target) = survey.target_sample_size {
        let progress = (total_responses as f64 / target as f64) * 100.0;
        if progress < 50.0 {
            insights.push(format!("样本收集进度为{:.1}%，建议加强推广以达到目标样本量", progress));
        } else if progress >= 100.0 {
            insights.push("已达到目标样本量，数据收集完成".to_string());
        }
    }

    // 完成率分析
    if completion_rate < 80.0 {
        insights.push("问卷完成率偏低，建议检查问题设置是否合理".to_string());
    } else if completion_rate >= 95.0 {
        insights.push("问卷完成率很高，数据质量良好".to_string());
    }

    // 回答数量分析
    if total_responses < 30 {
        insights.push("当前样本量较小，结果可能存在统计偏差".to_string());
    } else if total_responses >= 200 {
        insights.push("样本量充足，统计结果具有较高可信度".to_string());
    }

    if insights.is_empty() {
        insights.push("数据收集正常进行中".to_string());
    }

    insights
}

/// 导出分析报告
pub async fn export_survey_report(
    auth_context: AuthContext,
    Path(survey_id): Path<i32>,
    Query(query): Query<AnalyticsQuery>,
    State((database, _config)): State<(Database, crate::Config)>,
) -> Result<Json<serde_json::Value>, AppError> {
    // 获取分析数据
    let analytics_response = get_survey_analytics(auth_context, Path(survey_id), Query(query), State((database, _config))).await?;
    let analytics = analytics_response.0;

    // 构建导出数据
    let export_data = serde_json::json!({
        "survey_id": analytics.survey_id,
        "export_time": chrono::Utc::now().to_rfc3339(),
        "summary": {
            "total_responses": analytics.total_responses,
            "completion_rate": analytics.completion_rate,
            "quality_score": analytics.response_quality_score
        },
        "detailed_analytics": analytics,
        "export_format": "json"
    });

    Ok(Json(export_data))
}