import os
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from scipy.integrate import solve_ivp
from matplotlib.widgets import Slider, Button, TextBox


class CompartmentalModelSimulator:

    def __init__(self, n_samples = 20, Ka = 0.5, Q = 1.3, Vc = 20, Vp = 10, CL = 0.75):
        # Initialize sampled means and spreads for each parameter
        self.n_samples = n_samples
        self.initial_means = {
            "K_a": Ka,
            "Q": Q,
            "V_c": Vc,
            "V_p": Vp,
            "CL": CL,
        }
        self.std_dev_values = {
            "K_a": 0.125,
            "Q": 0.325,
            "V_c": 5.0,
            "V_p": 2.5,
            "CL": 0.2,
        }
        self.sampled_means = self._generate_samples()

        # Define nominal sampling times and fixed jitter
        self.nominal_times = np.array([0, 0.5, 1, 2, 4, 6, 8, 12, 16, 24, 36, 48, 72, 96, 120])
        self.fixed_jitter = [
            self.nominal_times + np.random.uniform(-1.5, 1.5, size=self.nominal_times.shape) for _ in range(self.n_samples)
        ]

        # Set up the figure and axes
        self.fig, self.ax = plt.subplots(figsize=(10, 6))  # Standard figure size
        plt.subplots_adjust(left=0.1, bottom=0.35)  # Ensure enough space below the plot for sliders

        # Slider axes for means and standard deviations
        slider_color = 'lightgoldenrodyellow'
        slider_width = 0.35  # 35% of the figure width

        # Means (left column)
        ax_Ka_mean = plt.axes([0.1, 0.24, slider_width, 0.03], facecolor=slider_color)
        ax_Q_mean = plt.axes([0.1, 0.19, slider_width, 0.03], facecolor=slider_color)
        ax_Vc_mean = plt.axes([0.1, 0.14, slider_width, 0.03], facecolor=slider_color)
        ax_Vp_mean = plt.axes([0.1, 0.09, slider_width, 0.03], facecolor=slider_color)
        ax_CL_mean = plt.axes([0.1, 0.04, slider_width, 0.03], facecolor=slider_color)

        # Standard deviations (right column)
        ax_Ka_sd = plt.axes([0.55, 0.24, slider_width, 0.03], facecolor=slider_color)
        ax_Q_sd = plt.axes([0.55, 0.19, slider_width, 0.03], facecolor=slider_color)
        ax_Vc_sd = plt.axes([0.55, 0.14, slider_width, 0.03], facecolor=slider_color)
        ax_Vp_sd = plt.axes([0.55, 0.09, slider_width, 0.03], facecolor=slider_color)
        ax_CL_sd = plt.axes([0.55, 0.04, slider_width, 0.03], facecolor=slider_color)

        # Create sliders for means and standard deviations
        self.slider_Ka_mean = Slider(ax_Ka_mean, 'K_a Mean', 0.1, 2.0, valinit=self.initial_means["K_a"])
        self.slider_Q_mean = Slider(ax_Q_mean, 'Q Mean', 0.1, 5.0, valinit=self.initial_means["Q"])
        self.slider_Vc_mean = Slider(ax_Vc_mean, 'V_c Mean', 5.0, 50.0, valinit=self.initial_means["V_c"])
        self.slider_Vp_mean = Slider(ax_Vp_mean, 'V_p Mean', 5.0, 50.0, valinit=self.initial_means["V_p"])
        self.slider_CL_mean = Slider(ax_CL_mean, 'CL Mean', 0.1, 2.0, valinit=self.initial_means["CL"])

        self.slider_Ka_sd = Slider(ax_Ka_sd, 'K_a SD', 0.01, 0.5, valinit=self.std_dev_values["K_a"])
        self.slider_Q_sd = Slider(ax_Q_sd, 'Q SD', 0.01, 1.25, valinit=self.std_dev_values["Q"])
        self.slider_Vc_sd = Slider(ax_Vc_sd, 'V_c SD', 0.5, 12.5, valinit=self.std_dev_values["V_c"])
        self.slider_Vp_sd = Slider(ax_Vp_sd, 'V_p SD', 0.5, 12.5, valinit=self.std_dev_values["V_p"])
        self.slider_CL_sd = Slider(ax_CL_sd, 'CL SD', 0.01, 0.5, valinit=self.std_dev_values["CL"])

        # Attach the update function to the sliders
        self.sliders = [
            self.slider_Ka_mean, self.slider_Q_mean, self.slider_Vc_mean, self.slider_Vp_mean, self.slider_CL_mean,
            self.slider_Ka_sd, self.slider_Q_sd, self.slider_Vc_sd, self.slider_Vp_sd, self.slider_CL_sd
        ]

        for slider in self.sliders:
            slider.on_changed(self.update)
        
        # Add input box for n_samples
        self.n_samples_box_ax = plt.axes([0.2, 0.9, 0.1, 0.05])  # Position left of the save button
        self.n_samples_box = TextBox(
            self.n_samples_box_ax, 
            label="Samples:", 
            initial=str(self.n_samples)
        )
        self.n_samples_box.on_submit(self.update_n_samples)

        # Add a TextBox for file name input
        self.file_name_box_ax = plt.axes([0.4, 0.9, 0.25, 0.05])  # Position for file name TextBox
        self.file_name_box = TextBox(
            self.file_name_box_ax,
            label="File Name: ",
            initial="simulation_results.csv",
        )

        # Add a button to save plotted points to a CSV
        self.save_button_ax = plt.axes([0.675, 0.9, 0.1, 0.05])  # Position above the plot
        self.save_button = Button(self.save_button_ax, 'Save to CSV', color='lightblue', hovercolor='dodgerblue')
        self.save_button.on_clicked(self.save_to_csv)

        # Initial plot
        self.plot_simulation()

        plt.show()

    def _generate_samples(self):
        return {
            param: np.random.normal(self.initial_means[param], self.std_dev_values[param], self.n_samples)
            for param in self.initial_means
        }
    
    def _generate_fixed_jitter(self):
        return [
            self.nominal_times + np.random.uniform(-1.5, 1.5, size=self.nominal_times.shape)
            for _ in range(self.n_samples)
        ]

    def update_n_samples(self, text):
        try:
            n_samples = int(text)
            if n_samples > 0:
                self.n_samples = n_samples
                self.sampled_means = self._generate_samples()
                self.fixed_jitter = self._generate_fixed_jitter()
                self.plot_simulation()
            else:
                print("Number of samples must be greater than 0.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

    # Define the out-degree Laplacian matrix L
    def laplacian_out_matrix(self, K_a, Q, V_c, V_p, CL):
        self.L = np.array([
            [K_a, -K_a, 0, 0],  # Gut compartment (flows out to central)
            [0, (Q / V_c + CL / V_c), -Q / V_c, -CL / V_c],  # Central compartment (Vc)
            [0, -Q / V_p, Q / V_p, 0],  # Peripheral compartment (Vp)
            [0, 0, 0, 0],  # Elimination compartment (R) has no outflow
        ])

    # Define the system of ODEs
    def model(self, t, y):
        dydt = -self.L.T @ y
        return dydt
    
    def simulate_with_solve_ivp(self, t_span, y0):
        dense_t = np.linspace(t_span[0], t_span[1], 1000)  # Dense evaluation points
        solution = solve_ivp(
            self.model, 
            t_span=t_span, 
            y0=y0,  
            dense_output=True,
            t_eval=dense_t
        )
        return solution.t, solution.y.T

    def plot_simulation(self, initial_dose=50.0, total_time=120):
        # Clear the current figure
        self.ax.clear()
        self.plot_results = []

        for i in range(self.n_samples):
            # Define Laplacian matrix for each sample
            L = self.laplacian_out_matrix(
                self.sampled_means["K_a"][i],
                self.sampled_means["Q"][i],
                self.sampled_means["V_c"][i],
                self.sampled_means["V_p"][i],
                self.sampled_means["CL"][i],
            )
            t_eval, results = self.simulate_with_solve_ivp((0, total_time), [initial_dose, 0, 0, 0])

            # Extract central compartment concentration
            central_concentration = results[:, 1]
            self.plot_results.append(central_concentration)

            # Plot dense line for the central compartment
            self.ax.plot(t_eval, central_concentration, color=plt.get_cmap("tab10")(0), alpha=0.3)

            # Use the precomputed fixed jitter for sampling times
            jittered_times = np.clip(self.fixed_jitter[i], 0, total_time)  # Ensure times are within bounds
            jittered_indices = np.searchsorted(t_eval, jittered_times)  # Map jittered times to dense evaluation
            jittered_concentrations = central_concentration[jittered_indices]

            # Plot jittered points
            self.ax.scatter(jittered_times, jittered_concentrations, color=plt.get_cmap("tab10")(0), alpha=0.8, s=10)

        # Add the image of the compartmental model in the upper right corner
        inset_ax = self.ax.inset_axes([0.62, 0.58, 0.4, 0.4], transform=self.ax.transAxes)  # Adjust position and size
        inset_ax.axis("off")  # Remove axes for the inset
        model_image = mpimg.imread("model.png")  # Load your image
        inset_ax.imshow(model_image)

        # Finalize plot
        self.ax.set_xlabel("Time (hr)")
        self.ax.set_ylabel("Central Compartment Concentration (mg/L)")
        plt.draw()

    def update_spread(self, param, new_sd):
        """Update the spread of sampled means based on new standard deviation."""
        self.sampled_means
        mean_value = np.mean(self.sampled_means[param])
        deviations = self.sampled_means[param] - mean_value
        if np.sum(np.abs(deviations)) > 0:  # Avoid division by zero
            normalized_deviations = deviations / np.std(deviations)
        else:
            normalized_deviations = np.zeros_like(deviations)
        self.sampled_means[param] = mean_value + normalized_deviations * new_sd

    # Update function for sliders
    def update(self, val):
        # Update sampled means proportionally for mean sliders
        for param, slider in zip(["K_a", "Q", "V_c", "V_p", "CL"], 
                                 [self.slider_Ka_mean, self.slider_Q_mean, self.slider_Vc_mean, self.slider_Vp_mean, self.slider_CL_mean]):
            delta = slider.val - np.mean(self.sampled_means[param])
            self.sampled_means[param] += delta

        # Update spread based on SD sliders
        for param, slider in zip(["K_a", "Q", "V_c", "V_p", "CL"], 
                                 [self.slider_Ka_sd, self.slider_Q_sd, self.slider_Vc_sd, self.slider_Vp_sd, self.slider_CL_sd]):
            self.update_spread(param, slider.val)

        self.plot_simulation()
    
    # Save the plotted points to a CSV
    def save_to_csv(self, event):
        """Saves the nominal times, actual times, concentrations, and parameters to a CSV file."""
        file_name = self.file_name_box.text.strip()  # Get the file name from the TextBox
        if not file_name.endswith(".csv"):
            file_name += ".csv"

        with open(os.path.join("simulated_results", file_name), "w", newline="") as csvfile:
            writer = csv.writer(csvfile)

            # Write the header with parameter columns
            writer.writerow([
                "ID", "Nominal Time", "Actual Time", "Concentration",
                "K_a", "Q", "V_c", "V_p", "CL"
            ])

            # Write data for each sample
            for i in range(self.n_samples):
                params = [
                    self.sampled_means["K_a"][i],
                    self.sampled_means["Q"][i],
                    self.sampled_means["V_c"][i],
                    self.sampled_means["V_p"][i],
                    self.sampled_means["CL"][i],
                ]
                for nominal_time, actual_time, concentration in zip(
                    self.nominal_times, self.fixed_jitter[i], self.plot_results[i]
                ):
                    writer.writerow([i + 1, nominal_time, actual_time, concentration, *params])
        print(f"Results saved to {file_name}")



if __name__ == "__main__":
    simulator = CompartmentalModelSimulator()
    simulator.plot_simulation()
