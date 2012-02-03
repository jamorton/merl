
from pyglet.gl import *
import pyglet
from util import data_file, data_path, random
from gl import Texture, Shader

class Console(object):
	CHAR_WIDTH = 10
	CHAR_HEIGHT = 12
	def __init__(self, tilesx, tilesy, posx, posy):
		self.tilesx = tilesx
		self.tilesy = tilesy
		
		self.font = pyglet.image.load(data_path("tiles.png")).get_texture()
		self.ch_tex = Texture(tilesx, tilesy, GL_RED, GL_UNSIGNED_BYTE)
		self.fg_tex = Texture(tilesx, tilesy, GL_RGB, GL_UNSIGNED_BYTE)
		self.bg_tex = Texture(tilesx, tilesy, GL_RGB, GL_UNSIGNED_BYTE)
		
		self.shader = Shader(
			data_file("tiles.vert"),
			data_file("tiles.frag")
		)
		self.shader.bind()
		self.shader.uniformf("ntiles", tilesx, tilesy)
		self.shader.uniformf("potsize", self.ch_tex.pot_width, self.ch_tex.pot_height)
		self.shader.uniformf("fontscale", self.font.tex_coords[6], self.font.tex_coords[7])
		self.shader.uniformf("fontbg", 1.0, 0.0, 1.0)
		self.shader.uniformf("nchars", 16.0, 16.0)
		self.shader.unbind()
		
		self.batch = pyglet.graphics.Batch()
		w = tilesx * self.CHAR_WIDTH; h = tilesy * self.CHAR_HEIGHT
		self.batch.add(
			4, GL_QUADS, None,
			("v2f/static", (posx, posy, posx+w, posy, posx+w, posy+h, posx, posy+h)),
			("t2f/static", (0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0))
		)

	def render(self, chars, fg, bg):
		glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
		self.ch_tex.sub_data(chars, 0, 0, self.tilesx, self.tilesy)
		self.fg_tex.sub_data(fg, 0, 0, self.tilesx, self.tilesy)
		self.bg_tex.sub_data(bg, 0, 0, self.tilesx, self.tilesy)

		self.shader.bind()
		
		glActiveTexture(GL_TEXTURE0)
		glBindTexture(self.font.target, self.font.id)
		self.shader.uniformi("font", 0)

		glActiveTexture(GL_TEXTURE1)
		self.ch_tex.bind()
		self.shader.uniformi("chars", 1)
		
		glActiveTexture(GL_TEXTURE2)
		self.fg_tex.bind()
		self.shader.uniformi("fcols", 2)
		
		glActiveTexture(GL_TEXTURE3)
		self.bg_tex.bind()
		self.shader.uniformi("bcols", 3)
		
		self.batch.draw()
		self.shader.unbind()

		glBindTexture(GL_TEXTURE_2D, 0)
		glActiveTexture(GL_TEXTURE0)

class TileMap(object):
	def __init__(self, tiles, pos, max_tiles):
		"""
		tiles: tuple containing (x, y) width of console display
		pos: tuple containing (x, y) position of display
		max_tiles: tuple containing (x, y) total width of tile map
		"""
		
		self.con = Console(*(tiles+pos))
		self.xtiles = tiles[0]
		self.ytiles = tiles[1]
		self.xpos = pos[0]
		self.ypos = pos[1]
		self.xmax = max_tiles[0]
		self.ymax = max_tiles[1]

		sz = self.xmax * self.ymax
		self.tiles = [0] * sz
		self.fcols = [255,255,255] * sz
		self.bcols = [0,0,0] * sz

		self.xview = 0
		self.yview = 0

		self.dirty = True

	def set_view(self, vx, vy):
		self.xview = vx
		self.yview = vy
		self.dirty = True

	def move_view(self, dx, dy):
		self.xview += dx
		self.yview += dy
		self.dirty = True
		
	def render(self):
		if self.dirty:
			start = self.xview + self.yview * self.xmax
			stop  = start + self.xmax * self.ytiles
			self._tmp_t = []
			self._tmp_f = []
			self._tmp_b = []
			for i in range(start, stop, self.xmax):
				self._tmp_t.extend(self.tiles[i:i+self.xtiles])
			for i in range(start*3, stop*3, self.xmax*3):
				self._tmp_f.extend(self.fcols[i:i+self.xtiles*3])
			for i in range(start*3, stop*3, self.xmax*3):
				self._tmp_b.extend(self.bcols[i:i+self.xtiles*3])


		self.con.render(
			self._tmp_t,
			self._tmp_f,
			self._tmp_b
		)
		
		self.dirty = False
		
	def set_tile(self, x, y, n, fcol = 0xFFFFFF, bcol = 0x000000):
		if self.xview < x < self.xview + self.xtiles and \
		   self.yview < y < self.yview + self.ytiles:
			self.dirty = True
		
		i  = y * self.xmax + x
		i3 = i * 3
		self.tiles[i] = n
		self.fcols[i3]   = fcol >> 8
		self.fcols[i3+1] = (fcol & 0xFF00) >> 4
		self.fcols[i3+2] = fcol & 0xFF
		self.bcols[i3]   = bcol >> 8
		self.bcols[i3+1] = (bcol & 0xFF00) >> 4
		self.bcols[i3+2] = bcol & 0xFF

def test_tilemap():
	window = pyglet.window.Window(800, 600, caption="Graphics")
	tm = TileMap((80, 50), (0, 0), (300, 300))
	tm.set_tile(5, 5, 1)

	def update(dt):
		tm.render()

	pyglet.clock.schedule(update)

	@window.event
	def on_key_release(symbol, mods):
		if symbol == pyglet.window.key.RIGHT:
			tm.move_view(1, 0)
		if symbol == pyglet.window.key.DOWN:
			tm.move_view(0, 1)
		if symbol == pyglet.window.key.UP:
			tm.move_view(0, -1)
		if symbol == pyglet.window.key.LEFT:
			tm.move_view(-1, 0)

	pyglet.app.run()

if __name__ == "__main__":
	test_tilemap()
