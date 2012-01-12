
from util import random, data_path
import re
import os

def _load_data(fn):
	data = []
	o = open(data_path(fn))
	for w in re.split("\s+", o.read()):
		data.append(w.lower().strip())
	o.close()
	return list(set(data))
	
adjectives = _load_data("adjectives.txt")
prefixes   = _load_data("name_prefixes.txt")

class _Noun(object):
	_VOWELS = set(["a", "e", "i", "o", "u"])
	def __init__(self, sing, plural):
		self.is_countable = plural != None
		self.singular     = sing
		self.plural       = plural
		
		if sing[0] in _Noun._VOWELS:
			self.vowel = True
		else:
			self.vowel = False
		
	def singular_article(self):
		if not self.is_countable:
			return self.singular
		if self.vowel:
			return "an " + self.singular
		return "a " + self.singular
		
	def plural_article(self):
		if not self.is_countable:
			return self.singular
		return self.plural
		
class _Nouns(object):
	def __init__(self, words):
		self.countable = []
		self.uncountable = []
		self.all = []
		
		for elem in words:
			parts = elem.split(":")
			if len(parts) == 1:
				n = _Noun(elem, None)
				self.all.append(n)
				self.uncountable.append(n)
			else:
				n = _Noun(parts[0], parts[1])
				self.all.append(n)
				self.countable.append(n)
		
	def random(self):
		return random.choice(self.all)
	def random_countable(self):
		return random.choice(self.countable)
	def random_uncountable(self):
		return random.choice(self.uncountable)
		
nouns = _Nouns(_load_data("nouns.txt"))

############################################################

class MarkovGenerator(object):
	def __init__(self, order):
		self.order = order
		self.chain = {}
		self.starts = []
		
	def add_series(self, data):
		if len(data) <= self.order:
			return
			
		self.starts.append(list(data[:self.order]))
		for i in xrange(len(data) - self.order):
			ctx = self.chain
			for j in xrange(self.order + 1):
				w = data[i + j]
				ctx.setdefault(w, {})
				ctx = ctx[w]
				
	def random(self):
		out = random.choice(self.starts)
		while len(out) < 20:
			ctx = self.chain
			for symb in out[-self.order:]:
				if symb not in ctx:
					return out
				ctx = ctx[symb]
			out.append(random.choice(ctx.keys()))
		return out

def create_generator(fn, order):
	mk = MarkovGenerator(order)
	for k in _load_data(fn):
		mk.add_series(k)
	return mk

_markov_names = create_generator("names.txt", 3)

############################################################

class Fragment(object):

	def __init__(self, *args, **kwargs):
		self.data = args
		self.kwargs = kwargs

	def evaluate(self, args):
		joiner = " "
		if self.kwargs.get("nospaces", False):
			joiner = ""
		return joiner.join(self.string(x, args) for x in self.data).strip()

	def string(self, m, args):
		if type(m) == str:
			if self.kwargs.get("cap", False):
				return m.capitalize()
			return m
		return m.evaluate(args)

	def __call__(self, **kwargs):	
		return self.evaluate(kwargs)

class Phrase(Fragment):
	pass

class String(Fragment):
	def evaluate(self, args):
		return self.data

class Optional(Fragment):
	def evaluate(self, args):
		chance = self.kwargs.get("chance", 0.5)
		if random.random() < chance:
			return self.string(self.data[0], args)
		return ""

class Choice(Fragment):
	def evaluate(self, args):
		return self.string(random.choice(self.data), args)

class Argument(Fragment):
	def evaluate(self, args):
		return args[self.data[0]]

class Markov(Fragment):
	def evaluate(self, args):
		return "".join(self.data[0].random())
		
class Filter(Fragment):
	def evaluate(self, args):
		return self.kwargs["func"](self.string(self.data[0], args))
		
class RandomNoun(Fragment):
	def evaluate(self, args):
		return nouns.random().singular
		
############################################################

_name_word = Filter(Markov(_markov_names), func=lambda x: x[:7].capitalize())
random_name = Choice(
	Phrase(
		Choice(*prefixes, cap=True),
		Choice(
			Phrase(Choice(*adjectives, cap=True), RandomNoun(), nospaces=True),
			_name_word,
			Choice(*adjectives, cap=True)
		),
	),
	Phrase(_name_word, _name_word),
	Phrase(_name_word, "the", Choice(*adjectives, cap=True))
)
############################################################


print nouns.random_countable().singular_article()