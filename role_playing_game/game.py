from py4godot import gdclass
from py4godot.classes.AnimationPlayer import AnimationPlayer
from py4godot.classes.Node import Node
from py4godot.classes.Node2D import Node2D
from py4godot.classes.ResourceLoader import ResourceLoader
from py4godot.classes.core import NodePath, Array
from py4godot.classes.Object import ConnectFlags


def load_scene(path):
	return ResourceLoader.instance().load(path)


# Constants
PLAYER_WIN: str = "res://dialogue/dialogue_data/player_won.json"
PLAYER_LOSE: str = "res://dialogue/dialogue_data/player_lose.json"
@gdclass
class game(Node):

	combat_screen:Node
	exploration_screen:Node

	_animation_player: AnimationPlayer

	def __init__(self):
		super().__init__()

	def _ready(self) -> None:
		self._animation_player = self.get_node("AnimationPlayer")
		self.combat_screen.get("combat_finished").connect(self._on_combat_finished)
		self.combat_actors = None
		self.dialogue = None

		grid = self.get_node("Exploration/Grid")
		for n in grid.get_children():
			type_ = n.get_pyscript().type
			if not type_ == 0:
				continue
			if not n.has_node("DialoguePlayer"):
				continue
			dialogue_player = n.get_node("DialoguePlayer")
			dialogue_player.get_pyscript().dialogue_finished.connect(lambda opp=n:self._on_opponent_dialogue_finished(opp))

		self.remove_child(self.combat_screen)

	def start_combat(self, combat_actors) -> None:
		self._animation_player.play("fade_to_black")
		def fun(_):
			exploration = self.get_node("Exploration")
			self.remove_child(exploration)
			self.add_child(self.combat_screen)

			self.combat_screen.get_pyscript().initialize(combat_actors)
			self.combat_screen.show()
			self._animation_player.play_backwards("fade_to_black")
		self._animation_player.animation_finished.connect(fun, ConnectFlags.CONNECT_ONE_SHOT)
		self.combat_actors = combat_actors



	def _on_opponent_dialogue_finished(self, opponent) -> None:
		if opponent.get("lost"):
			return

		player = self.get_node("Exploration/Grid/Player")
		combatants = Array.from_list([player.get_pyscript().combat_actor, opponent.get_pyscript().combat_actor])
		self.start_combat(combatants)

	def _on_combat_finished(self, winner, _loser) -> None:
		self.remove_child(self.combat_screen)
		self._animation_player.play_backwards("fade_to_black")
		self.add_child(self.exploration_screen)

		dialogue_scene = load_scene("res://dialogue/dialogue_player/dialogue_player.tscn")
		dialogue = dialogue_scene.instantiate()

		if winner.name == "Player":
			dialogue.set("dialogue_file", PLAYER_WIN)
		else:
			dialogue.set("dialogue_file", PLAYER_LOSE)

		def on_combat_winner_finished(_):
			player = self.get_node("Exploration/Grid/Player")
			dialogue_ui = self.exploration_screen.get_node("DialogueCanvas/DialogueUI")
			dialogue_ui.get_pyscript().show_dialogue(player, dialogue)
			self.combat_screen.get_pyscript().clear_combat()
			dialogue.get_pyscript().dialogue_finished.connect(lambda:dialogue.queue_free, ConnectFlags.CONNECT_ONE_SHOT)
		self._animation_player.animation_finished.connect(on_combat_winner_finished, ConnectFlags.CONNECT_ONE_SHOT)
