import traceback
import zmq
import json
import redis

from werp import orm
from werp import nlog
from werp.common import sockets
from werp.common import red_keys

def run():
    conn = None
    ses = None
    try:
        ctx = zmq.Context()
        
        ugently_data_worker_socket = ctx.socket(zmq.REP)
        ugently_data_worker_socket.connect(sockets.ugently_data_worker)
        
        red = redis.StrictRedis(unix_socket_path=sockets.redis)
        
        while True:
            msg = ugently_data_worker_socket.recv_unicode()
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
                ugently_data_worker_socket.send_unicode(rnd_user_agent.decode('utf-8'))
            else:
                nlog.info('ugently - data worker error', 'Random user agent is None')
                ugently_data_worker_socket.send_unicode('')
    except:
        nlog.info('ugently - data worker fatal', traceback.format_exc())
        if ses is not None:
            ses.close()
        if conn is not None:    
            conn.close()