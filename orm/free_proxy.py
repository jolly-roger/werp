from .base import *


class FreeProxy(DBase):
    __tablename__ = 'free_proxy'
    id = Column(BigInteger, primary_key = True)
    ip = Column(String)
    domain = Column(String)
    port = Column(String)
    country = Column(String)
    protocol = Column(String)
    http_status = Column(SmallInteger)
    http_status_reason = Column(String)
    
    def __init__(self, ip=None, domain=None, port=None, country=None, protocol=None, http_status=None,
        http_status_reason=None):
        self.ip = ip
        self.domain = domain
        self.port = port
        self.country = country
        self.protocol = protocol
        self.http_status = http_status
        self.http_status_reason = http_status_reason