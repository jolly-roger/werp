class ProxyError(Exception):
    def __init__(self, proxy=None, base_exception=None):
        self.proxy = proxy
        self.base_exception = base_exception
    def __str__(self):
        return str(self.base_exception)
