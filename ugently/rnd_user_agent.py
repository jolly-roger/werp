from datetime import timedelta
import zmq
import random
import traceback
import random
import redis

from werp import orm
from werp import nlog

all_user_agents_key = 'ugently_all_user_agents'

try:
    context = zmq.Context()
    rnd_user_agent_socket = context.socket(zmq.REP)
    rnd_user_agent_socket.bind('ipc:///home/www/sockets/rnd_user_agent.socket')
    conn = orm.null_engine.connect()
    ses = orm.sescls(bind=conn)
    red = redis.StrictRedis()
    while True:
        msg = rnd_user_agent_socket.recv_unicode()
        user_agents = []
        if red.exists(all_user_agents_key):
            user_agents = orm.serializer.loads(red.get(all_user_agents_key))
            nlog.info('ugently - rnd user agent debug', 'cache')
        else:
            user_agents = ses.query(orm.UserAgent).filter(orm.UserAgent.is_bot == False).all()
            red.set(all_user_agents_key, orm.serializer.dumps(user_agents))
            delta = timedelta(days=1)
            red.expire(all_user_agents_key, delta)
            nlog.info('ugently - rnd user agent debug', 'sqlalchemy')
        rnd_user_agent = random.choice(user_agents)
        rnd_user_agent_socket.send_unicode(rnd_user_agent.value)
    ses.close()
    conn.close()
except:
    nlog.info('ugently - rnd user agent error', traceback.format_exc())