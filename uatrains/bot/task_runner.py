import traceback
from urllib.error import HTTPError
from werp import orm
from werp.orm import uatrains
from werp import nlog
from werp.uatrains.engine import drv
from werp.uatrains.bot import task_status
from werp.uatrains.bot import task_drvs

try:
    conn = orm.q_engine.connect()
    ses = orm.sescls(bind=conn)
    tasks = ses.query(uatrains.BotTask).filter(uatrains.BotTask.status == None).limit(32).all()
    task_ids = []
    for t in tasks:
        task_ids.append(t.id)
    with multiprocessing.Pool(processes=32) as ppool:
        ppool.map(run_task, [task_id for task_id in task_ids])
    ses.close()
    conn.close()
except:
    nlog.info('uatrains bot - task runner error', traceback.format_exc())
    
def run_task(task_id):
    conn = orm.null_engine.connect()
    ses = orm.sescls(bind=conn)
    task = None
    try:
        task = ses.query(uatrains.BotTask).filter(uatrains.BotTask.id == task_id).one()
    except:
        nlog.info('uatrains bot - task runner error', traceback.format_exc())
    if task is not None:
        task.status = task_status.running
        sess.commit()
        try:
            if task.drv == task_drvs.southwest:
                drv.southwest.get_train_data(task.data)
            elif task.drv == task_drvs.passengers:
                drv.passengers.get_train_data(task.data)
        except HTTPError as e:
            task.http_status = e.code
        except:
            nlog.info('uatrains bot - task runner error', traceback.format_exc())
        if task.http_status is None:
            task.http_status = 200
        task.status = task_status.completed
        ses.commit()
    ses.close()
    conn.close()