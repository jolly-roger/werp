import datetime
import zmq
import traceback
import redis
import random

from werp import orm
from werp import nlog

expire_delta = datetime.timedelta(days=1)
red_key_prfix = 'ugently_user_agent_value_'
conn = None
ses = None
ctx = None
try:
    ctx = zmq.Context()
    rnd_user_agent_socket = ctx.socket(zmq.REP)
    rnd_user_agent_socket.bind('ipc:///home/www/sockets/rnd_user_agent.socket')
    red = redis.StrictRedis(unix_socket_path='/tmp/redis.socket')
    while True:
        msg = rnd_user_agent_socket.recv_unicode()
        red_keys = red.keys(red_key_prfix + '*')
        rnd_user_agent = None
        if len(red_keys) > 0:
            rnd_key = random.choice(red_keys)
            rnd_user_agent = red.get(rnd_key)
        else:
            conn = orm.null_engine.connect()
            ses = orm.sescls(bind=conn)
            user_agents = ses.query(orm.UserAgent).filter(orm.UserAgent.is_bot == False).all()
            for user_agent in user_agents:
                red.set(red_key_prfix + str(user_agent.id), user_agent.value)
                red.expire(user_agent.id, expire_delta)
            ses.close()
            conn.close()
            rnd_key = random.choice(red.keys(red_key_prfix + '*'))
            rnd_user_agent = red.get(rnd_key)
        if rnd_user_agent is not None:
            rnd_user_agent_socket.send_unicode(rnd_user_agent.decode('utf-8'))
        else:
            nlog.info('ugently - rnd user agent error', 'Random user agent is None')
except:
    nlog.info('ugently - rnd user agent error', traceback.format_exc())
    if ctx is not None:
        ctx.destroy()
    if ses is not None:
        ses.close()
    if conn is not None:    
        conn.close()