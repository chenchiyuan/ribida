# -*- coding: utf-8 -*-
# __author__ = chenchiyuan
from __future__ import division, unicode_literals, print_function

__version__ = '1.2'

from utils import to_str, receive_length
import socket
import json
import os

HOME = '/tmp/'
SETTINGS = {
  'WORDSEG_SOCKET': os.path.join(HOME, 'wordseg.sock'),
  'RELATION_SOCKET': os.path.join(HOME, 'relation.sock'),
}

try:
  import django
  WORDSEG_UNIX_DOMAIN = getattr(django.conf.settings, 'WORDSEG_SOCKET', SETTINGS['WORDSEG_SOCKET'])
  RELATIONS_UNIX_DOMAIN = getattr(django.conf.settings, 'RELATION_SOCKET', SETTINGS['RELATION_SOCKET'])
except Exception:
  WORDSEG_UNIX_DOMAIN = SETTINGS['WORDSEG_SOCKET']
  RELATIONS_UNIX_DOMAIN =  SETTINGS['RELATION_SOCKET']

BUFFER_SIZE = 1024
MAX_SIZE = 65536
MAX_CONTENT = 20001

class SocketProxy(object):
  def __init__(self, connect_to, type=socket.AF_UNIX,
               stream=socket.SOCK_STREAM, func=None):
    self.connect_to = connect_to
    self.socket = socket.socket(type, stream)
    self.format_fun = func if func else self.format

  def connect(self):
    self.socket.connect(self.connect_to)

  def sendall(self, str):
    self.socket.sendall(str)

  def receive(self, size=BUFFER_SIZE):
    size = size if size < MAX_SIZE else MAX_SIZE
    data = self.socket.recv(size)
    return data

  def format(self, str_list):
    if not str_list:
      return {}

    return json.loads(str_list.decode('utf-8'))

  def close(self):
    self.socket.close()

  def process(self, str):
    if isinstance(str, dict):
      str = json.dumps(str)

    str = to_str(str)
    if len(str) > MAX_SIZE:
      return {}

    self.connect()
    self.sendall(str)
    size = len(str) * 10

    response_str = self.receive(size)
    self.close()

    return self.format_fun(response_str)

class API(object):
  def __init__(self, connect_to=None):
    self.connect_to = connect_to

  def parse_words(self, title=None, content=None, imagine=True, **kwargs):
    request_dict = {
      'title': title,
      'content': content[:MAX_CONTENT],
      'imagine': imagine
    }
    request_dict.update(kwargs)

    connect_to = self.connect_to if self.connect_to else WORDSEG_UNIX_DOMAIN
    sock = SocketProxy(connect_to=connect_to)
    return sock.process(request_dict)

  def traverse(self, words, **kwargs):
    request_dict = {
      'words': words
    }
    request_dict.update(kwargs)

    connect_to = self.connect_to if self.connect_to else RELATIONS_UNIX_DOMAIN
    sock = SocketProxy(connect_to=connect_to)
    return sock.process(request_dict)
