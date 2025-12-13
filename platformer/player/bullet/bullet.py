from py4godot.classes import gdclass
from py4godot.classes.RigidBody3D import RigidBody3D

@gdclass
class bullet(RigidBody3D):
	def _ready(self) -> None:
		self.enabled=True
