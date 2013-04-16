import zmq
import random

from werp import orm

context = zmq.Context()
rnd_user_agent_socket = context.socket(zmq.REP)
rnd_user_agent_socket.bind('ipc:///home/www/sockets/rnd_user_agent.socket')

try:
    conn = orm.q_engine.connect()
    ses = orm.sescls(bind=conn)
    while True:
        msg = rnd_user_agent_socket.recv_unicode()
        user_agents = ses.query(orm.UserAgent).filter(orm.UserAgent.is_bot == False).all()
        rnd_user_agent = random.choice(user_agents)
        rnd_user_agent_socket.send_unicode(rnd_user_agent.value)
    ses.close()
    conn.close()
except:
    nlog.info('req_logger - log error', traceback.format_exc())