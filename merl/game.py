
from util import random
import language

class Trait(object):
	def __init__(self, key, name):
		self.key   = key
		self.name  = name

class Rules(object):
	def __init__(self):
		
		self.traits = [
			Trait("hp",           "Life"),
			Trait("mp",           "Mana"),
			Trait("armor",        "Armor"),
			Trait("resist",       "Magic Resist"),
			Trait("attack_speed", "Attack Speed"),
			Trait("damage",       "Damage"),
			Trait("")
		]
		
		self.stats = []
		
		
	def random_price(self, val):
		
class Hero(object):
	def __init__(self):
		
