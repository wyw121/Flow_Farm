
import sys
import os
import marshal
import types

# 加载编译后的字节码
with open("smart_follow_compiled.pyc", "rb") as f:
    f.read(16)  # 跳过头部
    code = marshal.load(f)

# 执行代码
exec(code)
