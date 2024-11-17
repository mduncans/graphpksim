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
    def conc_func_generator(self, time, conc):
        def conc_func(self, t):
            return (time[t], conc[t], 0)
        return conc_func
    
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

        sim_results = extract_simulation_concs("simulated_results/simulation_results.csv")
        time = list(sim_results.keys())
        depot_concs = [concs[0] for concs in sim_results.values()]
        central_concs = [concs[1] for concs in sim_results.values()]
        periph_concs = [concs[2] for concs in sim_results.values()]
        
        max_conc = max(max(depot_concs), max(central_concs), max(periph_concs))
        # Create fill animation
        total_duration = 12
        num_frames = len(sim_results)
        frame_duration = total_duration / num_frames
        
        # Create graphs
        axes = Axes(
            x_range=[0, max(time), 24],
            y_range=[0, max_conc, max_conc / 5],
            x_length=4,
            y_length=2,
            axis_config={"include_tip": False}
        ).to_edge(UP).shift(0.25 * UP)

        depot_graph = axes.plot_line_graph(time, depot_concs, line_color=GREEN, vertex_dot_radius=0)
        central_graph = axes.plot_line_graph(time, central_concs, line_color=PINK, vertex_dot_radius=0)
        periph_graph = axes.plot_line_graph(time, periph_concs, line_color=BLUE, vertex_dot_radius=0)

        depot_dot = Dot(color=GREEN).move_to(axes.c2p(time[0], depot_concs[0]))
        central_dot = Dot(color=PINK).move_to(axes.c2p(time[0], central_concs[0]))
        periph_dot = Dot(color=BLUE).move_to(axes.c2p(time[0], periph_concs[0]))

        animations = []
        for i, (time, concs) in enumerate(sim_results.items()):
            
            animations.append(
                AnimationGroup(
                    circle_depot.animate.set_fill(GREEN, opacity=concs[0]/max_conc),
                    circle_central.animate.set_fill(PINK, opacity=concs[1]/max_conc),
                    circle_periph.animate.set_fill(BLUE, opacity=concs[2]/max_conc),

                    depot_dot.animate.move_to(axes.c2p(time, concs[0])),
                    central_dot.animate.move_to(axes.c2p(time, concs[1])),
                    periph_dot.animate.move_to(axes.c2p(time, concs[2])),

                    lag_ratio=0,  # Synchronous updates
                    run_time=frame_duration,
                )
            )

        self.play(
            Create(arrows[4]), Create(arrow_labels[4])
        )
        
        self.add(axes)
        self.add(depot_graph, central_graph, periph_graph)

        self.play(
            #FadeOut(arrows[4]), FadeOut(arrow_labels[4]),
            Succession(*animations)
        )
