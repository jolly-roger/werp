from werp.orm.base import *

class BotTask(DBase):
    __tablename__ = 'uatrains_bot_task'
    id = Column(postgresql.UUID, primary_key = True)
    data = Column(String, nullable=False)
    status = Column(SmallInteger)
    http_status = Column(SmallInteger)
    drv = Column(SmallInteger)

    def __init__(self, data=None, status=None, http_status=None, drv=None):
        self.data = data
        self.status = status
        self.http_status = http_status
        self.drv = drv