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


def run():
    try:
        if not os.path.exists(sockets.get_socket_path(sockets.uatrains_bot_task_worker)):
            ctx = zmq.Context()
            uatrains_bot_task_worker_socket = ctx.socket(zmq.PUSH)
            uatrains_bot_task_worker_socket.bind(sockets.uatrains_bot_task_worker)
    
            conn = orm.null_engine.connect()
            ses = orm.sescls(bind=conn)

            for tid in range(0, 5000):
                bot_task = orm.uatrains.BotTask()
                bot_task.data = str(tid)
                bot_task.drv = task_drvs.southwest
                ses.add(bot_task)
            #for tid in range(20000, 70000):
            #    bot_task = orm.uatrains.BotTask()
            #    bot_task.data = str(tid)
            #    bot_task.drv = task_drvs.passengers
            #    ses.add(bot_task)
            ses.commit()
            
            tasks = ses.query(orm.uatrains.BotTask).filter(orm.uatrains.BotTask.status == None).\
                order_by(orm.desc(orm.cast(orm.uatrains.BotTask.data, orm.BigInteger))).all()
            
            manager = threading.Thread(target=sink.run, args=(len(tasks),))
            manager.start()
            
            for wrk_num in range(8):
                thr = threading.Thread(target=worker.run)
                thr.start()
            
            for t in tasks:
                uatrains_bot_task_worker_socket.send_unicode(t.id)
            
            uatrains_bot_task_finish_socket = ctx.socket(zmq.SUB)
            uatrains_bot_task_finish_socket.connect(sockets.uatrains_bot_task_finish)
            uatrains_bot_task_finish_socket.setsockopt_string(zmq.SUBSCRIBE, '')
            uatrains_bot_task_finish_socket.recv_unicode()
            
            ses.close()
            conn.close()
        else:
            bot.logger.error('uatrains bot info. Bot already started')
    except:
        bot.logger.error('uatrains bot - task ventilator error\r\n' + traceback.format_exc())
        raise Exception('Task ventilator error. See log.')