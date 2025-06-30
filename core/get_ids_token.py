from bs4 import BeautifulSoup, Tag
import time
from typing import Optional
from core.passwd_encrypt import PasswordEncryptor
from utils.session_manager import SessionManager
from utils.logger import log


class QfnuAuthClient(SessionManager):
    """曲阜师范大学统一认证客户端，继承SessionManager"""

    def __init__(self, timeout: int = 30):
        """初始化客户端

        Args:
            timeout (int): 请求超时时间，默认30秒
        """
        super().__init__(timeout=timeout)
        self.encryptor = PasswordEncryptor()

    def get_salt_and_execution(self, redir_uri):
        """获取密码加密盐值和execution参数

        Args:
            redir_uri (str): 重定向URI

        Returns:
            tuple: (salt_data, execution_data) 或在失败时 (None, None)
        """

        try:
            response = self.get(url=redir_uri)
            soup = BeautifulSoup(response.text, "html.parser")

            # 修复BeautifulSoup的使用方法，添加正确的类型检查
            execution_element = soup.find(id="execution")
            salt_element = soup.find(id="pwdEncryptSalt")

            if execution_element and isinstance(execution_element, Tag):
                execution_data = execution_element.get("value")
                if salt_element and isinstance(salt_element, Tag):
                    salt_data = salt_element.get("value")
                    return salt_data, execution_data

            log.error("未能找到加密盐或execution参数")
            return None, None
        except Exception as e:
            log.error(f"获取加密盐和execution失败: {str(e)}")
            return None, None

    def check_need_captcha(self, username):
        """检查是否需要验证码

        Args:
            username (str): 用户名

        Returns:
            bool: 是否需要验证码
        """
        uri = "http://ids.qfnu.edu.cn/authserver/checkNeedCaptcha.htl"
        params = {"username": username, "_": int(round(time.time() * 1000))}

        try:
            res = self.get(url=uri, params=params)
            return "true" in res.text
        except Exception as e:
            log.error(f"检查是否需要验证码失败: {str(e)}")
            return True  # 出错时默认返回需要验证码

    def get_captcha(self):
        """获取验证码图像

        Returns:
            bytes: 验证码图片的字节数据，失败时返回None
        """
        uri = f"http://ids.qfnu.edu.cn/authserver/getCaptcha.htl?{int(round(time.time() * 1000))}"

        try:
            res = self.get(url=uri)
            return res.content
        except Exception as e:
            log.error(f"获取验证码失败: {str(e)}")
            return None

    def get_redir_uri(self, username, password, redir_uri):
        """获取认证token

        Args:
            username (str): 用户名
            password (str): 密码
            redir_uri (str): 重定向URI

        Returns:
            str: 带有ticket的链接，失败时返回None
        """
        # 获取盐值和execution
        salt, execution_data = self.get_salt_and_execution(redir_uri)
        if not salt or not execution_data:
            return None

        # 验证码处理
        # 备注：理想情况下不需要验证码
        # 修改版已删除验证码识别功能
        # cap_res = ""
        # log.info("正在检查是否需要验证码")
        # if self.check_need_captcha(username):
        #     log.info("需要验证码，正在尝试获取验证码")
        #     try:
        #         cap_pic = self.get_captcha()
        #         if cap_pic:
        #             cap_res = ""
        #             if isinstance(cap_res, str):
        #                 cap_res = cap_res.lower()
        #                 log.info(f"验证码识别结果: {cap_res}")
        #     except Exception as e:
        #         log.error(f"获取或识别验证码失败: {str(e)}")
        # else:
        #     log.info("无需验证码，尝试获取Token")

        # 加密密码
        enc_passwd = self.encryptor.encrypt_password(password, salt)

        # 准备提交数据
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        data = {
            "username": username,
            "password": enc_passwd,
            # "captcha": cap_res,
            "_eventId": "submit",
            "cllt": "userNameLogin",
            "dllt": "generalLogin",
            "lt": "",
            "execution": execution_data,
        }

        # 提交认证请求
        try:
            res = self.post(
                url=redir_uri, headers=headers, data=data, allow_redirects=False
            )

            if "Location" in res.headers:
                return res.headers["Location"]
            else:
                log.error("认证失败，未获得重定向链接")
                return None
        except Exception as e:
            log.error(f"认证过程发生错误: {str(e)}")
            return None

    def get_auth_cookie(self):
        """获取会话中的认证Cookie

        Returns:
            dict: Cookie字典
        """
        return self.get_cookies()


if __name__ == "__main__":
    # 使用上下文管理器确保资源正确释放
    with QfnuAuthClient() as client:
        redirect_url = client.get_redir_uri(
            "your_account",
            "your_password",
            "http://ids.qfnu.edu.cn/authserver/login?service=http://zhjw.qfnu.edu.cn/jsxsd/framework/xsMain.jsp",
        )

        if redirect_url:
            log.info(f"认证成功，重定向链接: {redirect_url}")
            log.info(f"Cookie: {client.get_auth_cookie()}")
        else:
            log.error("认证失败")
