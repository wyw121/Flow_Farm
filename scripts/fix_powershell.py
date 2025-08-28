#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PowerShell 问题诊断和修复工具

Author: Flow Farm Team
Date: 2025-08-28
Description: 自动诊断和修复VS Code PowerShell扩展问题
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def run_command(command, shell=True):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def check_powershell_versions():
    """检查PowerShell版本"""
    print("🔍 检查PowerShell版本...")
    
    # 检查Windows PowerShell 5.1
    success, stdout, stderr = run_command('powershell.exe -Command "$PSVersionTable.PSVersion"')
    if success:
        print(f"✅ Windows PowerShell 5.1: 可用")
        print(f"   版本信息: {stdout.strip()}")
    else:
        print(f"❌ Windows PowerShell 5.1: 不可用")
    
    # 检查PowerShell 7
    ps7_path = r"C:\Program Files\PowerShell\7\pwsh.exe"
    if os.path.exists(ps7_path):
        success, stdout, stderr = run_command(f'"{ps7_path}" -Command "$PSVersionTable.PSVersion"')
        if success:
            print(f"✅ PowerShell 7: 可用")
            print(f"   版本信息: {stdout.strip()}")
        else:
            print(f"⚠️  PowerShell 7: 已安装但可能有问题")
    else:
        print(f"❌ PowerShell 7: 未安装")


def check_vscode_extensions():
    """检查VS Code扩展"""
    print("\n🔍 检查VS Code扩展...")
    
    success, stdout, stderr = run_command('code --list-extensions')
    if success:
        extensions = stdout.strip().split('\n')
        powershell_ext = [ext for ext in extensions if 'powershell' in ext.lower()]
        
        if powershell_ext:
            print(f"✅ PowerShell扩展已安装: {', '.join(powershell_ext)}")
        else:
            print(f"❌ PowerShell扩展未安装")
    else:
        print(f"❌ 无法检查VS Code扩展")


def check_execution_policy():
    """检查执行策略"""
    print("\n🔍 检查PowerShell执行策略...")
    
    success, stdout, stderr = run_command('powershell.exe -Command "Get-ExecutionPolicy -List"')
    if success:
        print(f"✅ 执行策略:")
        print(f"   {stdout.strip()}")
    else:
        print(f"❌ 无法检查执行策略")


def fix_execution_policy():
    """修复执行策略"""
    print("\n🔧 修复执行策略...")
    
    success, stdout, stderr = run_command(
        'powershell.exe -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"'
    )
    if success:
        print(f"✅ 执行策略已修复")
    else:
        print(f"❌ 修复执行策略失败: {stderr}")


def clean_vscode_cache():
    """清理VS Code缓存"""
    print("\n🔧 清理VS Code缓存...")
    
    appdata = os.environ.get('APPDATA', '')
    if not appdata:
        print("❌ 无法获取APPDATA路径")
        return
    
    cache_paths = [
        os.path.join(appdata, 'Code', 'logs'),
        os.path.join(appdata, 'Code', 'User', 'globalStorage', 'ms-vscode.powershell')
    ]
    
    for cache_path in cache_paths:
        if os.path.exists(cache_path):
            try:
                import shutil
                shutil.rmtree(cache_path)
                print(f"✅ 已清理: {cache_path}")
            except Exception as e:
                print(f"⚠️  清理失败: {cache_path} - {e}")
        else:
            print(f"ℹ️  不存在: {cache_path}")


def create_vscode_settings():
    """创建VS Code设置"""
    print("\n🔧 创建VS Code设置...")
    
    workspace_path = Path(__file__).parent.parent
    vscode_dir = workspace_path / '.vscode'
    vscode_dir.mkdir(exist_ok=True)
    
    settings = {
        "powershell.powerShellDefaultVersion": "Windows PowerShell (x86)",
        "terminal.integrated.defaultProfile.windows": "PowerShell",
        "terminal.integrated.profiles.windows": {
            "PowerShell": {
                "source": "PowerShell",
                "icon": "terminal-powershell"
            },
            "Windows PowerShell": {
                "path": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
                "args": [],
                "icon": "terminal-powershell"
            }
        }
    }
    
    settings_file = vscode_dir / 'settings.json'
    try:
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        print(f"✅ VS Code设置已创建: {settings_file}")
    except Exception as e:
        print(f"❌ 创建VS Code设置失败: {e}")


def test_flow_farm():
    """测试Flow Farm应用"""
    print("\n🔍 测试Flow Farm应用...")
    
    workspace_path = Path(__file__).parent.parent
    main_script = workspace_path / 'src' / 'main.py'
    
    if not main_script.exists():
        print(f"❌ 主脚本不存在: {main_script}")
        return
    
    # 测试帮助信息
    success, stdout, stderr = run_command(f'python "{main_script}" --help')
    if success:
        print(f"✅ Flow Farm应用正常工作")
    else:
        print(f"❌ Flow Farm应用有问题: {stderr}")


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 Flow Farm PowerShell 问题诊断和修复工具")
    print("=" * 60)
    
    # 诊断阶段
    check_powershell_versions()
    check_vscode_extensions()
    check_execution_policy()
    test_flow_farm()
    
    print("\n" + "=" * 60)
    print("🔧 开始修复...")
    print("=" * 60)
    
    # 修复阶段
    fix_execution_policy()
    clean_vscode_cache()
    create_vscode_settings()
    
    print("\n" + "=" * 60)
    print("✅ 修复完成！")
    print("=" * 60)
    print("\n💡 建议:")
    print("1. 重启VS Code")
    print("2. 重新加载窗口 (Ctrl+Shift+P -> Developer: Reload Window)")
    print("3. 如果问题仍然存在，请卸载并重新安装PowerShell扩展")
    print("4. 考虑使用Windows PowerShell 5.1作为默认终端")


if __name__ == "__main__":
    main()
