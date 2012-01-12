 
import pyglet
from pyglet.gl import *
from util import data_path, random

class Window(pyglet.window.Window):
	def __init__(self, **kwargs):
		super(Window, self).__init__(800, 600, caption="RPG", **kwargs)

window = Window()
