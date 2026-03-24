from py4godot import gdclass, gdproperty
from py4godot.classes.PackedScene import PackedScene
from py4godot.classes.ResourceLoader import ResourceLoader
from py4godot.classes.SpriteFrames import SpriteFrames
from py4godot.classes.TileMapLayer import TileMapLayer
from py4godot.classes.core import Vector2
from py4godot.classes.Tween import Tween, EaseType
from py4godot.classes.Node2D import Node2D
from py4godot.classes.AnimationNodeStateMachinePlayback import (
	AnimationNodeStateMachinePlayback,
)
from py4godot.classes.Object import ConnectFlags


@gdclass
class walker(Node2D): 
	combat_actor_path = gdproperty(str, "")
	pose_anims_path = gdproperty(str, "")

	def __init__(self):
		super().__init__()
		self.lost = False
		self.grid_size = 0.0

		self.grid = None
		self.animation_playback = None
		self.walk_animation_time = 0.0
		self.pose = None

	def _ready(self) -> None:
		# @onready replacements
		self.grid = self.get_parent()
		self.combat_actor = ResourceLoader.instance().load(self.combat_actor_path)
		self.pose_anims = ResourceLoader.instance().load(self.pose_anims_path)

		self.animation_playback = (
			self.get_node("AnimationTree")
			.get("parameters/playback")
		)

		animation_player = self.get_node("AnimationPlayer")
		walk_anim = animation_player.get_animation("walk")
		self.walk_animation_time = walk_anim.length

		self.pose = self.get_node("Pivot/Slime")

		# Setup
		if self.pose_anims is not None:
			self.pose.sprite_frames = self.pose_anims

		self.update_look_direction(Vector2.RIGHT)
		self.grid_size = self.grid.tile_set.tile_size.x

	def update_look_direction(self, direction: Vector2) -> None:
		self.get_node("Pivot/FacingDirection").rotation = direction.angle()

	def move_to(self, target_position: Vector2) -> None:
		self.set_process(False)

		move_direction = (target_position - self.position).normalized()

		self.pose.play("idle")
		self.animation_playback.start("walk")

		tween = self.create_tween()
		tween.set_ease(EaseType.EASE_IN)

		end = self.get_node("Pivot").position + move_direction * self.grid_size
		tween.tween_property(
			self.get_node("Pivot"),
			"position",
			end,
			self.walk_animation_time,
		)

		def on_tween_finished():
			self.get_node("Pivot").position = Vector2.ZERO
			self.position = target_position
			self.animation_playback.start("idle")
			self.pose.play("idle")
			self.set_process(True)

		tween.finished.connect(
			on_tween_finished,
			ConnectFlags.CONNECT_ONE_SHOT
		)

	def bump(self) -> None:
		self.set_process(False)

		self.pose.play("bump")
		self.animation_playback.start("bump")

		def on_bump_finished(_anim_name=None):
			self.animation_playback.start("idle")
			self.pose.play("idle")
			self.set_process(True)

		self.get_node("AnimationTree").animation_finished.connect(
			on_bump_finished,
			ConnectFlags.CONNECT_ONE_SHOT
		)
