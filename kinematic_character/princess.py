# file: goal.py
from py4godot.classes import gdclass
from py4godot.classes.Node import Node
from py4godot.classes.Node2D import Node2D

@gdclass
class princess(Node):
	
	def _on_body_entered(self, body: Node2D) -> None:
		if body.name == "Player":
			self.get_node("../WinText").show()
