from werp.orm.base import *

class BotTask(DBase):
    __tablename__ = 'uatrains_bot_task'
    id = Column(postgresql.UUID, primary_key = True)
    data = Column(String, nullable=False)
    is_running = Column(Boolean, nullable=False)

    def __init__(self, data=None, is_running=False):
        self.data = data
        self.is_running = is_running