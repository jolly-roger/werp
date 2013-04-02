def app(env, start_res):
    start_res('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
    return bytes(str(env), 'utf-8')
