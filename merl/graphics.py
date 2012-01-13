
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

if __name__ == "__main__":

	window = pyglet.window.Window(800, 600, caption="Graphics")
	con = Console(75, 40, 20, 75)

	fps_display = pyglet.clock.ClockDisplay()
	
	chars = [random.randint(1,255) for i in range(75*40)]
	fcols = [random.randint(1,255) for i in range(75*40 * 3)]
	bcols = [random.randint(1,40) for i in range(75*40 * 3)]
	
	@window.event
	def on_draw():
		pass
	
	def update(dt):
		window.clear()
		con.render(chars, fcols, bcols)
		fps_display.draw()
		
	
	pyglet.clock.schedule(update)
	pyglet.app.run()

