from py4godot import gdclass
from py4godot.classes.Node3D import Node3D
from py4godot.classes.RenderingServer import RenderingServer
from py4godot.classes.DirectionalLight3D import DirectionalLight3D


@gdclass
class stage(Node3D):
	
	def __init__(self):
		super().__init__()
	
	def _ready(self) -> None:
		if RenderingServer.instance().get_current_rendering_method() == "gl_compatibility":
			# Use PCF13 shadow filtering to improve quality (Medium maps to PCF5 instead).
			RenderingServer.instance().directional_soft_shadow_filter_set_quality(
				RenderingServer.SHADOW_QUALITY_SOFT_HIGH
			)
			# Darken the light's energy to compensate for sRGB blending (without affecting sky rendering).
			directional_light = self.get_node("DirectionalLight3D")
			directional_light.sky_mode = DirectionalLight3D.SKY_MODE_SKY_ONLY
			
			new_light = directional_light.duplicate()
			new_light.light_energy = 0.25
			new_light.sky_mode = DirectionalLight3D.SKY_MODE_LIGHT_ONLY
			self.add_child(new_light)
