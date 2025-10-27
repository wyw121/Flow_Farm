// Repository 层：负责所有数据库操作
// Service 层通过 Repository 访问数据，而不是直接操作 Database

pub mod user_repository;
pub mod work_record_repository;
pub mod device_repository;
pub mod billing_repository;

pub use user_repository::UserRepository;
pub use work_record_repository::WorkRecordRepository;
pub use device_repository::DeviceRepository;
pub use billing_repository::BillingRepository;
