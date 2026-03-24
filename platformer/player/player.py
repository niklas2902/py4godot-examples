from enum import IntEnum
from py4godot import gdclass
from py4godot.classes.CharacterBody3D import CharacterBody3D
from py4godot.classes.Input import Input
from py4godot.classes.ProjectSettings import ProjectSettings
from py4godot.classes.ResourceLoader import ResourceLoader
from py4godot.classes.core import Vector3, Basis, Transform3D
from py4godot.functions import deg_to_rad, acos, clamp, atan2, sign, cos, sin

def load_scene(path):
	print("load_scene")
	return ResourceLoader.instance().load(path)


class Anim(IntEnum):
	FLOOR = 0
	AIR = 1
@gdclass
class player(CharacterBody3D):

	# Constants
	SHOOT_TIME: float = 1.5
	SHOOT_SCALE: float = 2.0
	CHAR_SCALE = Vector3.new3(0.3, 0.3, 0.3)
	MAX_SPEED: float = 6.0
	TURN_SPEED: float = 40.0
	JUMP_VELOCITY: float = 12.5
	BULLET_SPEED: float = 20.0
	AIR_IDLE_DEACCEL: bool = False
	ACCEL: float = 14.0
	DEACCEL: float = 14.0
	AIR_ACCEL_FACTOR: float = 0.5
	SHARP_TURN_THRESHOLD: float = deg_to_rad(140.0)

	def __init__(self):
		super().__init__()
		self.movement_dir = Vector3.new0()
		self.jumping: bool = False
		self.prev_shoot: bool = False
		self.shoot_blend: float = 0.0
		self.coins: int = 0

		self.initial_position = None
		self.gravity = None
		self._camera = None
		self._animation_tree = None

	def _ready(self) -> None:
		self.initial_position = self.position

		gravity_magnitude = ProjectSettings.instance().get_setting("physics/3d/default_gravity")
		gravity_vector = ProjectSettings.instance().get_setting("physics/3d/default_gravity_vector")
		self.gravity = gravity_vector * gravity_magnitude 

		self._camera = self.get_node("Target/Camera3D")
		self._animation_tree = self.get_node("AnimationTree")

	def _physics_process(self, delta: float) -> None:
		if Input.instance().is_action_pressed("reset_position") or self.global_position.y < -12:
			# Player hit the reset button or fell off the map.
			self.position = self.initial_position
			self.velocity = Vector3()
			# We teleported the player on the lines above. Reset interpolation
			# to prevent it from interpolating from the old player position
			# to the new position.
			self.reset_physics_interpolation()

		# Update coin count and its "parallax" copies.
		coin_count_node = self.get_node("%CoinCount")
		coin_count_node.text = str(self.coins)
		coin_count_node.get_node("Parallax").text = str(self.coins)
		coin_count_node.get_node("Parallax2").text = str(self.coins)
		coin_count_node.get_node("Parallax3").text = str(self.coins)
		coin_count_node.get_node("Parallax4").text = str(self.coins)

		self.velocity += self.gravity * delta

		anim = Anim.FLOOR

		vertical_velocity = self.velocity.y
		horizontal_velocity = Vector3.new3(self.velocity.x, 0, self.velocity.z)

		horizontal_direction = horizontal_velocity.normalized()
		horizontal_speed = horizontal_velocity.length()

		# Player input
		cam_basis = self._camera.get_global_transform().basis
		movement_vec2 = Input.instance().get_vector("move_left", "move_right", "move_forward", "move_back")
		movement_direction = cam_basis * Vector3.new3(movement_vec2.x, 0, movement_vec2.y)
		movement_direction.y = 0
		movement_direction = movement_direction.normalized()

		jump_attempt = Input.instance().is_action_pressed("jump")

		if self.is_on_floor():
			sharp_turn = (horizontal_speed > 0.1 and
						  acos(movement_direction.dot(horizontal_direction)) > self.SHARP_TURN_THRESHOLD)

			if movement_direction.length() > 0.1 and not sharp_turn:
				if horizontal_speed > 0.001:
					horizontal_direction = self.adjust_facing(
						horizontal_direction,
						movement_direction,
						delta,
						1.0 / horizontal_speed * self.TURN_SPEED,
						Vector3.UP
					)
				else:
					horizontal_direction = movement_direction

				if horizontal_speed < self.MAX_SPEED:
					horizontal_speed += self.ACCEL * delta
			else:
				horizontal_speed -= self.DEACCEL * delta
				if horizontal_speed < 0:
					horizontal_speed = 0

			horizontal_velocity = horizontal_direction * horizontal_speed

			skeleton = self.get_node("Player/Skeleton")
			mesh_xform = skeleton.get_transform()
			facing_mesh = -mesh_xform.basis.get_x().normalized()
			facing_mesh = (facing_mesh - Vector3.UP * facing_mesh.dot(Vector3.UP)).normalized()

			if horizontal_speed > 0:
				facing_mesh = self.adjust_facing(
					facing_mesh,
					movement_direction,
					delta,
					1.0 / horizontal_speed * self.TURN_SPEED,
					Vector3.UP
				)

			m3 = Basis.new4(
				-facing_mesh,
				Vector3.UP,
				-facing_mesh.cross(Vector3.UP).normalized()
			).scaled(self.CHAR_SCALE)

			skeleton.set_transform(Transform3D.new2(m3, mesh_xform.origin))

			if not self.jumping and jump_attempt:
				vertical_velocity = self.JUMP_VELOCITY
				self.jumping = True
				self.get_node("SoundJump").play()

		else:
			anim = Anim.AIR

			if movement_direction.length() > 0.1:
				horizontal_velocity += movement_direction * (self.ACCEL * self.AIR_ACCEL_FACTOR * delta)
				if horizontal_velocity.length() > self.MAX_SPEED:
					horizontal_velocity = horizontal_velocity.normalized() * self.MAX_SPEED
			elif self.AIR_IDLE_DEACCEL:
				horizontal_speed = horizontal_speed - (self.DEACCEL * self.AIR_ACCEL_FACTOR * delta)
				if horizontal_speed < 0:
					horizontal_speed = 0
				horizontal_velocity = horizontal_direction * horizontal_speed

			if Input.instance().is_action_just_released("jump") and self.velocity.y > 0.0:
				# Reduce jump height if releasing the jump key before reaching the apex.
				vertical_velocity *= 0.7

		if self.jumping and vertical_velocity < 0:
			self.jumping = False

		self.velocity = horizontal_velocity + Vector3.UP * vertical_velocity

		if self.is_on_floor():
			self.movement_dir = self.velocity

		self.move_and_slide()

		if self.shoot_blend > 0:
			self.shoot_blend *= 0.97
			if self.shoot_blend < 0:
				self.shoot_blend = 0

		shoot_attempt = Input.instance().is_action_pressed("shoot")
		if shoot_attempt and not self.prev_shoot:
			self.shoot_blend = self.SHOOT_TIME
			bullet_scene = load_scene("res://player/bullet/bullet.tscn")
			bullet = bullet_scene.instantiate()
			bullet_transform = self.get_node("Player/Skeleton/Bullet").get_global_transform().orthonormalized()
			bullet.set_transform(bullet_transform)
			self.get_parent().add_child(bullet)
			bullet.set_linear_velocity(
				bullet_transform.basis.get_z().normalized() * self.BULLET_SPEED
			)
			bullet.add_collision_exception_with(self)
			self.get_node("SoundShoot").play()

		self.prev_shoot = shoot_attempt

		if self.is_on_floor():
			# How much the player should be blending between the "idle" and "walk/run" animations.
			self._animation_tree.set("parameters/run/blend_amount", horizontal_speed / self.MAX_SPEED)

			# How much the player should be running (as opposed to walking).
			self._animation_tree.set("parameters/speed/blend_amount",
									 min(1.0, horizontal_speed / (self.MAX_SPEED * 0.5)))

		self._animation_tree.set("parameters/state/blend_amount", anim.value)
		self._animation_tree.set("parameters/air_dir/blend_amount",
								 clamp(-self.velocity.y / 4 + 0.5, 0, 1))
		self._animation_tree.set("parameters/gun/blend_amount", min(self.shoot_blend, 1.0))

	def adjust_facing(self, facing: Vector3, target: Vector3, step: float,
					  adjust_rate: float, current_gn: Vector3) -> Vector3:
		normal = target
		t = normal.cross(current_gn).normalized()

		x = normal.dot(facing)
		y = t.dot(facing)

		ang = atan2(y, x)

		if abs(ang) < 0.001:
			return facing

		s = sign(ang)
		ang = ang * s
		turn = ang * adjust_rate * step

		if ang < turn:
			a = ang
		else:
			a = turn

		ang = (ang - a) * s

		return (normal * cos(ang) + t * sin(ang)) * facing.length()
