from manim import *
import csv

run_time = 1

def extract_simulation_concs(file_path):
    data_dict = {}

    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)  
        for row in reader:
            time = float(row["Time (hr)"])
            concentrations = [
                float(row["Depot Concentration"]),
                float(row["Central Concentration"]),
                float(row["Peripheral Concentration"]),
            ]
            data_dict[time] = concentrations

    return data_dict

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

        self.wait(1)

        self.play(
            Create(arrows[4]), Create(arrow_labels[4])
        )

        sim_results = extract_simulation_concs("simulated_results/simulation_results.csv")
        max_depot = max(concs[0] for concs in sim_results.values())
        max_central = max(concs[1] for concs in sim_results.values())
        max_periph = max(concs[2] for concs in sim_results.values())
        
        max_conc = max(max_depot, max_central, max_periph)
        
        total_duration = 20
        num_frames = len(sim_results)
        frame_duration = total_duration / num_frames
        # Create animations for each time step
        animations = []
        for i, (t, concs) in enumerate(sim_results.items()):
            if i == 0:
                self.play(
                    FadeOut(arrows[4]),
                    FadeOut(arrow_labels[4])
                )

            animations.append(
                AnimationGroup(
                    circle_depot.animate.set_fill(GREEN, opacity=concs[0]/max_conc),
                    circle_central.animate.set_fill(PINK, opacity=concs[1]/max_conc),
                    circle_periph.animate.set_fill(BLUE, opacity=concs[2]/max_conc),
                    lag_ratio=0,  # Synchronous updates
                    run_time=frame_duration,
                )
            )
        self.play(Succession(*animations))
