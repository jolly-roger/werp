#import traceback
import zmq

#from werp import orm
#from werp.orm import uatrains
#from werp import nlog
#from werp.uatrains.engine import drv

ctx = zmq.Context()

pusher = ctx.socket(zmq.PUSH)
#pusher.bind("ipc:///home/www/sockets/uatrains_bot_task.socket")
pusher.bind("tcp://127.0.0.1:1431")

pusher.send(b'Yo!!')

#try:
    
    
    
    #for tid in range(0, 5000):
    #    msg = bytes(drv.southwest.ua_url.replace('(tid)', str(tid)), 'utf-8')
    #    pusher.send(msg)
    #    pusher.send_string(drv.southwest.ru_url.replace('(tid)', str(tid)))
    #    pusher.send_string(drv.southwest.en_url.replace('(tid)', str(tid)))
    #for tid in range(20000, 70000):
    #    pusher.send_string(drv.passengers.ua_url.replace('(tid)', str(tid)))
    #    pusher.send_string(drv.passengers.ru_url.replace('(tid)', str(tid)))
    #    pusher.send_string(drv.passengers.en_url.replace('(tid)', str(tid)))
    #conn = orm.q_engine.connect()
    #ses = orm.sescls(bind=conn)
    #
    #for tid in range(0, 5000):
    #    ua_bot_task = uatrains.BotTask()
    #    ua_bot_task.data = drv.southwest.ua_url.replace('(tid)', str(tid))
    #    ses.add(ua_bot_task)
    #    ru_bot_task = uatrains.BotTask()
    #    ru_bot_task.data = drv.southwest.ru_url.replace('(tid)', str(tid))
    #    ses.add(ru_bot_task)
    #    en_bot_task = uatrains.BotTask()
    #    en_bot_task.data = drv.southwest.en_url.replace('(tid)', str(tid))
    #    ses.add(en_bot_task)
    #for tid in range(20000, 70000):
    #    ua_bot_task = uatrains.BotTask()
    #    ua_bot_task.data = drv.passengers.ua_url.replace('(tid)', str(tid))
    #    ses.add(ua_bot_task)
    #    ru_bot_task = uatrains.BotTask()
    #    ru_bot_task.data = drv.passengers.ru_url.replace('(tid)', str(tid))
    #    ses.add(ru_bot_task)
    #    en_bot_task = uatrains.BotTask()
    #    en_bot_task.data = drv.passengers.en_url.replace('(tid)', str(tid))
    #    ses.add(en_bot_task)
    #ses.commit()
    #ses.close()
    #conn.close()
#except:
#    nlog.info('uatrains bot - task creator error', traceback.format_exc())