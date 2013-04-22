import multiprocessing
import traceback
import threading
from urllib.error import *
from werp import orm
from werp.orm import uatrains
from werp import nlog
from werp.uatrains.engine import drv
from werp.uatrains.bot import task_status
from werp.uatrains.bot import task_drvs

def run_task(task_id):
    
    try:
        conn = orm.null_engine.connect()
        ses = orm.sescls(bind=conn)
        task = None
        try:
            task = ses.query(uatrains.BotTask).filter(uatrains.BotTask.id == task_id).one()
        except:
            nlog.info('uatrains bot - task runner error', traceback.format_exc())
        if task is not None:
            task.status = task_status.running
            ses.commit()
            try:
                if task.drv == task_drvs.southwest:
                    drv.southwest.get_train_data(task.data)
                elif task.drv == task_drvs.passengers:
                    drv.passengers.get_train_data(task.data)
            except UnicodeDecodeError as e:
                task.http_status = -5
                task.http_status_reason = str(e)
            except URLError as e:
                task.http_status = -4
                task.http_status_reason = str(e)
            except HTTPError as e:
                task.http_status = -3
                task.http_status_reason = str(e)
            except ConnectionError as e:
                task.http_status = -2
                task.http_status_reason = str(e)
            except:
                task.http_status = -1
                task.http_status_reason = str(e)
                nlog.info('uatrains bot - task runner error', traceback.format_exc())
            if task.http_status is None:
                task.http_status = 200
            task.status = task_status.completed
            ses.commit()
        ses.close()
        conn.close()
    except:
        nlog.info('uatrains bot - task runner error', traceback.format_exc())

try:
    conn = orm.q_engine.connect()
    ses = orm.sescls(bind=conn)
    tasks = ses.query(uatrains.BotTask).filter(uatrains.BotTask.status == None).all()
    task_ids = []
    for t in tasks:
        task_ids.append(t.id)
    ses.close()
    conn.close()
    with multiprocessing.Pool(processes=32) as ppool:
        ppool.map(run_task, [task_id for task_id in task_ids])    
    #for task_id in task_ids:
    #    thr = threading.Thread(target=run_task, args=(task_id,))
    #    thr.setDaemon(True)
    #    thr.start()
except:
    nlog.info('uatrains bot - task runner error', traceback.format_exc())