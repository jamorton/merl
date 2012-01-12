#version 120

uniform sampler2D font;
uniform sampler2D chars;
uniform sampler2D fcols;
uniform sampler2D bcols;

uniform vec2 ntiles;
uniform vec2 potsize;
uniform vec2 fontscale;
uniform vec3 fontbg;

void main()
{
	vec2 coord    = (gl_TexCoord[0].xy * ntiles);
	vec2 tile_pos = floor(coord);
	vec2 pix_off  = fract(coord) / 16.0;
	pix_off.y = 1.0/16.0 - pix_off.y; // flip each character in Y
	
	vec2 address = tile_pos / potsize + 0.001;

	float char_num = texture2D(chars, address).r * 255.0;
	vec4  fcol = texture2D(fcols, address);
	vec4  bcol = texture2D(bcols, address);

	vec2 charsel = vec2(
		char_num - (16.0 * floor(char_num/16.0)),
		15.0 - floor(char_num / 16.0) //  flip tilemap on Y
	);

	vec4 col = texture2D(font,  (charsel / 16.0f + pix_off) * fontscale);

	if (distance(col.xyz, fontbg)  < 0.05)
		gl_FragColor = bcol;
	else
		gl_FragColor = fcol;


}
