use adb_xml_reader::{AdbClient, UIElement};
use anyhow::Result;
use clap::{Arg, Command};
use serde_json;
use std::fs;

#[tokio::main]
async fn main() -> Result<()> {
    let matches = Command::new("ADB XML Reader")
        .version("1.0")
        .author("Flow Farm Team")
        .about("通过 ADB 读取 Android 设备的 UI XML 信息")
        .arg(
            Arg::new("device")
                .short('d')
                .long("device")
                .value_name("DEVICE_ID")
                .help("指定设备 ID（可选，如果只有一台设备）")
        )
        .arg(
            Arg::new("output")
                .short('o')
                .long("output")
                .value_name("FILE")
                .help("输出 JSON 文件路径")
                .default_value("ui_hierarchy.json")
        )
        .arg(
            Arg::new("screenshot")
                .short('s')
                .long("screenshot")
                .value_name("FILE")
                .help("同时保存屏幕截图")
                .default_value("screenshot.png")
        )
        .arg(
            Arg::new("search")
                .long("search")
                .value_name("TEXT")
                .help("搜索包含指定文本的元素")
        )
        .arg(
            Arg::new("find-id")
                .long("find-id")
                .value_name("RESOURCE_ID")
                .help("查找具有指定资源ID的元素")
        )
        .arg(
            Arg::new("print")
                .short('p')
                .long("print")
                .help("在终端打印 UI 层次结构")
                .action(clap::ArgAction::SetTrue)
        )
        .arg(
            Arg::new("auto-contact-flow")
                .long("auto-contact-flow")
                .help("自动执行联系人流程: 左上角菜单 -> 发现好友 -> 通讯录")
                .action(clap::ArgAction::SetTrue)
        )
        .arg(
            Arg::new("auto-follow-contacts")
                .long("auto-follow-contacts")
                .help("自动执行联系人流程并关注所有通讯录好友")
                .action(clap::ArgAction::SetTrue)
        )
        .arg(
            Arg::new("smart-follow")
                .long("smart-follow")
                .help("智能检测当前页面并自动关注通讯录好友（推荐）")
                .action(clap::ArgAction::SetTrue)
        )
        .arg(
            Arg::new("follow-current-page")
                .long("follow-current-page")
                .help("直接关注当前页面的所有用户（无需导航）")
                .action(clap::ArgAction::SetTrue)
        )
        .arg(
            Arg::new("import-contacts")
                .long("import-contacts")
                .value_name("CSV_FILE")
                .help("从CSV文件导入联系人到设备 (格式: 姓名,电话,地址,职业,邮箱)")
        )
        .arg(
            Arg::new("import-contacts-optimized")
                .long("import-contacts-optimized")
                .value_name("CSV_FILE")
                .help("优化版联系人导入 (避免Google登录弹窗，适用于小红书等应用)")
        )
        .arg(
            Arg::new("import-vcf")
                .long("import-vcf")
                .value_name("CSV_FILE")
                .help("通过VCF文件导入联系人 (格式: 姓名,电话,地址,职业,邮箱)")
        )
        .arg(
            Arg::new("click")
                .long("click")
                .value_name("X,Y")
                .help("点击指定坐标 (格式: x,y)")
        )
        .get_matches();

    let device_id = matches.get_one::<String>("device").cloned();
    let output_file = matches.get_one::<String>("output").unwrap();
    let screenshot_file = matches.get_one::<String>("screenshot").unwrap();
    let search_text = matches.get_one::<String>("search");
    let find_resource_id = matches.get_one::<String>("find-id");
    let print_hierarchy = matches.get_flag("print");
    let auto_contact_flow = matches.get_flag("auto-contact-flow");
    let auto_follow_contacts = matches.get_flag("auto-follow-contacts");
    let smart_follow = matches.get_flag("smart-follow");
    let click_coords = matches.get_one::<String>("click");
    let import_contacts_file = matches.get_one::<String>("import-contacts");
    let import_contacts_optimized_file = matches.get_one::<String>("import-contacts-optimized");
    let import_vcf_file = matches.get_one::<String>("import-vcf");

    let adb_client = AdbClient::new(device_id.clone());

    // 显示连接的设备
    println!("正在检查连接的设备...");
    let devices = adb_client.get_devices().await?;

    if devices.is_empty() {
        println!("❌ 未找到连接的设备");
        println!("请确保:");
        println!("1. Android 设备已连接并启用 USB 调试");
        println!("2. ADB 已正确安装并在 PATH 中");
        println!("3. 设备已授权 ADB 连接");
        return Ok(());
    }

    println!("✅ 发现设备:");
    for (i, device) in devices.iter().enumerate() {
        let marker = if Some(device) == device_id.as_ref() || (device_id.is_none() && i == 0) {
            "➤"
        } else {
            " "
        };
        println!("  {} {}", marker, device);
    }

    let target_device = device_id.or_else(|| devices.first().cloned());
    if let Some(device) = &target_device {
        println!("使用设备: {}", device);
    }

    // 获取 UI 层次结构
    println!("\n正在获取 UI 层次结构...");
    let xml_content = adb_client.dump_ui_hierarchy().await?;

    if xml_content.trim().is_empty() {
        println!("❌ 获取到空的 XML 内容，请确保设备屏幕处于活动状态");
        return Ok(());
    }

    println!("✅ 成功获取 UI XML ({} 字符)", xml_content.len());

    // 解析 XML
    println!("正在解析 UI 层次结构...");
    let ui_root = adb_client.parse_ui_xml(&xml_content)?;
    println!("✅ 解析完成，发现 UI 元素");

    // 保存 JSON 文件
    println!("正在保存到 {}...", output_file);
    let json_content = serde_json::to_string_pretty(&ui_root)?;
    fs::write(output_file, json_content)?;
    println!("✅ UI 层次结构已保存到: {}", output_file);

    // 保存截图（如果指定）
    if matches.contains_id("screenshot") {
        println!("正在获取屏幕截图...");
        match adb_client.take_screenshot(screenshot_file).await {
            Ok(_) => println!("✅ 截图已保存"),
            Err(e) => println!("⚠️  截图失败: {}", e),
        }
    }

    // 打印层次结构（如果指定）
    if print_hierarchy {
        println!("\n📋 UI 层次结构:");
        println!("{}", "=".repeat(50));
        adb_client.print_hierarchy(&ui_root, 0);
    }

    // 搜索文本（如果指定）
    if let Some(text) = search_text {
        println!("\n🔍 搜索包含文本 \"{}\" 的元素:", text);
        println!("{}", "-".repeat(40));
        let found_elements = adb_client.find_elements_by_text(&ui_root, text);

        if found_elements.is_empty() {
            println!("  未找到包含该文本的元素");
        } else {
            for (i, element) in found_elements.iter().enumerate() {
                println!("  {}. [{}]", i + 1, element.tag);
                if let Some(text) = &element.text {
                    println!("     文本: \"{}\"", text);
                }
                if let Some(desc) = &element.content_desc {
                    println!("     描述: \"{}\"", desc);
                }
                if let Some(id) = &element.resource_id {
                    println!("     ID: {}", id);
                }
                if let Some(bounds) = &element.bounds {
                    println!("     位置: {}", bounds);
                }
                println!("     可点击: {}", element.clickable);
                println!();
            }
        }
    }

    // 查找资源ID（如果指定）
    if let Some(resource_id) = find_resource_id {
        println!("\n🎯 查找资源ID \"{}\":", resource_id);
        println!("{}", "-".repeat(40));

        if let Some(element) = adb_client.find_element_by_resource_id(&ui_root, resource_id) {
            println!("  ✅ 找到元素:");
            println!("     标签: [{}]", element.tag);
            if let Some(class) = &element.class {
                println!("     类名: {}", class);
            }
            if let Some(text) = &element.text {
                println!("     文本: \"{}\"", text);
            }
            if let Some(desc) = &element.content_desc {
                println!("     描述: \"{}\"", desc);
            }
            if let Some(bounds) = &element.bounds {
                println!("     位置: {}", bounds);
            }
            println!("     可点击: {}", element.clickable);
            println!("     已启用: {}", element.enabled);
        } else {
            println!("  ❌ 未找到具有该资源ID的元素");
        }
    }

    // 点击指定坐标（如果指定）
    if let Some(coords) = click_coords {
        let coords_parts: Vec<&str> = coords.split(',').collect();
        if coords_parts.len() == 2 {
            if let (Ok(x), Ok(y)) = (coords_parts[0].parse::<i32>(), coords_parts[1].parse::<i32>()) {
                println!("\n👆 执行点击操作...");
                match adb_client.click_coordinates(x, y).await {
                    Ok(_) => println!("✅ 点击成功: ({}, {})", x, y),
                    Err(e) => println!("❌ 点击失败: {}", e),
                }
            } else {
                println!("❌ 坐标格式错误，应为: x,y");
            }
        } else {
            println!("❌ 坐标格式错误，应为: x,y");
        }
    }

    // 执行智能关注流程（如果指定）
    if smart_follow {
        println!("\n🧠 开始执行智能关注流程...");
        println!("   📢 将自动检测当前页面状态并从合适位置开始");
        println!("{}", "=".repeat(50));

        match adb_client.execute_smart_contact_flow().await {
            Ok(_) => {
                println!("\n✅ 智能关注流程执行成功！");
                return Ok(());
            },
            Err(e) => {
                println!("❌ 智能关注流程执行失败: {}", e);
                println!("提示: 请确保在小红书APP中，程序会自动检测页面状态");
            }
        }
    }

    // 执行自动联系人流程（如果指定）
    if auto_contact_flow || auto_follow_contacts {
        println!("\n🤖 开始执行自动联系人流程...");
        if auto_follow_contacts {
            println!("   📢 注意: 将在联系人流程后自动关注所有好友");
        }
        println!("{}", "=".repeat(50));

        match adb_client.execute_contact_flow().await {
            Ok(_) => {
                println!("\n✅ 自动联系人流程执行成功！");
                if auto_follow_contacts {
                    println!("✅ 已完成: 左上角菜单 -> 发现好友 -> 通讯录 -> 自动关注");
                } else {
                    println!("已完成: 左上角菜单 -> 发现好友 -> 通讯录");
                }

                // 如果执行了自动流程，直接返回，不显示常规统计信息
                return Ok(());
            },
            Err(e) => {
                println!("❌ 自动联系人流程执行失败: {}", e);
                println!("提示: 请确保应用界面正确，并且元素可见");
            }
        }
    }

    // 执行VCF联系人导入（如果指定）
    if let Some(contacts_file) = import_vcf_file {
        println!("\n📞 开始VCF联系人导入...");
        println!("{}", "=".repeat(50));

        let adb_path = "D:\\leidian\\LDPlayer9\\adb.exe";
        let default_device = "127.0.0.1:5555".to_string();
        let device_id = target_device.as_ref().unwrap_or(&default_device);
        let vcf_importer = adb_xml_reader::VcfImporter::new(adb_path, device_id);

        match vcf_importer.import_contacts_from_file(contacts_file).await {
            Ok(_) => {
                println!("\n✅ VCF联系人导入准备完成！");
                println!("📱 请按照提示在设备上完成导入操作");

                // 如果执行了VCF导入流程，直接返回
                return Ok(());
            },
            Err(e) => {
                println!("❌ VCF联系人导入失败: {}", e);
                println!("💡 建议：");
                println!("   1. 确保联系人文件格式正确 (姓名,电话,地址,职业,邮箱)");
                println!("   2. 检查设备存储权限");
                println!("   3. 确保联系人应用可以正常打开");
                return Err(e);
            }
        }
    }

    // 执行优化版联系人导入（如果指定）
    if let Some(contacts_file) = import_contacts_optimized_file {
        println!("\n📞 开始优化版联系人导入（避免Google登录弹窗）...");
        println!("{}", "=".repeat(60));

        match adb_client.import_contacts_to_device(contacts_file).await {
            Ok(_) => {
                println!("\n✅ 优化版联系人导入完成！");
                println!("🎯 特点：避免了Google登录弹窗干扰");
                println!("📄 建议检查小红书通讯录页面确认导入结果");

                // 如果执行了导入流程，直接返回
                return Ok(());
            },
            Err(e) => {
                println!("❌ 优化版联系人导入失败: {}", e);
                println!("💡 建议：");
                println!("   1. 确保当前在小红书通讯录页面");
                println!("   2. 检查联系人文件格式 (姓名,电话)");
                println!("   3. 确保设备屏幕常亮，避免锁屏");
                return Err(e);
            }
        }
    }

    // 执行联系人导入（如果指定）
    if let Some(contacts_file) = import_contacts_file {
        println!("\n📞 开始导入联系人...");
        println!("{}", "=".repeat(50));

        match adb_client.import_contacts_to_device(contacts_file).await {
            Ok(_) => {
                println!("\n✅ 联系人导入流程执行完成！");
                println!("详细结果请查看 contact_import_report.txt");

                // 如果执行了导入流程，直接返回
                return Ok(());
            },
            Err(e) => {
                println!("❌ 联系人导入失败: {}", e);
                println!("提示: 请确保CSV文件格式正确，设备连接正常");
                return Err(e);
            }
        }
    }

    // 显示统计信息
    let stats = count_elements(&ui_root);
    println!("\n📊 统计信息:");
    println!("{}", "-".repeat(20));
    println!("  总元素数: {}", stats.total);
    println!("  可点击元素: {}", stats.clickable);
    println!("  有文本元素: {}", stats.with_text);
    println!("  有ID元素: {}", stats.with_id);

    println!("\n🎉 分析完成!");
    println!("💡 提示:");
    println!("  - 使用 --print 查看完整层次结构");
    println!("  - 使用 --search \"文本\" 搜索特定元素");
    println!("  - 使用 --find-id \"ID\" 查找特定资源ID");
    println!("  - JSON 文件可用于进一步分析或自动化脚本");

    Ok(())
}

struct ElementStats {
    total: usize,
    clickable: usize,
    with_text: usize,
    with_id: usize,
}

fn count_elements(element: &UIElement) -> ElementStats {
    let mut stats = ElementStats {
        total: 1,
        clickable: if element.clickable { 1 } else { 0 },
        with_text: if element.text.as_ref().map_or(false, |t| !t.trim().is_empty()) { 1 } else { 0 },
        with_id: if element.resource_id.is_some() { 1 } else { 0 },
    };

    for child in &element.children {
        let child_stats = count_elements(child);
        stats.total += child_stats.total;
        stats.clickable += child_stats.clickable;
        stats.with_text += child_stats.with_text;
        stats.with_id += child_stats.with_id;
    }

    stats
}
