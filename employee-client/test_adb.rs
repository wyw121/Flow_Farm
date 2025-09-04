use std::process::Command;

fn main() {
    // 测试雷电模拟器ADB路径
    let adb_path = r"D:\leidian\LDPlayer9\adb.exe";

    println!("正在测试ADB路径: {}", adb_path);

    match Command::new(adb_path)
        .arg("version")
        .output()
    {
        Ok(output) => {
            if output.status.success() {
                let version_info = String::from_utf8_lossy(&output.stdout);
                println!("✅ ADB测试成功!");
                println!("版本信息: {}", version_info);
            } else {
                let error_info = String::from_utf8_lossy(&output.stderr);
                println!("❌ ADB命令执行失败");
                println!("错误信息: {}", error_info);
            }
        }
        Err(e) => {
            println!("❌ 无法执行ADB命令: {}", e);
        }
    }
}
