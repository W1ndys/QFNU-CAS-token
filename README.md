# Qfnu CAS Token 获取工具

基于 [nakaii-002](https://github.com/nakaii-002) 的 [Qfnu_CAS_token](https://github.com/nakaii-002/Qfnu_CAS_token) 修改，这是一个用于获取曲阜师范大学统一认证系统(CAS)的 Token 工具，采用模块化设计和面向对象编程实现，使用 requests 的 Session 管理会话。删除了验证码识别功能，在理想情况下不需要验证码。

## 功能特点

- Session 会话管理
- 模块化设计，易于扩展和维护

## 安装依赖

```bash
pip install -r requirements.txt
```

## 文件结构

- `core/get_ids_token.py`: 主认证客户端类
- `utils/session_manager.py`: 会话管理模块
- `utils/logger.py`: 日志管理模块
- `zhjw.py`: 教务系统客户端类
- `example.py`: 使用示例

## 使用方法

1. 在项目根目录创建虚拟环境并安装依赖

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. 修改`.env`中的账号和密码

```env
USERNAME = 你的账号
PASSWORD = 你的密码
```

3. 运行示例

```bash
python zhjw.py
```

## 注意事项

- 本工具仅用于学习和研究目的
- 请勿用于非法用途或违反学校规定的行为
