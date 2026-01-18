from py4godot import gdclass
from grid_movement.pawns.walker import walker


@gdclass
class opponent_character(walker):
	type:int = 0
	
	combat_actor_path:str = "res://combat/combatants/opponent.tscn"
	pose_anims_path: str = "res://grid_movement/pawns/anim_opponent.tres"

	def _ready(self) -> None:
		super()._ready()
		self.set_process(False)
