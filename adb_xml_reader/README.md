# ADB XML Reader

一个用 Rust 编写的独立工具，通过 ADB 连接读取 Android 设备的 UI 页面信息并解析为结构化数据。

## 功能特性

- 🔍 **UI 层次结构分析**: 完整解析 Android 应用的 UI 结构
- 📱 **多设备支持**: 自动检测连接的设备，支持指定特定设备
- 🎯 **智能搜索**: 按文本内容和资源ID查找UI元素
- 📸 **截图功能**: 同时保存当前屏幕截图用于对比分析
- 📊 **统计报告**: 提供UI元素的详细统计信息
- 💾 **数据导出**: 将UI层次结构保存为JSON格式便于后续处理
- 📞 **联系人导入**: 支持CSV和VCF格式的联系人批量导入
- 🤖 **自动化操作**: 小红书自动导航和关注功能
- 🎮 **智能点击**: 支持精确坐标点击和UI元素自动定位

## 安装要求

- Rust 1.70+
- ADB (Android Debug Bridge) 已安装并在 PATH 中
- Android 设备已启用 USB 调试并授权连接

## 编译运行

```bash
# 进入项目目录
cd d:\repositories\Flow_Farm\adb_xml_reader

# 编译项目
cargo build --release

# 运行程序
cargo run -- --help
```

## 使用方法

### 基本用法

```bash
# 获取默认设备的UI信息
cargo run

# 指定特定设备
cargo run -- --device emulator-5554

# 保存到指定文件
cargo run -- --output my_ui.json
```

### 高级功能

```bash
# 同时保存截图
cargo run -- --screenshot screen.png

# 在终端打印UI层次结构
cargo run -- --print

# 搜索包含特定文本的元素
cargo run -- --search "登录"

# 查找特定资源ID的元素
cargo run -- --find-id "com.example:id/login_button"

# 精确坐标点击
cargo run -- --click 500,800

# 组合使用多个功能
cargo run -- --print --search "按钮" --screenshot current.png
```

### 小红书自动化功能 ⭐ NEW

```bash
# 自动导航到通讯录页面（左上角菜单 -> 发现好友 -> 通讯录）
cargo run -- --auto-contact-flow

# 完整自动关注流程（导航 + 自动关注所有通讯录好友）
cargo run -- --auto-follow-contacts

# 使用编译后的程序（推荐）
target\release\adb_xml_reader.exe --auto-follow-contacts

# 指定设备执行自动关注
target\release\adb_xml_reader.exe --auto-follow-contacts --device "127.0.0.1:5555"
```

### 联系人导入功能

```bash
# VCF格式联系人导入（推荐）
cargo run -- --import-vcf contacts.csv

# 优化版联系人导入（避免Google登录）
cargo run -- --import-contacts-optimized contacts.csv

# 传统联系人导入
cargo run -- --import-contacts contacts.csv
```

## 输出格式

### JSON 结构
```json
{
  "tag": "android.widget.LinearLayout",
  "class": "android.widget.LinearLayout",
  "text": null,
  "content_desc": null,
  "resource_id": "com.example:id/main_layout",
  "package": "com.example.app",
  "bounds": "[0,0][1080,1920]",
  "clickable": false,
  "enabled": true,
  "focused": false,
  "selected": false,
  "children": [...]
}
```

### 终端输出示例
```
✅ 发现设备:
  ➤ emulator-5554

正在获取 UI 层次结构...
✅ 成功获取 UI XML (15234 字符)
✅ UI 层次结构已保存到: ui_hierarchy.json

📊 统计信息:
  总元素数: 127
  可点击元素: 23
  有文本元素: 45
  有ID元素: 67
```

## UI 元素属性说明

| 属性 | 类型 | 说明 |
|------|------|------|
| `tag` | String | XML标签名 (如 Button, TextView) |
| `class` | Option<String> | Android 类名 |
| `text` | Option<String> | 显示的文本内容 |
| `content_desc` | Option<String> | 无障碍描述 |
| `resource_id` | Option<String> | 资源ID标识符 |
| `package` | Option<String> | 所属应用包名 |
| `bounds` | Option<String> | 屏幕坐标边界 |
| `clickable` | bool | 是否可点击 |
| `enabled` | bool | 是否启用 |
| `focused` | bool | 是否获得焦点 |
| `selected` | bool | 是否被选中 |
| `children` | Vec<UIElement> | 子元素列表 |

## 应用场景

1. **UI 自动化测试**: 分析应用界面结构，编写自动化测试脚本
2. **应用逆向分析**: 了解第三方应用的界面组织结构
3. **辅助功能开发**: 为无障碍功能提供UI元素信息
4. **自动化脚本开发**: 为自动化操作提供精确的元素定位信息
5. **界面调试**: 帮助开发者理解复杂界面的层次结构

## 注意事项

⚠️ **重要提示**
- 确保目标设备屏幕处于活动状态（非锁屏状态）
- 某些系统界面可能需要更高权限才能获取完整信息
- 请遵守相关法律法规，仅用于合法的开发和测试目的
- 不同Android版本的UI结构可能存在差异

## 故障排除

### 常见问题

1. **未找到设备**
   ```bash
   adb devices  # 检查设备连接状态
   adb kill-server && adb start-server  # 重启ADB服务
   ```

2. **获取到空XML**
   - 确保设备屏幕未锁定
   - 尝试操作设备后重新获取
   - 检查应用是否有特殊保护机制

3. **权限被拒绝**
   - 在设备上重新授权ADB调试权限
   - 检查开发者选项是否正确启用

## 开发说明

本工具基于以下技术栈：
- **tokio**: 异步运行时
- **roxmltree**: XML 解析
- **serde**: 序列化和反序列化
- **clap**: 命令行参数解析
- **anyhow**: 错误处理

## 许可证

本项目为 Flow Farm 内部工具，仅供学习和开发使用。
