from py4godot import gdclass
from py4godot.classes.Node import Node
from py4godot.classes.core import Array, NodePath
from py4godot.classes.Object import ConnectFlags, Object
from py4godot.signals import signal, SignalArg


@gdclass
class turn_queue(Node):
	combatants_node: Node
	active_combatant_changed = signal([SignalArg("active_combatant", Object)])

	def __init__(self):
		super().__init__()
		self.queue = []
		self.active_combatant = None

	def initialize(self) -> None:
		self.set_queue(self.combatants_node.get_children())
		self.play_turn()

	def play_turn(self) -> None:
		def on_turn_finished():
			self.get_next_in_queue()
			self.play_turn()

		self.active_combatant.get("turn_finished").connect(
			on_turn_finished,
			ConnectFlags.CONNECT_ONE_SHOT
		)

	def get_next_in_queue(self):
		current = self.queue.pop(0)
		current.set("active", False)

		self.queue.append(current)
		self._set_active_combatant(self.queue[0])
		return self.active_combatant

	def remove(self, combatant) -> None:
		new_queue = list(self.queue)

		if combatant in new_queue:
			new_queue.remove(combatant)

		combatant.queue_free()
		self.set_queue(new_queue)

	def set_queue(self, new_queue) -> None:
		self.queue.clear()

		for node in new_queue:
			if not node.get_name() in ("Player", "Opponent", "Combatant"):
				continue

			self.queue.append(node)
			node.set("active", False)

		if self.queue:
			self._set_active_combatant(self.queue[0])

	def _set_active_combatant(self, new_combatant) -> None:
		self.active_combatant = new_combatant
		self.active_combatant.set("active", True)
		self.active_combatant_changed.emit(self.active_combatant)
