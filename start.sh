#!/bin/bash
# Flow Farm 快速启动脚本
# 自动检测并启动Flow Farm应用程序

echo ""
echo "=========================================="
echo "       Flow Farm 启动助手 v1.0"
echo "=========================================="
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "[错误] 未检测到Python环境"
        echo "请先安装Python 3.8或更高版本"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "[信息] Python环境检测通过"

# 检查是否在正确目录
if [ ! -f "src/main.py" ]; then
    echo "[错误] 未找到主程序文件"
    echo "请确保在Flow_Farm项目根目录运行此脚本"
    exit 1
fi

echo "[信息] 程序文件检测通过"

# 检查虚拟环境
if [ -d "venv" ]; then
    echo "[信息] 检测到虚拟环境，正在激活..."
    source venv/bin/activate
    echo "[信息] 虚拟环境已激活"
else
    echo "[警告] 未检测到虚拟环境"
    echo "建议创建虚拟环境以避免依赖冲突"
fi

# 进入源代码目录
cd src

echo ""
echo "请选择启动模式:"
echo "[1] GUI模式 (图形界面，推荐)"
echo "[2] 控制台模式 (命令行界面)"
echo "[3] 调试模式 (开发调试)"
echo "[0] 退出"
echo ""

read -p "请输入选择 (1-3): " choice

case $choice in
    1)
        echo ""
        echo "[启动] GUI模式启动中..."
        $PYTHON_CMD main.py --gui
        ;;
    2)
        echo ""
        echo "[启动] 控制台模式启动中..."
        $PYTHON_CMD main.py --console
        ;;
    3)
        echo ""
        echo "[启动] 调试模式启动中..."
        $PYTHON_CMD main.py --debug --gui
        ;;
    0)
        echo ""
        echo "感谢使用Flow Farm！"
        exit 0
        ;;
    *)
        echo ""
        echo "[错误] 无效选择，请输入1-3之间的数字"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "          程序运行结束"
echo "=========================================="
