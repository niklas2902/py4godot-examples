
from py4godot.methods import private
from py4godot.signals import signal, SignalArg
from py4godot.classes import gdclass
from py4godot.classes.core import Vector3
from py4godot.classes.Area3D import Area3D

@gdclass
class coin(Area3D):
	def _ready(self):
		self.taken = False
	def _on_coin_body_enter(self, body):
		if not self.taken and str(body.get_name()) == "Player":
			self.get_node("Animation").play("take")
			self.taken = True
			# We've already checked whether the colliding body is a Player, which has a `coins` property.
			# As a result, we can safely increment its `coins` property.
			body.get_pyscript().coins += 1	
