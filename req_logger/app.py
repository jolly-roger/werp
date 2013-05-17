import traceback
import zmq

from werp import orm
from werp import nlog

ctx = zmq.Context()

puller = ctx.socket(zmq.PULL)
puller.bind("ipc:///home/www/sockets/req_logger.socket")

try:
    while True:
        message = puller.recv()
        conn = orm.q_engine.connect()
        ses = orm.sescls(bind=conn)
        log = orm.Log(message.decode('utf-8').strip())
        ses.add(log)
        ses.commit()
        ses.close()
        conn.close()
except:
    nlog.info('req_logger - log error', traceback.format_exc())
