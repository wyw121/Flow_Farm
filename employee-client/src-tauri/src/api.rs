use reqwest;
use serde_json;
use std::collections::HashMap;

#[derive(Debug)]
pub struct ApiClient {
    base_url: String,
    client: reqwest::Client,
    auth_token: Option<String>,
}

impl ApiClient {
    pub fn new(base_url: String) -> Self {
        Self {
            base_url,
            client: reqwest::Client::new(),
            auth_token: None,
        }
    }

    pub fn set_auth_token(&mut self, token: String) {
        self.auth_token = Some(token);
    }

    pub async fn login(
        &mut self,
        username: &str,
        password: &str,
    ) -> Result<String, Box<dyn std::error::Error>> {
        let mut payload = HashMap::new();
        payload.insert("username", username);
        payload.insert("password", password);

        let response = self
            .client
            .post(&format!("{}/auth/login", self.base_url))
            .json(&payload)
            .send()
            .await?;

        if response.status().is_success() {
            let result: serde_json::Value = response.json().await?;
            if let Some(token) = result.get("access_token").and_then(|t| t.as_str()) {
                self.auth_token = Some(token.to_string());
                Ok(token.to_string())
            } else {
                Err("No access token in response".into())
            }
        } else {
            Err(format!("Login failed: {}", response.status()).into())
        }
    }

    pub async fn get_user_info(&self) -> Result<serde_json::Value, Box<dyn std::error::Error>> {
        let token = self.auth_token.as_ref().ok_or("No auth token available")?;

        let response = self
            .client
            .get(&format!("{}/users/me", self.base_url))
            .bearer_auth(token)
            .send()
            .await?;

        if response.status().is_success() {
            Ok(response.json().await?)
        } else {
            Err(format!("Failed to get user info: {}", response.status()).into())
        }
    }

    pub async fn submit_work_record(
        &self,
        record: serde_json::Value,
    ) -> Result<serde_json::Value, Box<dyn std::error::Error>> {
        let token = self.auth_token.as_ref().ok_or("No auth token available")?;

        let response = self
            .client
            .post(&format!("{}/work-records", self.base_url))
            .bearer_auth(token)
            .json(&record)
            .send()
            .await?;

        if response.status().is_success() {
            Ok(response.json().await?)
        } else {
            Err(format!("Failed to submit work record: {}", response.status()).into())
        }
    }
}
