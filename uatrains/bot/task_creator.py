import traceback
from werp import orm
from werp.orm import uatrains
from werp import nlog
from werp.uatrains.bot import task_drvs

try:
    conn = orm.null_engine.connect()
    ses = orm.sescls(bind=conn)
    
    for tid in range(0, 5000):
        bot_task = uatrains.BotTask()
        bot_task.data = str(tid)
        bot_task.drv = task_drvs.southwest
        ses.add(bot_task)
    #for tid in range(20000, 70000):
    #    bot_task = uatrains.BotTask()
    #    bot_task.data = str(tid)
    #    bot_task.drv = task_drvs.passengers
    #    ses.add(bot_task)
    ses.commit()
    ses.close()
    conn.close()
except:
    nlog.info('uatrains bot - task creator error', traceback.format_exc())