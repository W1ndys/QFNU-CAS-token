import requests
from typing import Optional, Dict, Any
from utils.logger import log


class SessionManager:
    """统一的会话管理器"""

    def __init__(self, timeout: int = 30):
        """初始化会话管理器

        Args:
            timeout (int): 请求超时时间，默认30秒
        """
        self._session = None
        self.timeout = timeout
        self.default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
        }

    @property
    def session(self) -> requests.Session:
        """获取会话实例，懒加载模式"""
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update(self.default_headers)
        return self._session

    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> requests.Response:
        """发送GET请求

        Args:
            url (str): 请求URL
            headers (dict, optional): 额外的请求头
            params (dict, optional): 请求参数
            **kwargs: 其他requests参数

        Returns:
            requests.Response: 响应对象
        """
        request_headers = self.default_headers.copy()
        if headers:
            request_headers.update(headers)

        log.debug(f"GET请求: {url}")

        return self.session.get(
            url=url,
            headers=request_headers,
            params=params,
            timeout=self.timeout,
            **kwargs,
        )

    def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> requests.Response:
        """发送POST请求

        Args:
            url (str): 请求URL
            data (dict, optional): 请求数据
            headers (dict, optional): 额外的请求头
            **kwargs: 其他requests参数

        Returns:
            requests.Response: 响应对象
        """
        request_headers = self.default_headers.copy()
        if headers:
            request_headers.update(headers)

        log.debug(f"POST请求: {url}")

        return self.session.post(
            url=url, data=data, headers=request_headers, timeout=self.timeout, **kwargs
        )

    def get_cookies(self) -> Dict[str, str]:
        """获取当前会话的Cookie

        Returns:
            dict: Cookie字典
        """
        return self.session.cookies.get_dict()

    def set_cookie(self, name: str, value: str, domain: Optional[str] = None):
        """设置Cookie

        Args:
            name (str): Cookie名称
            value (str): Cookie值
            domain (str, optional): Cookie域名
        """
        self.session.cookies.set(name, value, domain=domain)

    def clear_cookies(self):
        """清空所有Cookie"""
        self.session.cookies.clear()

    def update_headers(self, headers: Dict[str, str]):
        """更新默认请求头

        Args:
            headers (dict): 要更新的请求头
        """
        self.default_headers.update(headers)
        if self._session:
            self._session.headers.update(headers)

    def close(self):
        """关闭会话"""
        if self._session:
            self._session.close()
            self._session = None

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


# 全局会话管理器实例
_global_session_manager = None


def get_global_session_manager() -> SessionManager:
    """获取全局会话管理器实例

    Returns:
        SessionManager: 全局会话管理器
    """
    global _global_session_manager
    if _global_session_manager is None:
        _global_session_manager = SessionManager()
    return _global_session_manager


def reset_global_session_manager():
    """重置全局会话管理器"""
    global _global_session_manager
    if _global_session_manager:
        _global_session_manager.close()
    _global_session_manager = None
