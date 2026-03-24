from py4godot import gdclass
from py4godot.classes.Node import Node
from py4godot.classes.FileAccess import FileAccess, ModeFlags
from py4godot.classes.JSON import JSON
from py4godot.classes.core import String
from py4godot.signals import signal


@gdclass
class dialogue_player(Node):

	dialogue_started = signal([])
	dialogue_finished = signal([])

	dialogue_file: str = ""
	
	dialogue_name:str = ""
	dialogue_text:str = ""

	def __init__(self):
		super().__init__()
		self.dialogue_keys = []
		self.dialogue_name = ""
		self.current = 0
		self.dialogue_text = ""

	def start_dialogue(self) -> None:
		self.dialogue_started.emit()
		self.current = 0
		self.index_dialogue()

		if not self.dialogue_keys:
			self.dialogue_finished.emit()
			return

		entry = self.dialogue_keys[self.current]
		self.dialogue_text = entry.get("text", "")
		self.dialogue_name = entry.get("name", "")

	def next_dialogue(self) -> None:
		self.current += 1

		if self.current == len(self.dialogue_keys):
			self.dialogue_finished.emit()
			return

		entry = self.dialogue_keys[self.current]
		self.dialogue_text = entry.get("text", "")
		self.dialogue_name = entry.get("name", "")

	def index_dialogue(self) -> None:
		dialogue = self.load_dialogue(self.dialogue_file)
		self.dialogue_keys.clear()

		for key in dialogue.keys():
			self.dialogue_keys.append(dialogue[key])

	def load_dialogue(self, file_path: String):
		file = FileAccess.open(file_path, ModeFlags.READ)

		if file:
			json_parser = JSON.new()
			err = json_parser.parse(file.get_as_text())

			if err == 0:
				return json_parser.data

		return {}
