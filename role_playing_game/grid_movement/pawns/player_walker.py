from py4godot import gdclass
from py4godot.classes.Input import Input
from py4godot.classes.core import Vector2
from py4godot.classes.Node2D import Node2D
from grid_movement.pawns.walker import walker


@gdclass
class player_walker(walker):
	
	
	combat_actor_path:str = "res://combat/combatants/player.tscn"
	pose_anims_path: str = "res://grid_movement/pawns/anim_player.tres"
	
	type:int = 0

	def _process(self, _delta: float) -> None:
		input_direction = self.get_input_direction()

		# We only move in integer increments
		input_direction = input_direction.round()

		if input_direction.is_zero_approx():
			return

		self.update_look_direction(input_direction)

		target_position = self.grid.get_pyscript().request_move(self, input_direction)

		if target_position != Vector2.ZERO:
			self.move_to(target_position)
		elif self.get("active"):
			self.bump()

	def get_input_direction(self) -> Vector2:
		return Input.instance().get_vector(
			"move_left",
			"move_right",
			"move_up",
			"move_down"
		)
