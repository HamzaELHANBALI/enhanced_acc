"""
Cruise Control Application

Author: @Hamza EL HANBALI
Date: 12/10/2024
"""

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import time
from car import Car
from sensors import Sensors

class CruiseControlApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.title("Cruise Control Simulation")
        self.geometry("1200x900")

        # Get the target object speed and position from the sensor module
        self.target_object = Sensors()

        # Initialize car and simulation variables
        self.car = Car(target_speed=60)
        self.speed_history = []
        self.target_speed_history = []
        self.time_history = []
        self.time_step = 0.1  # 100ms
        self.start_time = time.time()

        # Create and set up UI elements
        self.create_widgets()

    def create_widgets(self):
        # Create speed display label
        self.speed_label = ctk.CTkLabel(self, text="Current Speed: 0 kph", font=("Arial", 24))
        self.speed_label.pack(pady=10)

        # Create target speed display and control buttons
        target_speed_frame = ctk.CTkFrame(self)
        target_speed_frame.pack(pady=10)

        self.set_minus_button = ctk.CTkButton(target_speed_frame, text="Set-", command=self.decrease_set_speed, width=60)
        self.set_minus_button.pack(side=ctk.LEFT, padx=5)

        self.target_speed_label = ctk.CTkLabel(target_speed_frame, text="Target Speed: 60 kph", width=150)
        self.target_speed_label.pack(side=ctk.LEFT, padx=5)

        self.set_plus_button = ctk.CTkButton(target_speed_frame, text="Set+", command=self.increase_set_speed, width=60)
        self.set_plus_button.pack(side=ctk.LEFT, padx=5)

        # Create a button to manually set the speed (always suppose target is on ego vehicle's lane)
        self.set_speed_button = ctk.CTkButton(self, text="Set TargetObject Speed", command=self.set_target_object_speed)
        self.set_speed_button.pack(pady=10)

        # Create a button to manually set the target longitudinal position (in meters)
        self.set_position_button = ctk.CTkButton(self, text="Set TargetObject Position", command=self.set_target_object_position)
        self.set_position_button.pack(pady=10)

        # Create Start/Stop button
        self.toggle_button = ctk.CTkButton(self, text="Start", command=self.toggle_simulation)
        self.toggle_button.pack(pady=10)

        # Set up Matplotlib figure and canvas
        self.figure, self.ax = plt.subplots(figsize=(7, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=ctk.BOTH, expand=True)

        # Configure plot lines and axes
        self.speed_line, = self.ax.plot([], [], label='Current Speed')
        self.target_line, = self.ax.plot([], [], label='Target Speed', linestyle='--')
        self.ax.set_ylim(0, 130)
        self.ax.set_xlim(0, 60)  # Show 60 seconds of data
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Speed (kph)')
        self.ax.set_title('Speed vs Time')
        self.ax.legend()

        self.running = False

    def target_speed_management(self):
        # Set target speed to the minimum of the driver's set speed and the target object speed (always regulate to the lowest speed)
        self.car.target_speed = min(self.car.set_speed, self.target_object.TargetObjectSpeed)

    def increase_set_speed(self):
        # Increase target speed by 1, up to a maximum of 130 kph
        self.car.set_speed = min(130, self.car.set_speed + 1)
        self.update_target_speed_label()

    def decrease_set_speed(self):
        # Decrease target speed by 1, down to a minimum of 0 kph
        self.car.set_speed = max(0, self.car.set_speed - 1)
        self.update_target_speed_label()

    def update_target_speed_label(self):
        # Update the target speed display
        self.target_speed_label.configure(text=f"Target Speed: {self.car.target_speed} kph")

    def toggle_simulation(self):
        if self.running:
            # Stop the simulation
            self.running = False
            self.toggle_button.configure(text="Start")
        else:
            # Start the simulation
            self.running = True
            self.toggle_button.configure(text="Stop")
            self.start_time = time.time()
            self.run_simulation()

    def run_simulation(self):
        if self.running:
            # Calculate current time and update car speed
            current_time = time.time() - self.start_time
            current_speed = self.car.update_speed(self.time_step)
            
            # Record speed, target speed, and time data
            self.speed_history.append(current_speed)
            self.target_speed_history.append(self.car.target_speed)
            self.time_history.append(current_time)

            # Update speed display
            self.speed_label.configure(text=f"Current Speed: {current_speed:.1f} kph")
            
            # Update the graph
            self.update_graph()

            # Schedule the next update
            self.after(int(self.time_step * 1000), self.run_simulation)

    def update_graph(self):
        # Update the data for both speed and target speed lines
        self.speed_line.set_data(self.time_history, self.speed_history)
        self.target_line.set_data(self.time_history, self.target_speed_history)
        
        # Adjust x-axis to show the last 60 seconds of data
        if self.time_history[-1] > 60:
            self.ax.set_xlim(self.time_history[-1] - 60, self.time_history[-1])
        
        # Recalculate the plot limits and redraw the canvas
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()
