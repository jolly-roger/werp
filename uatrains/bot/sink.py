import traceback
import zmq

from werp.uatrains import bot
from werp.common import sockets

def run(task_count):
    try:
        ctx = zmq.Context()
        
        uatrains_bot_task_sink_socket = ctx.socket(zmq.PULL)
        uatrains_bot_task_sink_socket.bind(sockets.uatrains_bot_task_sink)
        
        uatrains_bot_task_finish_socket = ctx.socket(zmq.PUB)
        uatrains_bot_task_finish_socket.bind(sockets.uatrains_bot_task_finish)
        
        while True:
            uatrains_bot_task_sink_socket.recv_unicode()

            task_count = task_count - 1
            if task_count == 0:
                break
        uatrains_bot_task_finish_socket.send_unicode(str(0))
    except:
        bot.logger.error('uatrains bot - task sink error\r\n', traceback.format_exc())