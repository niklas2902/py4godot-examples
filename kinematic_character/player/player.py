# file: player.py
from py4godot.functions import move_toward, clamp
from py4godot.methods import private
from py4godot.classes import gdclass
from py4godot.classes.CharacterBody2D import CharacterBody2D
from py4godot.classes.Input import Input
from py4godot.classes.ProjectSettings import ProjectSettings

WALK_FORCE = 600
WALK_MAX_SPEED = 200
STOP_FORCE = 1300
JUMP_SPEED = 200

@gdclass
class player(CharacterBody2D):
	gravity: float = 0.0
	
	def _ready(self) -> None:
		self.gravity = float(ProjectSettings.instance().get_setting("physics/2d/default_gravity"))
	
	def _physics_process(self, delta: float) -> None:
		# Horizontal movement code. First, get the player's input.
		walk = WALK_FORCE * Input.instance().get_axis("move_left", "move_right")
		
		# Slow down the player if they're not trying to move.
		if abs(walk) < WALK_FORCE * 0.2:
			# The velocity, slowed down a bit, and then reassigned.
			self.velocity.x = move_toward(self.velocity.x, 0, STOP_FORCE * delta)
		else:
			self.velocity.x += walk * delta
		
		# Clamp to the maximum horizontal movement speed.
		self.velocity.x = clamp(self.velocity.x, -WALK_MAX_SPEED, WALK_MAX_SPEED)
		
		# Vertical movement code. Apply gravity.
		self.velocity.y += self.gravity * delta
		
		# Move based on the velocity and snap to the ground.
		# TODO: This information should be set to the CharacterBody properties instead of arguments: snap, Vector2.DOWN, Vector2.UP
		# TODO: Rename velocity to linear_velocity in the rest of the script.
		self.move_and_slide()
		
		# Check for jumping. is_on_floor() must be called after movement code.
		if self.is_on_floor() and Input.instance().is_action_just_pressed("jump"):
			self.velocity.y = -JUMP_SPEED
