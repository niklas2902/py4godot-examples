from py4godot.classes import gdclass
from py4godot.classes.DisplayServer import DisplayServer
from py4godot.classes.Input import Input
from py4godot.classes.VehicleBody3D import VehicleBody3D
from py4godot.functions import absf, lerpf, is_zero_approx, clampf, move_toward

STEER_SPEED = 1.5
STEER_LIMIT = 0.4
BRAKE_STRENGTH = 2.0

@gdclass
class vehicle(VehicleBody3D):
	engine_force_value:float = 40.


	def _ready(self) -> None:
		self.previous_speed = self.linear_velocity.length()
		self._steer_target = 0.0
		self.desired_engine_pitch: float = self.get_node("EngineSound").pitch_scale
	
	def _physics_process(self, delta:float) -> None:
		self._steer_target = Input.instance().get_axis("turn_right", "turn_left")
		self._steer_target *= STEER_LIMIT

		# Engine sound simulation (not realistic, as this car script has no notion of gear or engine RPM).
		desired_engine_pitch = 0.05 + self.linear_velocity.length() / (self.engine_force_value * 0.5)
		# Change pitch smoothly to avoid abrupt change on collision.
		self.get_node("EngineSound").pitch_scale = lerpf(self.get_node("EngineSound").pitch_scale, desired_engine_pitch, 0.2)

		if absf(self.linear_velocity.length() - self.previous_speed) > 1.0:
			# Sudden velocity change, likely due to a collision. Play an impact sound to give audible feedback,
			# and vibrate for haptic feedback.
			self.get_node("ImpactSound").play()
			Input.instance().vibrate_handheld(100)
			for joypad in Input.instance().get_connected_joypads():
				Input.instance().start_joy_vibration(joypad, 0.0, 0.5, 0.1)

		# Automatically accelerate when using touch controls (reversing overrides acceleration).
		if DisplayServer.instance().is_touchscreen_available() or Input.instance().is_action_pressed("accelerate"):
			# Increase engine force at low speeds to make the initial acceleration faster.
			speed = self.linear_velocity.length()
			if speed < 5.0 and not is_zero_approx(speed):
				self.engine_force = clampf(self.engine_force_value * 5.0 / speed, 0.0, 100.0)
			else:
				self.engine_force = self.engine_force_value

			if not DisplayServer.instance().is_touchscreen_available():
				# Apply analog throttle factor for more subtle acceleration if not fully holding down the trigger.
				self.engine_force *= Input.instance().get_action_strength("accelerate")
		else:
			self.engine_force = 0.0

		if Input.instance().is_action_pressed("reverse"):
			# Increase engine force at low speeds to make the initial reversing faster.
			speed = self.linear_velocity.length()
			if speed < 5.0 and not is_zero_approx(speed):
				self.engine_force = -clampf(self.engine_force_value * BRAKE_STRENGTH * 5.0 / speed, 0.0, 100.0)
			else:
				self.engine_force = -self.engine_force_value * BRAKE_STRENGTH

			# Apply analog brake factor for more subtle braking if not fully holding down the trigger.
			self.engine_force *= Input.instance().get_action_strength("reverse")

		self.steering = move_toward(self.steering, self._steer_target, STEER_SPEED * delta)

		self.previous_speed = self.linear_velocity.length()
