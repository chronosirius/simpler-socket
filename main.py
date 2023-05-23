import socket
from threading import Thread, Event

class Protocol:
  def __init__(self, protocol_name, *, parser=None, editor=None):
    self.protocol_name = protocol_name
    if parser is None:
      self.parser = lambda x: x
    else:
      self.parser = parser
    if editor is None:
      self.make_edits = lambda x: x
    else:
      self.make_edits = editor
      
class _Connection:
  """
  This class should never be instantiated by itself.
  """
  def __init__(self, socket, addr, save_comms):
    self._socket = socket
    self.addr = addr
    self.datas = []
    self.rseq = 0
    self.sseq = 0
  def send(self, data):
    self._socket.send(data.encode())
    self.sseq += 1
    if self.save_comms:
      self.datas.append({
        'type': 'outgoing',
        'data': data
      })
  def recv(self, bufsize):
    d = self._socket.recv(bufsize)
    d = d.decode()
    self.rseq += 1
    if self.save_comms:
      self.datas.append({
        'type': 'incoming',
        'data': d
      })
  def close(self):
    self._socket.close()
    

class ServerSocket:
  """
  This is the server socket class.
  
  Arguments: 
    host: host to bind to
    port: port to bind to
    kw protocol: any of tcp or udp
    kw dataprotocol: an instance of the Protocol class that can handle custom protocols
  """
  def __init__(self, host: str, port: int, *, protocol: str='tcp', dataprotocol: Protocol = Protocol('default_proto')):
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
    self.dataprotocol = dataprotocol
    self.terminator = Event()
    self.runner = None
    
  def set_handler(self, event: str):
    def inner(f):
      if event == 'connect':
        self._on_con = f
      elif event == 'recieve':
        self._on_recv = f
      elif event == 'disconnect':
        self._on_dcon = f
      return f
    return inner
    
  def run(self, *, max_connections: int=0, bufsize=1024, save_prev=False):
    if self.runner is not None:
      return False
    def _listen(conn):
      self._on_con(conn)
      while True:
        d = conn.recv(bufsize)
        if d == 0 or self.terminator.is_set():
          self._on_dcon(conn)
          conn.close()
          break
        d = self.dataprotocol.parse(d)
        conn['seq'] += 1
        if (p := self._on_recv(d, conn)) is not None:
          proto_fixed = self.dataprotocol.make_edits(p)
          conn.send(proto_fixed)
    def _run():
      self.socket.listen(max_connections)
      while True:
        sk, addr = self.socket.accept()
        conn = _Connection(sk, addr, save_prev)
        t = Thread(target=_listen, args=(conn,))
        self.connections.append(t)
        t.start()
        if self.terminator.is_set():
          for c in self.connections:
            t.join()
          break
    self.runner = Thread(target=_run)
    self.runner.start()
    return self.runner
  def stop(self):
    self.terminator.set()
    self.runner.join()
    
        
        
        
        
