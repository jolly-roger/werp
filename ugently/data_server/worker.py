import traceback
import zmq
import json
import redis
import psycopg2

from werp import nlog
from werp.common import sockets
from werp.common import red_keys

def run():
    conn = None
    cur = None
    try:
        ctx = zmq.Context()
        
        ugently_data_worker_socket = ctx.socket(zmq.REP)
        ugently_data_worker_socket.connect(sockets.ugently_data_worker)
        
        red = redis.StrictRedis(unix_socket_path=sockets.redis)
        
        while True:
            msg = ugently_data_worker_socket.recv_unicode()
            rnd_user_agent = None
            if red.exists(red_keys.ugently_user_agent_value) and red.scard(red_keys.ugently_user_agent_value) > 0:
                rnd_user_agent = red.srandmember(red_keys.ugently_user_agent_value).decode('utf-8')
            else:
                conn = psycopg2.connect('host=localhost port=5432 dbname=werp user=werp password=0v}II587')
                cur = conn.cursor()
                cur.execute("select value from user_agent order by random() limit 1;")
                rnd_user_agent = cur.fetchone()[0]
                cur.close()
                conn.close()
            if rnd_user_agent is not None:
                ugently_data_worker_socket.send_unicode(rnd_user_agent)
            else:
                nlog.info('ugently - data worker error', 'Random user agent is None')
                ugently_data_worker_socket.send_unicode('')
    except:
        nlog.info('ugently - data worker fatal', traceback.format_exc())
        if cur is not None:
            cur.close()
        if conn is not None:    
            conn.close()