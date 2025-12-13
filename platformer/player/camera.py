from py4godot import gdclass
from py4godot.classes.Camera3D import Camera3D
from py4godot.classes.CharacterBody3D import CharacterBody3D
from py4godot.classes.PhysicsRayQueryParameters3D import PhysicsRayQueryParameters3D
from py4godot.classes.PhysicsServer3D import PhysicsServer3D
from py4godot.classes.RigidBody3D import RigidBody3D
from py4godot.classes.core import Vector3, Basis, Array
from py4godot.functions import deg_to_rad, clamp

liste = []
@gdclass
class camera(Camera3D):
	MAX_HEIGHT = 2.0
	MIN_HEIGHT = 0.0
	
	min_distance: float = 0.5
	max_distance: float = 3.5
	angle_v_adjust: float = 0.0
	autoturn_ray_aperture: float = 25.0
	autoturn_speed: float = 50.0
	
	def __init__(self):
		super().__init__()
		self.collision_exception = []
	
	def _ready(self):
		# Find collision exceptions for ray.
		# This is done to prevent the player and enemies from colliding
		# with the camera.
		node = self
		while node is not None:
			if isinstance(node, (RigidBody3D, CharacterBody3D)):
				self.collision_exception.append(node.get_rid())
				break
			else:
				node = node.get_parent()
		
		# This detaches the camera transform from the parent spatial node.
		self.set_as_top_level(True)
		self.empty_basis = Basis.new0()
	
	def _physics_process(self, delta: float):
		target = self.get_parent().get_global_transform().origin
		pos = self.get_global_transform().origin
		difference = pos - target
		
		# Regular delta follow.
		# Check ranges.
		if difference.length() < self.min_distance:
			difference = difference.normalized() * self.min_distance
		elif difference.length() > self.max_distance:
			difference = difference.normalized() * self.max_distance
		
		# Check upper and lower height.
		difference.y = clamp(difference.y, self.MIN_HEIGHT, self.MAX_HEIGHT)
		
		# Check autoturn.
		ds = PhysicsServer3D.instance().space_get_direct_state(self.get_world_3d().get_space())
		
		col_left = ds.intersect_ray(PhysicsRayQueryParameters3D.create(
			target,
			target + Basis.new3(Vector3.UP, deg_to_rad(self.autoturn_ray_aperture)) * difference,
			0xffffffff,
			Array.from_list(self.collision_exception)
		))
		
		col = ds.intersect_ray(PhysicsRayQueryParameters3D.create(
			target,
			target + difference,
			0xffffffff,
			Array.from_list(self.collision_exception)
		))
		
		col_right = ds.intersect_ray(PhysicsRayQueryParameters3D.create(
			target,
			target + Basis.new3(Vector3.UP, deg_to_rad(-self.autoturn_ray_aperture)) * difference,
			0xffffffff,
			Array.from_list(self.collision_exception)
		))
		
		
		if not col.is_empty():
			# If main ray was occluded, get camera closer, this is the worst case scenario.
			difference = col["position"] - target
		elif not col_left.is_empty() and col_right.is_empty():
			# If only left ray is occluded, turn the camera around to the right.
			difference = Basis.new3(Vector3.UP, deg_to_rad(-delta * self.autoturn_speed)) * difference
		elif col_left.is_empty() and not col_right.is_empty():
			# If only right ray is occluded, turn the camera around to the left.
			difference = Basis.new3(Vector3.UP, deg_to_rad(delta * self.autoturn_speed)) * difference
		
		# Do nothing otherwise, left and right are occluded but center is not, so do not autoturn.
		
		# Apply lookat.
		if difference.is_zero_approx():
			difference = (pos - target).normalized() * 0.0001
		
		pos = target + difference
		
		self.look_at_from_position(pos, target, Vector3.UP)
		
		
		# Turn a little up or down.
		self.transform.basis *= Basis.new3(self.transform.basis.get_x(), deg_to_rad(self.angle_v_adjust))
