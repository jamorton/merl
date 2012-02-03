
from pyglet.gl import *

def _next_pot(v):
	v -= 1
	v |= v >> 1
	v |= v >> 2
	v |= v >> 4
	v |= v >> 8
	v |= v >> 16
	v += 1
	return v

class Shader(object):
	"""
	Simple shader support for pyglet
	"""
	def __init__(self, vert = [], frag = [], geom = []):
		self.handle = glCreateProgram()
		self.linked = False

		if isinstance(vert, basestring):
			vert = [vert]
		if isinstance(frag, basestring):
			frag = [frag]
		if isinstance(geom, basestring):
			geom = [geom]
		
		self._createShader(vert, GL_VERTEX_SHADER)
		self._createShader(frag, GL_FRAGMENT_SHADER)
		# self.createShader(frag, GL_GEOMETRY_SHADER_EXT)

		self._link()

	def _createShader(self, strings, type):
		count = len(strings)
		if count < 1:
			return

		shader = glCreateShader(type)

		src = (c_char_p * count)(*strings)
		glShaderSource(shader, count, cast(pointer(src), POINTER(POINTER(c_char))), None)

		glCompileShader(shader)
		temp = c_int(0)
		glGetShaderiv(shader, GL_COMPILE_STATUS, byref(temp))

		if not temp:
			glGetShaderiv(shader, GL_INFO_LOG_LENGTH, byref(temp))
			buffer = create_string_buffer(temp.value)
			glGetShaderInfoLog(shader, temp, None, buffer)
			print buffer.value
		else:
			glAttachShader(self.handle, shader)
			# flag for deletion, won't actually diseapper until __del__
			glDeleteShader(shader) # flag for deletion, won't

	def __del__(self):
		try:
			glDeleteProgram(self.handle)
		except:
			pass
			
	def _link(self):
		glLinkProgram(self.handle)

		temp = c_int(0)
		glGetProgramiv(self.handle, GL_LINK_STATUS, byref(temp))

		if not temp:
			glGetProgramiv(self.handle, GL_INFO_LOG_LENGTH, byref(temp))
			buffer = create_string_buffer(temp.value)
			glGetProgramInfoLog(self.handle, temp, None, buffer)
			print buffer.value
		else:
			self.linked = True

	def bind(self):
		glUseProgram(self.handle)

	def unbind(self):
		glUseProgram(0)

	UNIFORMF_FUNCS = {
		1: glUniform1f, 2: glUniform2f,
		3: glUniform3f, 4: glUniform4f
	}
	UNIFORMI_FUNCS = {
		1: glUniform1i,	2: glUniform2i,
		3: glUniform3i,	4: glUniform4i
	}

	def uniformf(self, name, *vals):
		"""
		send a float uniform to the shader. accepts 1-5 values
		"""
		if 0 < len(vals) < 5:
			self.UNIFORMF_FUNCS[len(vals)](glGetUniformLocation(self.handle, name), *vals)

	def uniformi(self, name, *vals):
		"""
		send an integer uniform to the shader. accepts 1-5 values
		"""
		if 0 < len(vals) < 5:
			self.UNIFORMI_FUNCS[len(vals)](glGetUniformLocation(self.handle, name), *vals)

	# works with matrices stored as lists,
	# as well as euclid matrices
	def uniform_matrixf(self, name, mat):
		loc = glGetUniformLocation(self.Handle, name)
		glUniformMatrix4fv(loc, 1, False, (c_float * 16)(*mat))

class Texture(object):
	"""
	Pyglet's texture support is complicated and not very flexible.
	This provides a much more thin and simple layer on top of GL's texture support
	"""
	DATA_MAP = {
		GL_UNSIGNED_BYTE: GLubyte,
	}
	def __init__(self, width, height, tex_format, data_format, min_filter = GL_NEAREST, mag_filter = GL_NEAREST):
		self.pot_width = _next_pot(width)
		self.pot_height = _next_pot(height)
		self.width = width
		self.height = height
		self.format = tex_format
		self.data_format = data_format
		self.id = GLuint()

		glGenTextures(1, byref(self.id))
		self.bind()
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, min_filter)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, mag_filter)
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.pot_width, self.pot_height, 0, tex_format, data_format, 0)
		self.unbind()

	def __del__(self):
		try:
			glDeleteTextures(1, byref(self.id))
		except:
			pass
			
	def bind(self):
		glBindTexture(GL_TEXTURE_2D, self.id)

	def unbind(self):
		glBindTexture(GL_TEXTURE_2D, 0)

	def sub_data(self, data, xoff, yoff, width, height):
		self.bind()
		gl_data = (self.DATA_MAP[self.data_format] * len(data))(*data)
		glTexSubImage2D(GL_TEXTURE_2D, 0, xoff, yoff, width, height, self.format, self.data_format, gl_data)
		self.unbind()
