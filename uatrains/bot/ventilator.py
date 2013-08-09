import traceback
import zmq
import json
import threading
import os.path

from werp.uatrains import bot
from werp import orm
from werp.common import sockets
from werp.uatrains.bot import sink, worker
from werp.uatrains.bot import task_drvs


def run(task_drv, worker_pool):
    try:
        if not os.path.exists(sockets.get_socket_path(
            sockets.format_socket_uri(sockets.uatrains_bot_task_worker, drv=task_drv))):
            ctx = zmq.Context()
            uatrains_bot_task_worker_socket = ctx.socket(zmq.PUSH)
            uatrains_bot_task_worker_socket.bind(sockets.format_socket_uri(sockets.uatrains_bot_task_worker, drv=task_drv))
    
            conn = orm.null_engine.connect()
            ses = orm.sescls(bind=conn)
            
            if task_drv == task_drvs.southwest:
                for tid in range(0, 5000):
                    bot_task = orm.uatrains.BotTask()
                    bot_task.data = str(tid)
                    bot_task.drv = task_drvs.southwest
                    ses.add(bot_task)
            elif task_drv == task_drvs.passengers:
                for tid in range(0, 70000):
                    bot_task = orm.uatrains.BotTask()
                    bot_task.data = str(tid)
                    bot_task.drv = task_drvs.passengers
                    ses.add(bot_task)
            ses.commit()
            
            tasks = ses.query(orm.uatrains.BotTask).\
                filter(orm.and_(orm.uatrains.BotTask.status == None, orm.uatrains.BotTask.drv == task_drv)).\
                order_by(orm.desc(orm.cast(orm.uatrains.BotTask.data, orm.BigInteger))).all()
            
            manager = threading.Thread(target=sink.run, args=(len(tasks), task_drv))
            manager.start()
            
            for wrk_num in range(worker_pool):
                thr = threading.Thread(target=worker.run, args=(task_drv,))
                thr.start()
            
            for t in tasks:
                uatrains_bot_task_worker_socket.send_unicode(t.id)
            
            uatrains_bot_task_finish_socket = ctx.socket(zmq.SUB)
            uatrains_bot_task_finish_socket.connect(
                sockets.format_socket_uri(sockets.uatrains_bot_task_finish, drv=task_drv))
            uatrains_bot_task_finish_socket.setsockopt_string(zmq.SUBSCRIBE, '')
            uatrains_bot_task_finish_socket.recv_unicode()
            
            ses.close()
            conn.close()
        else:
            bot.logger.error('uatrains bot info. Bot already started')
    except:
        bot.logger.error('uatrains bot - task ventilator error\r\n' + traceback.format_exc())
        raise Exception('Task ventilator error. See log.')