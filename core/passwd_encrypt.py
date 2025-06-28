import random
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from utils.logger import log


class PasswordEncryptor:
    """密码加密类，处理AES加密相关功能"""

    def __init__(self):
        """初始化加密器"""
        self.aes_chars = "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678"
        self.aes_chars_len = len(self.aes_chars)

    def random_string(self, length):
        """生成指定长度的随机字符串

        Args:
            length (int): 字符串长度

        Returns:
            str: 随机字符串
        """
        res = ""
        for _ in range(length):
            res += self.aes_chars[random.randint(0, self.aes_chars_len - 1)]
        return res

    def get_aes_string(self, data, key, iv):
        """AES加密数据

        Args:
            data (str): 要加密的数据
            key (str): 加密密钥
            iv (str): 初始化向量

        Returns:
            str: Base64编码的加密结果
        """
        data = data.strip()
        data = data.encode("utf-8")
        key_encoded = key.encode("utf-8")
        iv_encoded = iv.encode("utf-8")
        backend = default_backend()
        cipher = Cipher(
            algorithms.AES(key_encoded), modes.CBC(iv_encoded), backend=backend
        )

        # 修复block_size类型错误，使用固定的128位(16字节)块大小
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()

        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        encrypted_base64 = base64.b64encode(encrypted_data).decode("utf-8")

        return encrypted_base64

    def encrypt_password(self, passwd, salt):
        """加密密码，添加随机前缀

        Args:
            passwd (str): 原始密码
            salt (str): 加密盐值

        Returns:
            str: 加密后的密码
        """
        return self.get_aes_string(
            self.random_string(64) + passwd, salt, self.random_string(16)
        )


if __name__ == "__main__":
    encryptor = PasswordEncryptor()
    log.info(encryptor.encrypt_password("", "LqqQdC3a3DIin1P1"))
