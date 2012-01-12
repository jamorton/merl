
import random as _random
import os

class Random(_random.Random):
	pass
	
random = Random()

def data_path(fn):
	return os.path.join(os.path.dirname(__file__), "data", fn)
def data_file(fn):
	f = open(data_path(fn))
	d = f.read()
	f.close()
	return d
