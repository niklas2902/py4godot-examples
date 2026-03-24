from py4godot import gdclass
from py4godot.classes.Control import Control
from py4godot.classes.PackedScene import PackedScene
from py4godot.classes.Node import Node
from py4godot.classes.core import NodePath
from py4godot.classes.ResourceLoader import ResourceLoader
from py4godot.classes.Object import Object
from py4godot.signals import signal, SignalArg


@gdclass
class ui(Control):
	flee = signal([
		SignalArg("winner", Object),
		SignalArg("loser", Object)
	])
	combatants: Node
	info_scene: PackedScene = PackedScene.new()
	
	def initialize(self) -> None:

		for combatant in self.combatants.get_children():
			health = combatant.get_node("Health")
			info = self.info_scene.instantiate()

			health_info = info.get_node("VBoxContainer/HealthContainer/Health")
			health_info.set("value", health.get("life"))
			health_info.set("max_value", health.get("max_life"))

			info.get_node("VBoxContainer/NameContainer/Name").set(
				"text", combatant.get_name()
			)

			health.get("health_changed").connect(
				health_info.set_value
			)

			self.get_node("Combatants").add_child(info)

		self.get_node("Buttons/GridContainer/Attack").grab_focus()

	def _on_Attack_button_up(self) -> None:
		player = self.combatants.get_node("Player")

		if not player.get("active"):
			return

		player.call("attack", self.combatants.get_node("Opponent"))

	def _on_Defend_button_up(self) -> None:
		player = self.combatants.get_node("Player")

		if not player.get("active"):
			return

		player.call("defend")

	def _on_Flee_button_up(self) -> None:
		player = self.combatants.get_node("Player")

		if not player.get("active"):
			return

		player.call("flee")

		loser = player
		winner = self.combatants.get_node("Opponent")
		self.flee.emit(winner, loser)
