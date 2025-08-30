use anyhow::{Result, anyhow};
use crate::{Database, models::{UserInfo, KpiStats, UserStats}};

pub struct KpiService {
    database: Database,
}

impl KpiService {
    pub fn new(database: Database) -> Self {
        Self { database }
    }

    pub async fn get_kpi_stats(
        &self,
        current_user: &UserInfo,
        start_date: Option<&str>,
        end_date: Option<&str>,
        platform: Option<&str>,
    ) -> Result<KpiStats> {
        Err(anyhow!("功能待实现"))
    }

    pub async fn get_user_stats(
        &self,
        current_user: &UserInfo,
        start_date: Option<&str>,
        end_date: Option<&str>,
    ) -> Result<Vec<UserStats>> {
        Err(anyhow!("功能待实现"))
    }
}
