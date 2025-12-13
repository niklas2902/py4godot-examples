from py4godot import gdclass
from py4godot.classes.RigidBody3D import RigidBody3D
from py4godot.classes.AnimationPlayer import AnimationPlayer
from py4godot.classes.RayCast3D import RayCast3D
from py4godot.classes.Node3D import Node3D
from py4godot.classes.AudioStreamPlayer3D import AudioStreamPlayer3D
from py4godot.classes.ProjectSettings import ProjectSettings
from py4godot.classes.core import Vector3, Basis, Transform3D


@gdclass
class enemy(RigidBody3D):
	# Constants
	ACCEL: float = 5.0
	DEACCEL: float = 20.0
	MAX_SPEED: float = 2.0
	ROT_SPEED: float = 1.0
	
	def __init__(self):
		super().__init__()
		self.prev_advance: bool = False
		self.dying: bool = False
		self.rot_dir: float = 4.0
		
		self.gravity = None
		self._animation_player = None
		self._ray_floor = None
		self._ray_wall = None
		self._enemy_node = None
		self._skeleton_node = None
		self._sound_walk_loop = None
		self._sound_hit = None
	
	def _ready(self) -> None:
		# Initialize gravity
		gravity_magnitude = ProjectSettings.instance().get_setting("physics/3d/default_gravity")
		gravity_vector = ProjectSettings.instance().get_setting("physics/3d/default_gravity_vector")
		self.gravity = gravity_vector * gravity_magnitude
		
		# Get node references
		self._enemy_node = self.get_node("Enemy")
		self._animation_player = self.get_node("Enemy/AnimationPlayer")
		self._skeleton_node = self.get_node("Enemy/Skeleton")
		self._ray_floor = self.get_node("Enemy/Skeleton/RayFloor")
		self._ray_wall = self.get_node("Enemy/Skeleton/RayWall")
		self._sound_walk_loop = self.get_node("SoundWalkLoop")
		self._sound_hit = self.get_node("SoundHit")
	
	def _integrate_forces(self, state) -> None:
		delta = state.get_step()
		lin_velocity = state.get_linear_velocity()
		grav = state.get_total_gravity()
		
		# get_total_gravity returns zero for the first few frames, leading to errors.
		if grav.is_zero_approx():
			grav = self.gravity
		
		lin_velocity += grav * delta  # Apply gravity.
		up = -grav.normalized()
		
		if self.dying:
			state.set_linear_velocity(lin_velocity)
			return
		
		# Check collisions
		for i in range(state.get_contact_count()):
			contact_collider = state.get_contact_collider_object(i)
			contact_normal = state.get_contact_local_normal(i)
			
			if contact_collider is not None:
				# Check if collider is a Bullet with enabled propertyaaaawwww
				if str(contact_collider.get_name()) == "Bullet" and contact_collider.get_pyscript().enabled:
					self.dying = True
					self.axis_lock_angular_x = False
					self.axis_lock_angular_y = False
					self.axis_lock_angular_z = False
					self.collision_layer = 0
					state.set_angular_velocity(-contact_normal.cross(up).normalized() * 33.0)
					self._animation_player.play("impact")
					self._animation_player.queue("extra/explode")
					contact_collider.enabled = False
					self._sound_walk_loop.stop()
					self._sound_hit.play()
					return
		
		# Movement logic
		advance = self._ray_floor.is_colliding() and not self._ray_wall.is_colliding()
		dir = self._skeleton_node.get_transform().basis.z.normalized()
		deaccel_dir = dir
		
		if advance:
			if dir.dot(lin_velocity) < self.MAX_SPEED:
				lin_velocity += dir * self.ACCEL * delta
			deaccel_dir = dir.cross(self.gravity).normalized()
		else:
			if self.prev_advance:
				self.rot_dir = 1
			dir = Basis.new3(up, self.rot_dir * self.ROT_SPEED * delta) * dir
			self._skeleton_node.set_transform(Transform3D.new0().looking_at(-dir, up))
		
		dspeed = deaccel_dir.dot(lin_velocity)
		dspeed -= self.DEACCEL * delta
		if dspeed < 0:
			dspeed = 0
		
		lin_velocity = lin_velocity - deaccel_dir * deaccel_dir.dot(lin_velocity) \
				+ deaccel_dir * dspeed
		
		state.set_linear_velocity(lin_velocity)
		self.prev_advance = advance
	
	def _die(self) -> None:
		self.queue_free()
