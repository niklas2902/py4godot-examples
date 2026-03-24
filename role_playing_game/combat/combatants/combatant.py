from py4godot import gdclass
from py4godot.classes.Node import Node
from py4godot.signals import signal
from py4godot.classes.AnimationNodeStateMachinePlayback import AnimationNodeStateMachinePlayback


@gdclass
class combatant(Node):
	# Signals
	turn_finished = signal([])
	
	# Properties
	defense: int = 1
	damage: int = 1
	active: bool = False
	animation_playback: AnimationNodeStateMachinePlayback = None
	
	def _ready(self) -> None:
		animation_tree = self.get_node("Sprite2D/AnimationTree")
		self.animation_playback = animation_tree.get("parameters/playback")
	
	def set_active(self, value: bool) -> None:
		self.active = value
		self.set_process(value)
		self.set_process_input(value)
		
		if not self.active:
			return
		
		health = self.get_node("Health")
		if health.get_pyscript().armor >= health.get_pyscript().base_armor + self.defense:
			health.get_pyscript().armor = health.get_pyscript().base_armor
	
	def attack(self, target: Node) -> None:
		target.get_pyscript().take_damage(self.damage)
		self.turn_finished.emit()
	
	def defend(self) -> None:
		health = self.get_node("Health")
		health.get_pyscript().armor += self.defense
		self.turn_finished.emit()
	
	def flee(self) -> None:
		self.turn_finished.emit()
	
	def take_damage(self, damage_to_take: float) -> None:
		health = self.get_node("Health")
		health.get_pyscript().take_damage(damage_to_take)
		self.animation_playback.start("take_damage")
