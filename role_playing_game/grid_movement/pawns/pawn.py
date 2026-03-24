from py4godot import gdclass
from py4godot.classes.Node2D import Node2D


@gdclass
class pawn(Node2D):

	ACTOR: int = 0
	OBSTACLE: int = 1
	OBJECT: int = 2

	type: int = OBJECT

	def __init__(self):
		super().__init__()
		self.active = True

	def set_active(self, value: bool) -> None:
		self.active = value
		self.set_process(value)
		self.set_process_input(value)
