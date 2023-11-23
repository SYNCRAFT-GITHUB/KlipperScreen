import json

class Moonraker:
    class DEFAULT:
        HOST = "127.0.0.1"
        PORT = "7125"
        API = ""
    class New:
        host = None
        port = None
        api = None

    def get_host():
        return Moonraker.New.host if Moonraker.New.host else Moonraker.DEFAULT.HOST

    def get_port():
        return Moonraker.New.port if Moonraker.New.port else Moonraker.DEFAULT.PORT

    def get_api():
        return Moonraker.New.api if Moonraker.New.api else Moonraker.DEFAULT.API

    def set_new_connection(host=None, port=None, api=None):
        Moonraker.New.host = host
        Moonraker.New.port = port
        Moonraker.New.api = api
    
