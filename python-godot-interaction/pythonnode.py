from py4godot.classes import gdclass
from py4godot.classes.Node2D import Node2D

@gdclass
class pythonnode(Node2D):
		
	def _ready(self) -> None:
		pass
		# put initialization code here
		self.csharpnode = self.get_node("../csharpnode")
		print(self.csharpnode.name)
		self.csharpnode.call_thread_safe("Calledfrompython", "hello world from py4godot")
