import json
from decimal import *
import unittest

items = {'b':2,'basd':2}
msg = items
print(dir(msg))
msg.pop('b')
print(msg)