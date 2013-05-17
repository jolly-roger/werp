import datetime
import zmq
import traceback
import redis
import random

from werp import orm
from werp import nlog
from werp.common import sockets
from werp.common import red_keys

conn = None
ses = None
ctx = None
try:
    ctx = zmq.Context()
    rnd_user_agent_socket = ctx.socket(zmq.REP)
    rnd_user_agent_socket.bind(sockets.rnd_user_agent)
    red = redis.StrictRedis(unix_socket_path=sockets.redis)
    while True:
        msg = rnd_user_agent_socket.recv_unicode()
        rnd_user_agent = None
        if red.exists(red_keys.ugently_user_agent_value) and red.scard(red_keys.ugently_user_agent_value) > 0:
            rnd_user_agent = red.srandmember(red_keys.ugently_user_agent_value)
        else:
            conn = orm.null_engine.connect()
            ses = orm.sescls(bind=conn)
            user_agents = ses.query(orm.UserAgent).filter(orm.UserAgent.is_bot == False).all()
            for user_agent in user_agents:
                red.sadd(red_keys.ugently_user_agent_value, user_agent.value)
            ses.close()
            conn.close()
            rnd_user_agent = red.srandmember(red_keys.ugently_user_agent_value)
        if rnd_user_agent is not None:
            rnd_user_agent_socket.send_unicode(rnd_user_agent.decode('utf-8'))
        else:
            nlog.info('ugently - rnd user agent error', 'Random user agent is None')
except:
    nlog.info('ugently - rnd user agent error', traceback.format_exc())
    if ses is not None:
        ses.close()
    if conn is not None:    
        conn.close()
    if ctx is not None:
        ctx.term()