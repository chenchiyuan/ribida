# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function

receive_length = lambda str: len(str) * 10

def to_unicode(obj):
  if isinstance(obj, str):
    return obj.decode('utf-8')
  else:
    return obj

def to_str(obj):
  if isinstance(obj, unicode):
    return obj.encode('utf-8')
  elif isinstance(obj, str):
    return obj
  else:
    return obj
