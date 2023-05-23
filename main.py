import socket
from threading import Thread

class ServerSocket:
  def __init__(self, host: str, port: int, *, protocol: str='tcp'):
    if protocol.lower() == 'tcp':
      proto = socket.SOCK_STREAM
    elif protocol.lower() == 'udp':
      proto = socket.SOCK_DGRAM
    else:
      raise ValueError('Protocol must be either tcp or udp.')
    self.socket: socket.socket = socket.socket(socket.AF_INET, proto)
    self.socket.bind((host, port))
    self.connections: list[Thread] = []
    def _ig(*a,**k):
      pass
    self._on_recv = _ig
    self._on_con = _ig
    self._on_dcon = _ig
    
  def set_handler(self, event):
    def inner(f):
      if event == 'connect':
        self._on_con = f
      elif event == 'recieve':
        s
    
  def run(max_connections: int=0, 
