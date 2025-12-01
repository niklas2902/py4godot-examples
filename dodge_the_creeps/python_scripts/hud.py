from py4godot import signal
from py4godot.classes import gdclass
from py4godot.classes.CanvasLayer import CanvasLayer


@gdclass
class hud(CanvasLayer):
	start_game = signal([])

	def show_message(self, text: str) -> None:
		message_label = self.get_node("MessageLabel")
		message_timer = self.get_node("MessageTimer")

		message_label.text = text
		message_label.show()
		message_timer.start()

	def show_game_over(self) -> None:
		message_timer = self.get_node("MessageTimer")
		self.show_message("Game Over")
		message_timer.timeout.connect(self.show_title)

	def show_title(self):
		message_label = self.get_node("MessageLabel")
		message_label.text = "Dodge the\nCreeps"
		message_label.show()
		self.get_tree().create_timer(1).timeout.connect(self.show_start_button)
		self.get_node("MessageTimer").timeout.disconnect(self.show_title)

	def show_start_button(self):
		start_button = self.get_node("StartButton")
		start_button.show()

	def update_score(self, score: int) -> None:
		score_label = self.get_node("ScoreLabel")
		score_label.text = f"{score}"

	def _on_StartButton_pressed(self) -> None:
		start_button = self.get_node("StartButton")
		start_button.hide()
		self.start_game.emit()

	def _on_MessageTimer_timeout(self) -> None:
		message_label = self.get_node("MessageLabel")
		message_label.hide()
