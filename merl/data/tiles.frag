#version 120

uniform sampler2D font;
uniform sampler2D chars;
uniform sampler2D fcols;
uniform sampler2D bcols;

uniform vec2 ntiles;    // number of tiles in console in X,Y dir
uniform vec2 potsize;   // true size of char/col textures (power-of-two)
uniform vec2 fontscale; // percent of font texture that is used
uniform vec3 fontbg;    // bg color of font to make transparent
uniform vec2 nchars;     // number of chars in x, y  dir on font sheet

void main()
{
	vec2 coord    = gl_TexCoord[0].xy * ntiles;
	vec2 tile_pos = floor(coord);
	vec2 pix_off  = fract(coord) / nchars;
	pix_off.y = 1.0/nchars.y - pix_off.y; // flip each character in Y
	
	vec2 address = tile_pos / potsize + 0.001;

	float char_num = texture2D(chars, address).r * 255.0;
	vec4  fcol     = texture2D(fcols, address);
	vec4  bcol     = texture2D(bcols, address);

	vec2 charsel = vec2(
		char_num - (nchars.x * floor(char_num/16.0)),
		(nchars.y - 1.0) - floor(char_num / nchars) //  flip tilemap on Y
	);

	vec4 col = texture2D(font,  (charsel / nchars + pix_off) * fontscale);

	if (distance(col.xyz, fontbg)  < 0.05)
		gl_FragColor = bcol;
	else
		gl_FragColor = fcol;
}
