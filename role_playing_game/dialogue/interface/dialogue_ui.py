from py4godot import gdclass
from py4godot.classes.Control import Control
from py4godot.classes.Object import Object, ConnectFlags
from py4godot.classes.core import Callable


@gdclass
class dialogue_ui(Control):

	def __init__(self):
		super().__init__()
		self.dialogue_node = None

	def _ready(self) -> None:
		self.visible = False

	def show_dialogue(self, player, dialogue) -> None:
		self.visible = True
		self.get_node("Button").grab_focus()
		self.dialogue_node = dialogue

		for c in dialogue.get_signal_connection_list("dialogue_started"):
			callable_ = c.get("callable")
			if callable_.get_object() == player:
				self.dialogue_node.call("start_dialogue")
				self._update_text()
				return

		self.dialogue_node.get("dialogue_started").connect(
			lambda: player.call("set_active", False), ConnectFlags.CONNECT_ONE_SHOT
		)
		def dialogue_finished():
			self.hide()
			player.call("set_active", True)
		self.dialogue_node.get("dialogue_finished").connect(
			dialogue_finished, ConnectFlags.CONNECT_ONE_SHOT
		)

		self.dialogue_node.call("start_dialogue")
		self._update_text()


	def _on_Button_button_up(self) -> None:
		if self.dialogue_node is None:
			return

		self.dialogue_node.call("next_dialogue")
		self._update_text()

	def _update_text(self) -> None:
		self.get_node("Name").set(
			"text",
			"[center]" + self.dialogue_node.get("dialogue_name") + "[/center]"
		)
		self.get_node("Text").set(
			"text",
			self.dialogue_node.get("dialogue_text")
		)
