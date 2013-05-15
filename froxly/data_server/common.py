def jproxy2sproxy(proxy):
    return '{"id": ' + str(proxy['id']) + ',"ip": "' + str(proxy['ip']) + '", "port": "' + str(proxy['port']) + \
        '", "protocol": "' + str(proxy['protocol']) + '"}'
def dbproxy2sproxy(proxy):
    return '{"id": ' + str(proxy.id) + ',"ip": "' + str(proxy.ip) + '", "port": "' + str(proxy.port) + \
        '", "protocol": "' + str(proxy.protocol) + '"}'