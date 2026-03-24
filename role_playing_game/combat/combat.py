from py4godot import gdclass
from py4godot.classes.Node import Node
from py4godot.classes.PackedScene import PackedScene
from py4godot.classes.core import Array
from py4godot.classes.Object import Object, ConnectFlags

from py4godot.signals import signal, SignalArg


@gdclass
class combat(Node):
	combat_finished = signal([SignalArg("winner", Object), SignalArg("loser", Object)])

	def _ready(self) -> None:
		self.ui = self.get_node("CombatCanvas/UI")

		self.ui.get("flee").connect(self._on_flee)

	def initialize(self, combat_combatants: Array) -> None:
		for combatant_scene in combat_combatants:
			if not isinstance(combatant_scene, PackedScene):
				continue

			combatant = combatant_scene.instantiate()

			if combatant.get_name() in ("Player", "Opponent", "Combatant"):
				self.get_node("Combatants").call("add_combatant", combatant)

				health = combatant.get_node("Health")
				health.get("dead").connect(
					lambda c=combatant: self._on_combatant_death(c)
				)
			else:
				combatant.queue_free()

		self.ui.call("initialize")
		self.get_node("TurnQueue").get_pyscript().initialize()
	def clear_combat(self) -> None:
		for n in self.get_node("Combatants").get_children():
			n.queue_free()

		for n in self.ui.get_node("Combatants").get_children():
			n.queue_free()

	def finish_combat(self, winner, loser) -> None:
		self.combat_finished.emit(winner, loser)

	def _on_flee(self, winner, loser) -> None:
		self.finish_combat(winner, loser)

	def _on_combatant_death(self, combatant) -> None:
		winner = None
		combatants_node = self.get_node("Combatants")

		if combatant.name != "Player":
			winner = combatants_node.get_node("Player")
		else:
			for n in combatants_node.get_children():
				if n.name != "Player":
					winner = n
					break

		self.finish_combat(winner, combatant)
