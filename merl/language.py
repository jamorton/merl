
from util import random, data_path
import re
import os

#################################################
#### DATA DEFINITIONS
#################################################

def _load_data(fn):
	data = []
	o = open(data_path(fn))
	for w in re.split("\s+", o.read()):
		if len(w) > 0:
			data.append(w.lower().strip())
	o.close()
	return list(set(data))	

class _LangData(object):
	def __init__(self, filename):
		self.init()
		f = open(data_path(filename))
		self.all = []
		self.tags = {}
		for line in f.readlines():
			if len(line.strip()) == 0:
				continue
			parts = line.split("|")
			w = self.add_word(parts[0].strip().split(":"))
			self.all.append(w)
			if len(parts) == 2:
				for tag in parts[1].strip().split():
					self.tags.setdefault(tag, []).append(w)
		f.close()

	def init(self):
		pass

	def add_word(self, parts):
		raise Error()

	def random(self):
		return random.choice(self.all)
	def random_tag(self, tag):
		if tag not in self.tags:
			return ""
		return random.choice(self.tags[tag])

		
class _Noun(object):
	_VOWELS = set(["a", "e", "i", "o", "u"])
	def __init__(self, sing, plural = None):
		self.is_countable = True
		if plural is None:
			self.is_countable = False
			plural = sing
		self.singular     = sing
		self.plural       = plural

		self.vowel = True if sing[0] in self._VOWELS else False
		
	def singular_article(self):
		if not self.is_countable:
			return self.singular
		if self.vowel:
			return "an " + self.singular
		return "a " + self.singular
		
class _Nouns(_LangData):
	def init(self):
		self.countable = []
		self.uncountable = []
		
	def add_word(self, parts):
		n = _Noun(*parts)
		if n.is_countable: self.countable.append(n)
		else:              self.uncountable.append(n)
		return n

	def random_countable(self):
		return random.choice(self.countable)
	def random_uncountable(self):
		return random.choice(self.uncountable)
		
class _Verb(object):
	def __init__(self, parts):
		self.pres_singular = parts[0]
		self.pres_plural   = parts[1]
		self.pres_particip = parts[2]
		self.past          = parts[3]
		self.past_particip = parts[4]
		
class _Verbs(_LangData):
	def add_word(self, parts):
		return _Verb(parts)
	
#################################################
#### LANGUAGE GENERATION
#################################################
	
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
		if isinstance(m, basestring):
			if self.kwargs.get("cap", False):
				return m.capitalize()
			return m
		return m.evaluate(args)

	def __call__(self, **kwargs):	
		return self.evaluate(kwargs)

class Phrase(Fragment):
	pass

class Concat(Fragment):
	def __init__(self, *args, **kwargs):
		kwargs["nospaces"] = True
		Fragment.__init__(self, *args, **kwargs)

class Optional(Fragment):
	def evaluate(self, args):
		chance = self.kwargs.get("chance", 0.5)
		if random.random() < chance:
			return self.string(self.data[0], args)
		return ""

class Choice(Fragment):
	def evaluate(self, args):
		if len(self.data) == 1 and hasattr(self.data[0], "__getitem__"):
			return self.string(random.choice(self.data[0]), args)
		return self.string(random.choice(self.data), args)

class Argument(Fragment):
	def evaluate(self, args):
		return args[self.data[0]]

class Filter(Fragment):
	def evaluate(self, args):
		return self.kwargs["func"](self.string(self.data[0], args))

class Func(Fragment):
	def evaluate(self, args):
		return self.data[0]()
		
#################################################
#### USAGES
#################################################

markov_names = None
nouns        = None
adjectives   = None
prefixes     = None
verbs        = None

def compile():
	global markov_names, nouns, adjectives, prefixes, verbs
	markov_names = create_generator("lang/names.txt", 3)
	nouns        = _Nouns("lang/nouns.txt")
	adjectives   = _load_data("lang/adjectives.txt")
	prefixes     = _load_data("lang/name_prefixes.txt")
	verbs        = _Verbs("lang/verbs.txt")

	

#################################################

_noun = Func(lambda: nouns.random().singular)

# Names
_rname = Func(lambda: "".join(markov_names.random())[:7].capitalize())
_radjective = Func(lambda: random.choice(adjectives).capitalize())
_rprefix    = Func(lambda: random.choice(prefixes).capitalize())
random_name = Choice(
	Phrase(
		_rprefix,
		Choice(
			Concat(_radjective, _noun),
			_rname,
			_radjective
		),
	),
	Phrase(_rname, _rname),
	Phrase(_rname, "the", _radjective)
)

# Items
item_name = Choice(
	Phrase(
		Func(lambda: nouns.random().singular.capitalize()),
		"of",
		Func(lambda: verbs.random().pres_particip.capitalize())
	),
	Phrase(
		_radjective,
		Func(lambda: nouns.random().singular.capitalize())
	),
	Phrase(
		Func(lambda: verbs.random().past.capitalize()),
		Func(lambda: nouns.random().singular.capitalize())
	)
)

if __name__ == "__main__":
	compile()
	print item_name()
