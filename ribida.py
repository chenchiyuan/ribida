# -*- coding: utf-8 -*-
# __author__ = chenchiyuan
from __future__ import division, unicode_literals, print_function

__version__ = '1.4.0'

from utils import to_str
import socket
import json
import os

HOME = '/tmp/'
SETTINGS = {
  'WORDSEG_SOCKET': os.path.join(HOME, 'wordseg.sock'),
  'RELATIONS_SOCKET': os.path.join(HOME, 'relations.sock'),
  'PLACEINFO_SOCKET': os.path.join(HOME, 'place_info.sock')
}

try:
  import django
  WORDSEG_UNIX_DOMAIN = getattr(django.conf.settings, 'WORDSEG_SOCKET', SETTINGS['WORDSEG_SOCKET'])
  RELATIONS_UNIX_DOMAIN = getattr(django.conf.settings, 'RELATIONS_SOCKET', SETTINGS['RELATIONS_SOCKET'])
  PLACEINFO_UNIX_DOMAIN = getattr(django.conf.settings, 'PLACEINFO_SOCKET', SETTINGS['PLACEINFO_SOCKET'])
except Exception:
  WORDSEG_UNIX_DOMAIN = SETTINGS['WORDSEG_SOCKET']
  RELATIONS_UNIX_DOMAIN =  SETTINGS['RELATIONS_SOCKET']
  PLACEINFO_UNIX_DOMAIN = SETTINGS['PLACEINFO_SOCKET']

BUFFER_SIZE = 1024
MAX_SIZE = 65536
MAX_CONTENT = 20001

class SocketProxy(object):
  def __init__(self, connect_to, type=socket.AF_UNIX,
               stream=socket.SOCK_STREAM, func=None,
               force_max=False):
    self.connect_to = connect_to
    self.socket = socket.socket(type, stream)
    self.format_fun = func if func else self.format
    self.force_max = force_max

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
    size = len(str) * 10 if not self.force_max else MAX_SIZE

    response_str = self.receive(size)
    self.close()

    return self.format_fun(response_str)

class API(object):
  def __init__(self, connect_to=None):
    self.connect_to = connect_to

  def parse_words(self, title='', content='', imagine=True, **kwargs):
    """
    Parse words based on title and content
    """
    request_dict = {
      'func_name': 'rank',
      'title': title,
      'content': content[:MAX_CONTENT],
      'imagine': imagine
    }
    request_dict.update(kwargs)

    connect_to = self.connect_to if self.connect_to else WORDSEG_UNIX_DOMAIN
    sock = SocketProxy(connect_to=connect_to)
    return sock.process(request_dict)

  def traverse(self, words, **kwargs):
    """
    Get tag relations.
    """
    request_dict = {
      'func_name': 'traverse',
      'words': words
    }
    request_dict.update(kwargs)

    connect_to = self.connect_to if self.connect_to else RELATIONS_UNIX_DOMAIN
    sock = SocketProxy(connect_to=connect_to)
    return sock.process(request_dict)

  def get_place_info(self, slug_or_slugs, **kwargs):
    """
    Can search place_info by place_slug or slugs.
    Waring: socket is limit to 65536, so when you search
    a log of data, it may cause exception.
    """
    request_dict = {
      'func_name': 'get_by_slug',
      'slugs': slug_or_slugs,
    }
    request_dict.update(kwargs)

    connect_to = self.connect_to if self.connect_to else PLACEINFO_UNIX_DOMAIN
    sock = SocketProxy(connect_to=connect_to, force_max=True)
    return sock.process(request_dict)

  def tag(self, name, func_name, score=6.0, parents=[], equal_to='', items=[]):
    if not func_name in ('update', 'add', 'remove', 'get'):
      return ''

    request_dict = {
      'name': name,
      'func_name': func_name,
      'score': score,
      'parents': parents,
      'equal_to': equal_to,
      'items': items
    }
    connect_to = self.connect_to if self.connect_to else WORDSEG_UNIX_DOMAIN
    sock = SocketProxy(connect_to=connect_to)
    return sock.process(request_dict)

