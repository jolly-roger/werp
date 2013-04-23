class ProxyError(Exception):
    def __init__(self, base_exception=None, proxy=None):
        self.base_exception = base_exception
        self.proxy = proxy
    def __str__(self):
        return str(self.base_exception)
