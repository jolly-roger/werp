froxly_checker_worker = 'ipc:///home/www/sockets/froxly_checker_worker_(url).socket'
froxly_checker_finish = 'ipc:///home/www/sockets/froxly_checker_finish_(url).socket'
froxly_checker_sink = 'ipc:///home/www/sockets/froxly_checker_sink_(url).socket'
froxly_checker_server = 'ipc:///home/www/sockets/froxly_checker_server.socket'

froxly_data_server = 'ipc:///home/www/sockets/froxly_data_server.socket'
froxly_data_worker = 'ipc:///home/www/sockets/froxly_data_worker.socket'

froxly_requester_server = 'ipc:///home/www/sockets/froxly_requester_server.socket'
froxly_requester_worker = 'ipc:///home/www/sockets/froxly_requester_worker.socket'

ugently_data_server = 'ipc:///home/www/sockets/ugently_data_server.socket'
ugently_data_worker = 'ipc:///home/www/sockets/ugently_data_worker.socket'

uatrains_bot_server = 'ipc:///home/www/sockets/uatrains_bot_server.socket'
uatrains_bot_task_worker = 'ipc:///home/www/sockets/uatrains_bot_task_worker.socket'

redis = '/tmp/redis.socket'


def format_socket_path(socket_path, url=''):
    return socket_path.replace('(url)', url.replace('/', '%'))