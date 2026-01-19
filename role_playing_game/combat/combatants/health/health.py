from py4godot import gdclass
from py4godot.classes.Node import Node
from py4godot.signals import signal, SignalArg


@gdclass
class health(Node):
	# Signals
	dead = signal()
	health_changed = signal([SignalArg("life", float)])
	
	# Properties
	life: int = 0
	max_life: int = 10
	base_armor: int = 0
	armor: int = 0
	
	def _ready(self) -> None:
		self.armor = self.base_armor
	
	def take_damage(self, damage: int) -> None:
		self.life = self.life - damage + self.armor
		if self.life <= 0:
			self.dead.emit()
		else:
			self.health_changed.emit(float(self.life))
	
	def heal(self, amount: int) -> None:
		self.life += amount
		self.life = clamp(self.life, self.life, self.max_life)
		self.health_changed.emit(float(self.life))
	
	def get_health_ratio(self) -> float:
		return float(self.life) / self.max_life
