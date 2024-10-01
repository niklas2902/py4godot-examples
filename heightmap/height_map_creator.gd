@tool
extends Node3D

var heightmap_path = "res://heightmap_pillow.png"
var displacement_factor = 10.0

var vertices = PackedVector3Array()
var heightmap = Image.new()

var SCALE = 0.1
var DISPLACEMENT = 2
var generator_path:NodePath = "Generator"
var generator:Node

func _ready() -> void:
	generator = get_node(generator_path)
	generate_terrain_from_buffer()

func generate_height_value(val:float):
	return (val - 0.5) * DISPLACEMENT 

func add_triangles(current, left, bottom, bottom_left):
	# first triangle
	vertices.append(left)
	vertices.append(current)
	vertices.append(bottom)
	
	# second triangle
	vertices.append(left)
	vertices.append(bottom)
	vertices.append(bottom_left)
	

func generate_triangles_for_pixel(x:int, y:int, image:Image):
	var current = image.get_pixel(x,y).r
	var left = image.get_pixel(x-1,y).r
	var bottom = image.get_pixel(x,y+1).r
	var bottom_left = image.get_pixel(x-1,y+1).r
	
	var vertice_current = Vector3((x - image.get_width()/2)*SCALE, generate_height_value(current), (y - image.get_height()/2)*SCALE	)
	var vertice_left = Vector3(vertice_current.x - 1 * SCALE, generate_height_value(left) ,vertice_current.z)
	var vertice_bottom = Vector3(vertice_current.x, generate_height_value(bottom) ,vertice_current.z+1 * SCALE)
	var vertice_bottom_left = Vector3(vertice_current.x - 1 * SCALE, generate_height_value(bottom_left) ,vertice_current.z+1 * SCALE)
	
	add_triangles(vertice_current, vertice_left, vertice_bottom, vertice_bottom_left)
	
func generate_terrain_from_buffer():
	var width = 512
	var height = 512
	
	heightmap = Image.create(width, height, true, Image.FORMAT_RGB8)
	generator.call("fill_height_map", width, height, heightmap)
	
	for x in range(1, width):
		for y in range(0, height - 1):
			generate_triangles_for_pixel(x, y, heightmap)
	
	var array_mesh = ArrayMesh.new()
	var arrays = []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices

	array_mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)

	var terrain_mesh = MeshInstance3D.new()
	terrain_mesh.mesh = array_mesh

	var material = StandardMaterial3D.new()
	material.albedo_color = Color(0.8, 0.8, 0.8)  # Set the color to gray (or any other color)
	terrain_mesh.material_override = material
	add_child(terrain_mesh)
