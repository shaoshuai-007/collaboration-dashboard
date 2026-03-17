# Python编码规范完整指南

**来源**: PEP 8 官方规范
**整理人**: 🌿 南乔
**更新时间**: 2026-03-16

---

## 一、代码布局

### 1.1 缩进

- 使用 **4个空格** 进行缩进（不要使用Tab）
- 续行应与括号内元素对齐，或使用悬挂缩进

```python
# ✅ 正确：与左括号对齐
foo = long_function(var_one, var_two,
                     var_three, var_four)

# ✅ 正确：悬挂缩进
def long_function(var_one, var_two, var_three,
                  var_four):
    print(var_one)

# ❌ 错误：参数不与左括号对齐
foo = long_function(var_one, var_two,
    var_three, var_four)
```

### 1.2 行宽

- 最大行宽 **79字符**
- 文档字符串/注释限制为 **72字符**
- 使用反斜杠 `\` 进行换行

```python
# ✅ 正确
with open('/path/to/file', 'r') as file_one, \
        open('/path/to/other', 'w') as file_two:
    file_two.write(file_one.read())
```

### 1.3 空行

- 顶层函数和类定义之间：**2个空行**
- 类内方法定义之间：**1个空行**

```python
class MyClass:

    def method_one(self):
        pass

    def method_two(self):
        pass


def top_level_function():
    pass
```

---

## 二、导入

### 2.1 导入顺序

1. 标准库
2. 第三方库
3. 本地应用/库

```python
# ✅ 正确
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd

from myproject import mymodule
from myproject.mypackage import myclass
```

### 2.2 导入规范

- 避免使用 `from module import *`
- 每个导入单独一行

```python
# ✅ 正确
import os
import sys

# ❌ 错误
import os, sys

# ❌ 错误
from module import *
```

---

## 三、命名规范

### 3.1 命名风格

| 类型 | 风格 | 示例 |
|------|------|------|
| 模块 | 小写下划线 | `my_module.py` |
| 包 | 小写 | `mypackage` |
| 类 | 大驼峰 | `MyClass` |
| 异常 | 大驼峰+Error后缀 | `MyError` |
| 函数 | 小写下划线 | `my_function()` |
| 方法 | 小写下划线 | `my_method()` |
| 变量 | 小写下划线 | `my_variable` |
| 常量 | 大写下划线 | `MAX_SIZE` |

### 3.2 命名示例

```python
# ✅ 正确
class UserController:
    MAX_RETRY_COUNT = 3

    def get_user_info(self, user_id: int) -> dict:
        user_name = "张三"
        return {"name": user_name}

# ❌ 错误
class usercontroller:  # 类名应大驼峰
    maxRetryCount = 3  # 常量应大写下划线

    def GetUserInfo(self):  # 方法应小写下划线
        UserName = "张三"  # 变量应小写下划线
```

---

## 四、注释

### 4.1 块注释

- 每行以 `#` 开头，后跟一个空格
- 段落之间用空行分隔

```python
# 这是块注释的第一行
# 这是块注释的第二行
#
# 这是新段落
```

### 4.2 行内注释

- 与代码至少间隔 **2个空格**
- 以 `#` 开头，后跟一个空格

```python
x = x + 1  # 补偿边界条件
```

### 4.3 文档字符串（Docstring）

```python
def calculate_user_value(user_id: int, weight: float = 1.0) -> float:
    """
    计算用户价值分数

    Args:
        user_id: 用户ID
        weight: 权重系数，默认为1.0

    Returns:
        用户价值分数，范围0-100

    Raises:
        ValueError: 当用户ID不存在时抛出
        TypeError: 当参数类型错误时抛出

    Examples:
        >>> calculate_user_value(1001)
        85.5
        >>> calculate_user_value(1001, weight=1.5)
        128.25
    """
    if not isinstance(user_id, int):
        raise TypeError("user_id must be int")

    # 计算逻辑...
    return 85.5
```

---

## 五、类型注解

### 5.1 函数类型注解

```python
from typing import List, Dict, Optional, Union

def get_users(
    age: int,
    name: Optional[str] = None
) -> List[Dict[str, Union[str, int]]]:
    """
    获取用户列表

    Args:
        age: 年龄筛选条件
        name: 姓名筛选条件（可选）

    Returns:
        用户列表，每个用户包含name和age字段
    """
    users = [
        {"name": "张三", "age": 25},
        {"name": "李四", "age": 30}
    ]
    return users
```

### 5.2 类属性类型注解

```python
class User:
    """用户模型"""

    def __init__(self, user_id: int, name: str):
        self.user_id: int = user_id
        self.name: str = name
        self.age: Optional[int] = None
        self.tags: List[str] = []
```

---

## 六、代码风格

### 6.1 字符串引号

- 单引号和双引号都可以，保持一致即可
- 三引号用于多行字符串

```python
# ✅ 正确
single = '单引号字符串'
double = "双引号字符串"
multi = """
多行
字符串
"""
```

### 6.2 空格使用

```python
# ✅ 正确
spam(ham[1], {eggs: 2})

# ❌ 错误
spam( ham[ 1 ], { eggs: 2 } )

# ✅ 正确
if x == 4:
    print(x, y)
    x, y = y, x

# ❌ 错误
if x==4:
    print(x , y)
    x , y = y , x
```

### 6.3 比较运算

```python
# ✅ 正确：与None比较用 is
if foo is None:

# ❌ 错误
if foo == None:

# ✅ 正确：检查是否为空
if not my_list:

# ❌ 错误
if len(my_list) == 0:
```

---

## 七、异常处理

### 7.1 异常捕获

```python
# ✅ 正确：指定具体异常
try:
    value = my_dict[key]
except KeyError:
    value = default_value

# ❌ 错误：裸异常
try:
    value = my_dict[key]
except:
    value = default_value
```

### 7.2 异常抛出

```python
# ✅ 正确：抛出具体异常
if user_id <= 0:
    raise ValueError("user_id must be positive")

# ❌ 错误：抛出通用异常
if user_id <= 0:
    raise Exception("Invalid user_id")
```

---

## 八、最佳实践

### 8.1 函数设计

```python
# ✅ 正确：函数职责单一
def validate_user(user_id: int) -> bool:
    """验证用户是否存在"""
    return user_id > 0

def get_user_info(user_id: int) -> dict:
    """获取用户信息"""
    if not validate_user(user_id):
        raise ValueError("Invalid user_id")
    # 查询逻辑...

# ❌ 错误：函数职责过多
def validate_and_get_user(user_id: int) -> dict:
    """验证用户并获取信息"""  # 职责不清晰
    pass
```

### 8.2 避免魔法数字

```python
# ✅ 正确
MAX_RETRY_COUNT = 3
TIMEOUT_SECONDS = 30

for i in range(MAX_RETRY_COUNT):
    # 重试逻辑...

# ❌ 错误
for i in range(3):  # 3是什么意思？
    pass
```

---

## 九、代码检查工具

### 9.1 Pylint

```bash
# 安装
pip install pylint

# 检查代码
pylint my_module.py

# 生成配置文件
pylint --generate-rcfile > .pylintrc
```

### 9.2 Black（自动格式化）

```bash
# 安装
pip install black

# 格式化代码
black my_module.py

# 检查模式（不修改文件）
black --check my_module.py
```

### 9.3 isort（导入排序）

```bash
# 安装
pip install isort

# 排序导入
isort my_module.py
```

---

## 十、检查清单

- [ ] 使用4个空格缩进
- [ ] 行宽不超过79字符
- [ ] 导入按标准库/第三方/本地分组
- [ ] 类名使用大驼峰
- [ ] 函数/方法名使用小写下划线
- [ ] 常量使用大写下划线
- [ ] 函数有完整的文档字符串
- [ ] 使用类型注解
- [ ] 与None比较使用 `is`
- [ ] 异常捕获指定具体类型

---

*整理人: 🌿 南乔*
*参考: PEP 8 官方文档*
