from datetime import timedelta
import zmq
import traceback
import redis
import random

from werp import orm
from werp import nlog

delta = timedelta(days=1)
key_prfix = 'ugently_value_'

try:
    context = zmq.Context()
    rnd_user_agent_socket = context.socket(zmq.REP)
    rnd_user_agent_socket.bind('ipc:///home/www/sockets/rnd_user_agent.socket')
    red = redis.StrictRedis(unix_socket_path='/tmp/redis.socket')
    while True:
        msg = rnd_user_agent_socket.recv_unicode()
        rnd_key = random.choice(red.keys(key_prfix + '*'))
        rnd_user_agent = None
        if rnd_key is not None:
            rnd_user_agent = red.get(rnd_key)
        else:
            conn = orm.null_engine.connect()
            ses = orm.sescls(bind=conn)
            user_agents = ses.query(orm.UserAgent).filter(orm.UserAgent.is_bot == False).all()
            for user_agent in user_agents:
                red.set(key_prfix + str(user_agent.id), user_agent.value)
                red.expire(user_agent.id, delta)
            ses.close()
            conn.close()
            rnd_key = random.choice(red.keys(key_prfix + '*'))
            rnd_user_agent = red.get(rnd_key)
        if rnd_user_agent is not None:
            rnd_user_agent_socket.send_unicode(rnd_user_agent.decode('utf-8'))
        else:
            nlog.info('ugently - rnd user agent error', 'Random user agent is None')
        nlog.info('ugently - rnd user agent debug', rnd_user_agent.decode('utf-8'))
except:
    nlog.info('ugently - rnd user agent error', traceback.format_exc())