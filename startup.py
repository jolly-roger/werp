import os
import os.path

from werp.common import sockets


if os.path.isfile(sockets.get_socket_path(sockets.froxly_grabber_server)):
    os.remove(sockets.get_socket_path(sockets.froxly_grabber_server))