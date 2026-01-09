using Godot;

public partial class Csharpnode : Node2D
{
    public Label label;
    public override void _Ready()
    {
        label = GetNode<Label>("Label");
    }
    public void Calledfrompython(string s)
    {
        label.Text = s;
    }

}
