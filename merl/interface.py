 
import pyglet
from pyglet.gl import *
from util import data_path, random

class Window(pyglet.window.Window):
	def __init__(self, **kwargs):
		super(Window, self).__init__(800, 600, caption="RPG", **kwargs)

		
class TileMap(object):
	TILEWIDTH  = 10
	TILEHEIGHT = 12
	
	def __init__(self, width, height):
		self.width  = width
		self.height = height
		self.tiles  = [0] * (width * height)
		self.fgcolors = [(1.0, 1.0, 1.0)] * (width * height)
		self.bgcolors = [(0.0, 0.0, 0.0)] * (width * height)
		self.load_tiles(pyglet.image.load(data_path("tiles.png")))
		
	def load_tiles(self, im):
		data = list(im.get_image_data().get_data("RGBA", im.width * 4))
		
		a, b = chr(255), chr(0)
		for i in xrange(0, len(data), 4):
			if data[i] == a and data[i+1] == b and data[i+2] == a:
				data[i+3] = b
		
		im.set_data("RGBA", im.width * 4, "".join(data))
		
		grid = pyglet.image.ImageGrid(im, 16, 16)
		self.texes = pyglet.image.TextureGrid(grid)
		
			
	def display(self, x, y, sx, sy, nx, ny):
		TW = TileMap.TILEWIDTH
		TH = TileMap.TILEHEIGHT
		
		glEnable(GL_COLOR_MATERIAL)
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		
		for i in range(sx, sx + nx):
			for j in range(sy, sy + ny):
				k = i + self.width * j
				glColor3f(*self.fgcolors[k])
				self.texes[self.tiles[k]].blit(x + (i-sx) * TW, y + (j-sy) * TH)
				
	def set_tile(self, x, y, num, col):
		self.tiles[x + y * self.width] = num % 16 + (15 - num / 16) * 16
		self.fgcolors[x + y * self.width] = (((col & 0xFF0000) >> 16) / 255.0, ((col & 0xFF00) >> 8) / 255.0, (col & 0xFF) / 255.0)
		
	def text(self, x, y, text, color, wrap = 10000):
		i = 0
		for char in text:
			self.set_tile(x + i, y, ord(char), color)
			i += 1
			if i >= wrap:
				i = 0
				y -= 1
		
window = Window()

t = TileMap(30, 10)

t.text(0, 4, "i like turtles", 0xFF0000)
t.text(0, 3, "no really I do", 0x00FF00)

fps_display = pyglet.clock.ClockDisplay()

def update(dt):
	window.clear()
	t.tiles = [random.randint(0, 250)] * (t.width * t.height)
	t.display(200, 200, 0, 0, 30, 10)
	fps_display.draw()
	
pyglet.clock.schedule(update)

@window.event
def on_draw():
	pass


pyglet.app.run()
