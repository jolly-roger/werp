DATA_SERVER_WORKER_POOL = 256
CHECKER_WORKER_POOL = 64
REQUESTER_WORKER_POOL = 128

def jproxy2sproxy(proxy):
    return '{"id": ' + str(proxy['id']) + ',"ip": "' + str(proxy['ip']) + '", "port": "' + str(proxy['port']) + \
        '", "protocol": "' + str(proxy['protocol']) + '", "protocol_version": "' + str(proxy['protocol_version']) + '"}'
def dbproxy2sproxy(proxy):
    protocol_version = ''
    if proxy.protocol == 'http':
        protocol_version = '1.0'
    elif proxy.protocol == 'https':
        protocol_version = '1.0'
    elif proxy.protocol == 'socks4/5':
        protocol_version = '4'
    return '{"id": ' + str(proxy.id) + ',"ip": "' + str(proxy.ip) + '", "port": "' + str(proxy.port) + \
        '", "protocol": "' + str(proxy.protocol) + '", "protocol_version": "' + protocol_version + '"}'