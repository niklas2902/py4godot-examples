import math

import random
from py4godot.classes import gdclass
from py4godot.classes.Node import Node
from py4godot.classes.ResourceLoader import ResourceLoader
from py4godot.classes.core import Vector2


def load_mob_scene(path):
	return ResourceLoader.instance().load(path)


@gdclass
class main(Node):
	mob_scene_path: str = "res://pymob.tscn"

	def _ready(self):
		self.score = 0
		self._score_timer = self.get_node("ScoreTimer")
		self._start_timer = self.get_node("StartTimer")
		self._mob_timer = self.get_node("MobTimer")
		self._music = self.get_node("Music")
		self._death_sound = self.get_node("DeathSound")
		self._hud = self.get_node("HUD")
		self._start_position = self.get_node("StartPosition")
		self._mob_scene = load_mob_scene(self.mob_scene_path)
		self._player = self.get_node("Player").get_pyscript()
		self.create_mob()

	def create_mob(self):
		return self._mob_scene.instantiate()

	def game_over(self):
		self._mob_timer.stop()
		self._score_timer.stop()
		self._hud.get_pyscript().show_game_over()
		self._music.stop()
		self._death_sound.play()

	def new_game(self):
		self.get_tree().call_group("mobs", "queue_free")
		self.score = 0
		self._player.start(self._start_position.position)
		self._start_timer.start()
		self._hud.get_pyscript().update_score(self.score)
		self._hud.get_pyscript().show_message("Get Ready")
		self._music.play()

	def _on_MobTimer_timeout(self):
		mob = self.create_mob()
		mob_spawn_location = self.get_node("MobPath/MobSpawnLocation")
		mob_spawn_location.progress_ratio = random.random()
		mob.position = mob_spawn_location.position
		direction: float = mob_spawn_location.rotation + math.pi / 2
		velocity: Vector2 = Vector2.new3(random.random() * 100 + 150, 0)
		mob.linear_velocity = velocity.rotated(direction)
		self.add_child(mob)

	def _on_ScoreTimer_timeout(self):
		self.score += 1
		self._hud.get_pyscript().update_score(self.score)

	def on_StartTimer_timeout(self):
		self._mob_timer.start()
		self._score_timer.start()
