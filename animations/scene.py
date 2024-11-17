from manim import *

run_time = 1

class CompartmentalModel(Scene):
    def construct(self):
        # Compartments
        circle_depot = Circle(color = GREEN).shift(3.8 * LEFT)
        circle_central = Circle(color = PINK)
        circle_periph = Circle(color = BLUE).shift(4 * RIGHT)

        # Arrows
        arrows = [
            Line(2.8 * LEFT, 1.0 * LEFT)
                .add_tip(tip_width = 0.1, tip_length = 0.2), 
            Line(1.0 * DOWN, 2.8 * DOWN)
                .add_tip(tip_width = 0.1, tip_length = 0.2),
            ArcBetweenPoints(.78 * RIGHT, 3.2 * RIGHT, radius = -5)
                .shift(0.6 * UP)
                .add_tip(tip_width = 0.1, tip_length = 0.2),
            ArcBetweenPoints(3.2 * RIGHT, .78 * RIGHT, radius = -5)
                .shift(0.6 * DOWN)
                .add_tip(tip_width = 0.1, tip_length= 0.2),
            Arrow(start = 3.8 * LEFT + 2.8 * UP, end = 3.8 * LEFT + 0.4 * DOWN, 
                  tip_shape = ArrowCircleFilledTip)
                  .scale(0.5, scale_tips = True)
        ]
        arrow_labels = [
            MathTex(r"K_A").shift(2. * LEFT + 0.4 * UP),
            MathTex(r"CL/V_c").shift(1.8 * DOWN + .8 * LEFT),
            MathTex(r"Q/V_c").shift(2 * RIGHT + 1.1 * UP),
            MathTex(r"Q/V_p").shift(2 * RIGHT + 1.1 * DOWN),
            Text(r"Dose").shift(3.8 * LEFT + 2.5 * UP)
        ]   
        
        # Play
        self.play(
            Create(circle_depot), 
        )

        self.play(
            Create(arrows[0]), Create(arrow_labels[0]), 
            Create(circle_central), 
            run_time = run_time
        )

        self.play(
            Create(arrows[1]), Create(arrow_labels[1]),
            run_time = run_time 
        )
        
        self.play(
            Create(circle_periph),
            Create(arrows[2]), Create(arrow_labels[2]),
            Create(arrows[3]), Create(arrow_labels[3]),
            run_time = run_time
        )

        self.play(
            Create(arrows[4]), Create(arrow_labels[4])
        )