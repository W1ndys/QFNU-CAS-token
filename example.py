#!/usr/bin/env python3
import os
import re
from core.get_ids_token import QfnuAuthClient
from utils.logger import logger


class ZhjwClient:
    """曲阜师范大学教务系统客户端"""

    def __init__(self):
        self.auth_client = QfnuAuthClient()
        self.base_url = "http://zhjw.qfnu.edu.cn"

        # 设置更完整的浏览器请求头
        self.auth_client.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            }
        )

    def login(self, username, password):
        """登录教务系统"""
        target_url = "http://ids.qfnu.edu.cn/authserver/login?service=http://zhjw.qfnu.edu.cn/sso.jsp"

        logger.info("正在获取认证重定向URL...")

        # 第一步：获取认证重定向URL
        redirect_url = self.auth_client.get_redir_uri(
            username=username, password=password, redir_uri=target_url
        )

        if not redirect_url:
            logger.error("获取认证重定向URL失败")
            return False

        logger.info(f"获取到重定向URL：{redirect_url}")

        # 第二步：访问重定向URL完成SSO登录
        return self._complete_sso_login(redirect_url)

    def _complete_sso_login(self, redirect_url):
        """完成SSO登录流程"""
        try:
            # 访问重定向URL（包含ticket）
            response = self.auth_client.get(redirect_url, allow_redirects=True)

            logger.info(f"访问重定向URL状态码：{response.status_code}")
            logger.debug(f"访问重定向URL响应头：{dict(response.headers)}")

            logger.info("正在访问SSO重定向URL...")
            sso_url = "http://zhjw.qfnu.edu.cn/sso.jsp"
            response = self.auth_client.get(sso_url, allow_redirects=True)

            logger.info(f"访问sso.jsp状态码：{response.status_code}")
            logger.debug(f"访问sso.jsp响应头：{dict(response.headers)}")

            # 访问教务首页
            main_url = "http://zhjw.qfnu.edu.cn/jsxsd/framework/xsMain.jsp"
            response = self.auth_client.get(main_url, allow_redirects=True)
            logger.info(f"访问教务首页状态码：{response.status_code}")
            logger.debug(f"访问教务首页响应头：{dict(response.headers)}")

            if self._check_login_success(response.text):
                logger.info("教务系统登录成功！")
                return True
            else:
                logger.error("教务系统登录失败！")
                return False

        except Exception as e:
            logger.error(f"SSO登录过程中发生错误：{e}")
            return False

    def _check_login_success(self, html_content):
        """检查登录是否成功"""
        # 查找学生姓名或其他登录成功的标识
        patterns = [
            r"教学一体化服务平台",  # 页面标题
            r"个人中心",  # 个人中心标识
            r"我的桌面",  # 菜单项
            r"学籍成绩",  # 菜单项
            r'<span class="glyphicon-class">([^<退出]+)</span>',  # 查找姓名（排除"退出"）
        ]

        for pattern in patterns:
            match = re.search(pattern, html_content)
            if match:
                logger.info(f"登录验证成功，匹配到：{match.group()}")
                return True

        logger.error("未找到登录成功的标识")
        return False


def main():
    """示例：如何使用教务系统客户端"""
    # 从环境变量读取账号密码
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    # 检查环境变量是否设置
    if not username or not password:
        logger.error("错误：请设置环境变量 USERNAME 和 PASSWORD")
        logger.error("可以在 .env 文件中设置或直接设置环境变量")
        return

    # 创建教务系统客户端
    client = ZhjwClient()

    # 登录教务系统
    if client.login(username, password):
        # 打印cookie
        logger.info(client.auth_client.session.cookies)

    else:
        logger.error("登录失败，请检查账号密码是否正确或网络连接")


if __name__ == "__main__":
    main()
