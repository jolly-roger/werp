import redis
import uuid

from werp.common import sockets, red_keys

red = redis.StrictRedis(unix_socket_path=sockets.redis)

def create():
    ses_key = str(uuid.uuid4())
    red.set(red_keys.dap_ses_key_prefix + ses_key, '', ex=900)
    return ses_key

def exists(ses_key):
    return red.exists(red_keys.dap_ses_key_prefix + ses_key)