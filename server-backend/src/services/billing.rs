use anyhow::{Result, anyhow};
use crate::{Database, models::{UserInfo, BillingRecord, CreateBillingRecordRequest}};

pub struct BillingService {
    database: Database,
}

impl BillingService {
    pub fn new(database: Database) -> Self {
        Self { database }
    }

    pub async fn list_billing_records(
        &self,
        current_user: &UserInfo,
        page: i32,
        limit: i32,
        user_id: Option<&str>,
    ) -> Result<Vec<BillingRecord>> {
        Err(anyhow!("功能待实现"))
    }

    pub async fn create_billing_record(
        &self,
        current_user: &UserInfo,
        request: CreateBillingRecordRequest,
    ) -> Result<BillingRecord> {
        Err(anyhow!("功能待实现"))
    }
}
