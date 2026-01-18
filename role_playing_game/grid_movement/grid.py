from py4godot import gdclass
from py4godot.classes.TileMapLayer import TileMapLayer
from py4godot.classes.Node2D import Node2D
from py4godot.classes.core import NodePath, Vector2i, Vector2


@gdclass
class grid(TileMapLayer):

	ACTOR: int = 0
	OBSTACLE: int = 1
	OBJECT: int = 2

	dialogue_ui: NodePath = NodePath.new0()

	def _ready(self) -> None:
		for child in self.get_children():
			cell = self.local_to_map(child.position)
			self.set_cell(cell, child.get("type"), Vector2i.ZERO)

	def get_cell_pawn(self, cell: Vector2i, type_: int = ACTOR):
		for node in self.get_children():
			if node.get("type") != type_:
				continue

			if self.local_to_map(node.position) == cell:
				return node

		return None

	def request_move(self, pawn, direction: Vector2i) -> Vector2i:
		cell_start = self.local_to_map(pawn.position)
		cell_target = cell_start + Vector2i.new2(direction)

		cell_tile_id = self.get_cell_source_id(cell_target)

		# Empty cell
		if cell_tile_id == -1:
			self.set_cell(cell_target, self.ACTOR, Vector2i.ZERO)
			self.set_cell(cell_start, -1, Vector2i.ZERO)
			return self.map_to_local(cell_target)

		# Occupied cell
		if cell_tile_id in (self.OBJECT, self.ACTOR):
			target_pawn = self.get_cell_pawn(cell_target, cell_tile_id)

			if target_pawn is None:
				return Vector2.new0()

			if not target_pawn.has_node("DialoguePlayer"):
				return Vector2.new0()

			dialogue_ui_node = self.get_node(self.dialogue_ui)
			dialogue_ui_node.call(
				"show_dialogue",
				pawn,
				target_pawn.get_node("DialoguePlayer")
			)

		return Vector2.new0()
