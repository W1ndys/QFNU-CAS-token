#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from core.get_ids_token import QfnuAuthClient
from utils.logger import log

# 加载 .env 文件
load_dotenv()


def main():
    """示例：如何使用认证客户端获取Token"""
    # 从环境变量读取账号密码，提供默认值
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    target_url = os.getenv(
        "TARGET_URL",
        "http://ids.qfnu.edu.cn/authserver/login?service=http://zhjw.qfnu.edu.cn/sso.jsp",
    )

    # 检查环境变量是否设置
    if not username or not password:
        log.error("错误：请设置环境变量 USERNAME 和 PASSWORD")
        log.error("可以在 .env 文件中设置或直接设置环境变量")
        return

    log.info("正在尝试获取认证重定向URL...")

    # 使用上下文管理器创建客户端实例，确保资源正确释放
    with QfnuAuthClient() as client:
        # 获取认证重定向URL
        redirect_url = client.get_redir_uri(
            username=username, password=password, redir_uri=target_url
        )

        # 处理认证结果
        if redirect_url:
            log.info(f"认证成功！重定向URL：{redirect_url}")
        else:
            log.error("认证失败，请检查账号密码是否正确或网络连接")


if __name__ == "__main__":
    main()
