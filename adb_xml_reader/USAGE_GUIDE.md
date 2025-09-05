# ADB XML Reader 使用指南

这是一个用 Rust 编写的独立工具，可以通过 ADB 读取 Android 设备的 UI XML 页面信息，专门为雷电模拟器等虚拟机设备优化。

## ✨ 功能特性

- 🔍 读取设备 UI 层次结构并保存为 JSON 格式
- 📱 同时截取屏幕截图
- 🔎 搜索包含指定文本的 UI 元素
- 🎯 查找具有特定资源ID的元素
- 📊 提供详细的统计信息
- 🌐 支持多设备连接

## 🚀 快速开始

### 1. 编译项目

```bash
cargo build --release
```

### 2. 基础用法

```bash
# 获取帮助信息
./target/release/adb_xml_reader.exe --help

# 读取默认设备的UI信息
./target/release/adb_xml_reader.exe

# 指定设备并保存到自定义文件
./target/release/adb_xml_reader.exe --device "127.0.0.1:5555" --output app_ui.json --screenshot app_screen.png
```

### 3. 高级搜索

```bash
# 搜索包含特定文本的元素
./target/release/adb_xml_reader.exe --search "关注"

# 查找具有特定资源ID的元素
./target/release/adb_xml_reader.exe --find-id "com.example.app:id/button"

# 在终端直接查看UI层次结构
./target/release/adb_xml_reader.exe --print
```

## 📋 命令行参数

| 参数 | 简写 | 描述 | 默认值 |
|------|------|------|--------|
| `--device` | `-d` | 指定设备ID | 自动选择第一个设备 |
| `--output` | `-o` | JSON输出文件路径 | `ui_hierarchy.json` |
| `--screenshot` | `-s` | 截图保存路径 | `screenshot.png` |
| `--search` |  | 搜索包含指定文本的元素 |  |
| `--find-id` |  | 查找具有指定资源ID的元素 |  |
| `--print` | `-p` | 在终端打印UI层次结构 |  |

## 🎯 实际应用示例

### 示例1: 分析小红书应用

```bash
# 获取小红书的完整UI信息
./target/release/adb_xml_reader.exe --device "127.0.0.1:5555" --output xiaohongshu_ui.json --screenshot xiaohongshu_screen.png

# 搜索关注按钮
./target/release/adb_xml_reader.exe --device "127.0.0.1:5555" --search "关注"

# 查找发布按钮
./target/release/adb_xml_reader.exe --device "127.0.0.1:5555" --search "发布"
```

### 示例2: 多设备操作

```bash
# 查看所有连接的设备
"D:\leidian\LDPlayer9\adb.exe" devices

# 操作不同的设备
./target/release/adb_xml_reader.exe --device "127.0.0.1:5555" --output device1_ui.json
./target/release/adb_xml_reader.exe --device "127.0.0.1:5557" --output device2_ui.json
./target/release/adb_xml_reader.exe --device "emulator-5554" --output device3_ui.json
```

## 📊 输出说明

### JSON 文件结构

生成的 JSON 文件包含完整的 UI 元素层次结构，每个元素包含：

```json
{
  "tag": "android.widget.Button",
  "class": "android.widget.Button",
  "text": "关注",
  "content_desc": "关注按钮",
  "resource_id": "com.xingin.xhs:id/follow_button",
  "package": "com.xingin.xhs",
  "bounds": "[100,200][300,250]",
  "clickable": true,
  "enabled": true,
  "focused": false,
  "selected": false,
  "children": []
}
```

### 统计信息

工具会自动统计并显示：

- 📊 总元素数：页面中所有UI元素的数量
- 👆 可点击元素：可以被点击的元素数量
- 📝 有文本元素：包含文本内容的元素数量
- 🏷️ 有ID元素：具有资源ID的元素数量

## 🔧 技术配置

### ADB 路径配置

工具已经配置为使用雷电模拟器的 ADB：

```rust
const ADB_PATH: &str = r"D:\leidian\LDPlayer9\adb.exe";
```

如需更改 ADB 路径，请修改 `src/lib.rs` 文件中的 `ADB_PATH` 常量。

### 支持的设备类型

- ✅ 雷电模拟器 (LDPlayer)
- ✅ 夜神模拟器 (Nox)
- ✅ Android 物理设备
- ✅ Android Studio AVD 模拟器
- ✅ 其他支持 ADB 的 Android 设备

## 🐛 常见问题

### 1. 设备连接问题

```bash
# 检查设备连接
"D:\leidian\LDPlayer9\adb.exe" devices

# 如果没有设备，请确保：
# - 虚拟机正在运行
# - 开启了 ADB 调试模式
# - 防火墙没有阻止连接
```

### 2. 权限问题

确保在 Android 设备/虚拟机中：
- 开启"开发者选项"
- 启用"USB调试"
- 允许 ADB 连接

### 3. 获取空白 XML

如果获取到空白内容，可能是因为：
- 设备屏幕处于锁定状态
- 应用没有正确启动
- 需要等待应用完全加载

## 💡 使用技巧

1. **批量分析**：使用脚本调用工具，批量分析多个应用的UI结构
2. **自动化测试**：结合 JSON 输出编写自动化点击脚本
3. **UI监控**：定期获取UI信息，监控应用界面变化
4. **元素定位**：使用搜索功能快速定位目标元素的坐标和ID

## 🔗 相关资源

- 项目源码：`D:\repositories\Flow_Farm\adb_xml_reader\`
- ADB 官方文档：[Android Debug Bridge](https://developer.android.com/studio/command-line/adb)
- Rust 项目文档：[The Rust Programming Language](https://doc.rust-lang.org/)

## 📄 许可证

本工具是 Flow Farm 项目的一部分，仅供学习和研究使用。
