import zmq

import orm

ctx = zmq.Context()

puller = ctx.socket(zmq.PULL)
puller.bind("ipc:///home/www/sockets/req_logger.socket")

while True:
    message = puller.recv()
    conn = orm.q_engine.connect()
    ses = orm.sescls(bind=conn)
    entry = orm.Entry(message)
    ses.add(entry)
    ses.commit()
    ses.close()
    conn.close()
