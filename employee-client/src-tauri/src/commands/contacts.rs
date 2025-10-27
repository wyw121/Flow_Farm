use tauri::State;
use crate::AppState;
use crate::contact_manager::{ContactList, Contact};

/// 从文件加载通讯录
#[tauri::command]
pub async fn load_contacts_from_file(
    file_path: String,
    state: State<'_, AppState>
) -> Result<ContactList, String> {
    let contact_manager = &state.contact_manager;

    match contact_manager.load_contacts_from_txt(&file_path).await {
        Ok(contact_list) => {
            let list_id = contact_list.id.clone();
            let mut contact_lists = state.contact_lists.lock().unwrap();
            contact_lists.insert(list_id, contact_list.clone());
            Ok(contact_list)
        }
        Err(e) => Err(e.to_string())
    }
}

/// 获取通讯录列表
#[tauri::command]
pub async fn get_contact_lists(state: State<'_, AppState>) -> Result<Vec<ContactList>, String> {
    let contact_lists = state.contact_lists.lock().unwrap();
    Ok(contact_lists.values().cloned().collect())
}

/// 搜索通讯录中的联系人
#[tauri::command]
pub async fn search_contacts(
    list_id: String,
    keyword: String,
    state: State<'_, AppState>
) -> Result<Vec<Contact>, String> {
    let contact_lists = state.contact_lists.lock().unwrap();

    if let Some(contact_list) = contact_lists.get(&list_id) {
        let contact_manager = &state.contact_manager;
        let results = contact_manager.search_contacts(&contact_list.contacts, &keyword);
        Ok(results)
    } else {
        Err("联系人列表不存在".to_string())
    }
}
