from py4godot import gdproperty, signal, private, gdclass, SignalArg

from py4godot.classes.Image.Image import Image
from py4godot.classes.Node3D.Node3D import Node3D
import noise
import numpy as np

from py4godot.classes.Image.Image import Image as GDImage
from py4godot.classes.core import Color


def generate_height_map():

	# Parameters
	width, height = 512, 512
	scale = 0.1

	# Generate sinusoidal heightmap
	x = np.linspace(0, width * scale, width)
	y = np.linspace(0, height * scale, height)
	X, Y = np.meshgrid(x, y)

	heightmap = np.sin(X) * np.cos(Y)

	# Normalize to [0, 1] range
	heightmap = (heightmap - np.min(heightmap)) / (np.max(heightmap) - np.min(heightmap))

	# Convert to 8-bit (0-255 range)
	heightmap_8bit = (heightmap * 255).astype(np.uint8)

	# Save using Pillow
	img = Image.fromarray(heightmap_8bit)
	img.save("heightmap_pillow.png")

def create_sinusoidal_heightmap(width:int, height:int) -> np.ndarray:
	scale = 0.1

	# Generate sinusoidal heightmap
	x = np.linspace(0, width * scale, width)
	y = np.linspace(0, height * scale, height)
	X, Y = np.meshgrid(x, y)

	heightmap = np.sin(X) * np.cos(Y)

	# Normalize to [0, 1] range
	heightmap = (heightmap - np.min(heightmap)) / (np.max(heightmap) - np.min(heightmap))
	return heightmap

def create_perlin_heightmap(width:int, height:int) -> np.ndarray:
	scale = 100.0  # Adjust for the "zoom" of the noise

	# Generate heightmap
	heightmap = np.zeros((width, height))

	for x in range(width):
		for y in range(height):
			# Perlin noise: octaves, persistence, and lacunarity can tweak the result
			heightmap[x][y] = noise.pnoise2(x / scale,
											y / scale,
											octaves=6,
											persistence=0.5,
											lacunarity=2.0,
											repeatx=1024,
											repeaty=1024,
											base=42)

	# Normalize to [0, 1] range
	heightmap = (heightmap - np.min(heightmap)) / (np.max(heightmap) - np.min(heightmap))
	return heightmap
def create_for_godot_image(width:int,height:int,gd_heightmap:GDImage)->None:
	heightmap = create_sinusoidal_heightmap(width, height)
	for x in range(width):
		for y in range(height):
			numpy_color = heightmap[x,y]
			gd_heightmap.set_pixel(x,y, Color.new3(numpy_color, numpy_color, numpy_color))

@gdclass
class HeightMapGenerator(Node3D):
	def fill_height_map(self,width:int, height:int, heightmap:Image) -> None:
		create_for_godot_image(width, height, heightmap)
