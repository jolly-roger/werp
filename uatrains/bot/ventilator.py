import traceback
import zmq

from werp.uatrains import bot
from werp import orm
from werp.common import sockets

def run():
    try:
        ctx = zmq.Context()
        uatrains_bot_task_worker_socket = ctx.socket(zmq.PUSH)
        uatrains_bot_task_worker_socket.bind(sockets.uatrains_bot_task_worker)

        conn = orm.null_engine.connect()
        ses = orm.sescls(bind=conn)
        tasks = ses.query(orm.uatrains.BotTask).filter(orm.uatrains.BotTask.status == None).all()
        for t in tasks:
            uatrains_bot_task_worker_socket.send_unicode(t.id)
        ses.close()
        conn.close()
    except:
        bot.logger.error('uatrains bot - task ventilator error\r\n' + traceback.format_exc())
        raise Exception('Task ventilator error. See log.')