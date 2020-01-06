import websocket
from time import sleep
from threading import Thread
from dataclasses import dataclass

PoEConnections = None

class PoESocket:
    socket_id = 0

    def __init__(self, league, identifier, POESESSID,
                    on_message, on_connected=None, on_disconnected=None):
        self.league = league
        self.identifier = identifier
        self.POESESSID = POESESSID
        self.on_message = on_message
        self.on_connected = on_connected
        self.on_disconnected = on_disconnected
        self.reconnecting = False
        PoESocket.socket_id += 1
        self.socket_id = PoESocket.socket_id

        self.connect()

    def _connect(self):
        websocket.enableTrace(False)

        self.ws = websocket.WebSocketApp(
            "wss://www.pathofexile.com/api/trade/live/{}/{}".format(
                self.league, self.identifier
            ),
            on_open=self.on_open,
            on_error=self.on_error,
            on_close=self.on_close,
            on_message=self.on_message,
            cookie="POESESSID=" + self.POESESSID,
        )

        thread = Thread(target=self.ws.run_forever)
        thread.daemon = True
        thread.start()

        self.establish_connection(sleep_time=3)

    def connect(self):
        thread = Thread(target=self._connect)
        thread.start()
        thread.join()

    def establish_connection(self, sleep_time=0):
        sleep(sleep_time)  # Wait 3 seconds to see if we got an insta-disconnect

        # Retry connection if we couldn't connect
        if not self.ws.sock or not self.ws.sock.connected:
            self.reconnect()
        else:
            PoEConnections.add(self)
            if self.on_connected:
                self.on_connected(self)

    def close_connection(self):
        self.ws.close(status=6969, reason="Stop Button")
        if self.on_disconnected:
            self.on_disconnected(self)

    def on_error(self, err):
        print('Websocket #{} error: '.format(self.socket_id, err))

    def on_open(self):
        print('Websocket #{} connected'.format(self.socket_id))

    def on_close(self, code, reason):
        print('Websocket #{} closed [Code {}] | Reason: "{}"'.format(
            self.socket_id,
            code,
            reason
        ))
        if code and code != 6969:
            self.establish_connection(sleep_time=3)

    def reconnect(self):
        if not self.reconnecting:
            self.reconnecting = True
            print("Websocket refused to connect, retrying...")
            self.connect()
            self.reconnecting = False

@dataclass
class PoESockets:
    sockets: set
    connected: int

    def add(self, socket: PoESocket):
        self.sockets.add(socket)

    def status_update(self):
        self.connected = sum(
            1
            for socket in self.sockets
            if socket.ws.sock and socket.ws.sock.connected
        )
        return self.connected

    def get_dead(self):
        return {
            socket
            for socket in self.sockets
            if socket.ws.sock and not socket.ws.sock.connected
        }

PoEConnections = PoESockets(set(), 0)
