import traceback
import threading
import socket
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
            except socket.timeout as e:
                task.http_status = -6
                task.http_status_reason = str(e)
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
            except Exception as e:
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
    conn = orm.null_engine.connect()
    ses = orm.sescls(bind=conn)
    tasks = ses.query(uatrains.BotTask).filter(uatrains.BotTask.status == None).limit(32).all()
    task_ids = []
    for t in tasks:
        task_ids.append(t.id)
    for task_id in task_ids:
        run_task(task_id)
        #thr = threading.Thread(target=run_task, args=(task_id,))
        #thr.setDaemon(True)
        #thr.start()
    ses.close()
    conn.close()
except:
    nlog.info('uatrains bot - task runner error', traceback.format_exc())