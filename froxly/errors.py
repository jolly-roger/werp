class ProxyError(Exception):
    def __init__(self, reason=None, proxy=None):
        self.reason = reason
        self.proxy = proxy
    def __str__(self):
        return self.reason
