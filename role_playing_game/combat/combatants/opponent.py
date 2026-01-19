from py4godot import gdclass
from py4godot.classes.Node import Node
from combat.combatants.combatant import combatant
from py4godot.signals import signal
from py4godot.classes.Object import ConnectFlags, Object


@gdclass
class opponent(combatant):
	
	turn_finished = signal([])
	
	def set_active(self, value: bool) -> None:
		super().set_active(value)
		
		if not self.active:
			return
		
		timer = self.get_node("Timer")
		if not timer.is_inside_tree():
			return
		timer.timeout.connect(self._on_timer_timeout, ConnectFlags.CONNECT_ONE_SHOT)
		timer.start()
	
	def _on_timer_timeout(self) -> None:
		target: Node = None
		for actor in self.get_parent().get_children():
			if actor != self:
				target = actor
				break
		
		self.attack(target)
