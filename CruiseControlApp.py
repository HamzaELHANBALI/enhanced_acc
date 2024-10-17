"""
This file contains the CruiseControlApp which is the main application that runs the simulation and the GUI.

Author: Hamza El Hanbali
Date: 2024-07-28
"""

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import time
from car import Car

class CruiseControlApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Set up main window
        self.title("Cruise Control Simulation")
        self.geometry("1200x900")

        # Initialize car and simulation variables
        self.car = Car(current_speed=50, set_speed=50)
        self.time_step = 0.1
        self.start_time = time.time()

        self.time_history = []
        self.speed_history = []
        self.target_speed_history = []
        self.safe_distance_history = []
        self.object_position_history = []

        # Create and set up UI elements
        self.create_widgets()
        self.running = False

    def create_widgets(self):
        # Create a frame for control inputs
        control_frame = ctk.CTkFrame(self)
        control_frame.pack(pady=10, padx=10, fill="x")

        # Set Initial Speed
        initial_speed_label = ctk.CTkLabel(control_frame, text="Initial Speed (kph):")
        initial_speed_label.grid(row=0, column=0, padx=5, pady=5)
        self.initial_speed_entry = ctk.CTkEntry(control_frame)
        self.initial_speed_entry.grid(row=0, column=1, padx=5, pady=5)
        self.initial_speed_button = ctk.CTkButton(control_frame, text="Set Initial Speed", command=self.set_initial_speed)
        self.initial_speed_button.grid(row=0, column=2, padx=5, pady=5)

        # Set Speed
        set_speed_label = ctk.CTkLabel(control_frame, text="Set Speed (kph):")
        set_speed_label.grid(row=1, column=0, padx=5, pady=5)
        self.set_speed_entry = ctk.CTkEntry(control_frame)
        self.set_speed_entry.grid(row=1, column=1, padx=5, pady=5)
        self.set_speed_button = ctk.CTkButton(control_frame, text="Set Speed", command=self.set_speed)
        self.set_speed_button.grid(row=1, column=2, padx=5, pady=5)

        # Set Object Speed
        object_speed_label = ctk.CTkLabel(control_frame, text="Object Speed (kph):")
        object_speed_label.grid(row=2, column=0, padx=5, pady=5)
        self.object_speed_entry = ctk.CTkEntry(control_frame)
        self.object_speed_entry.grid(row=2, column=1, padx=5, pady=5)
        self.object_speed_button = ctk.CTkButton(control_frame, text="Set Object Speed", command=self.set_object_speed)
        self.object_speed_button.grid(row=2, column=2, padx=5, pady=5)

        # Set Object Distance
        object_distance_label = ctk.CTkLabel(control_frame, text="Object Distance (m):")
        object_distance_label.grid(row=3, column=0, padx=5, pady=5)
        self.object_distance_entry = ctk.CTkEntry(control_frame)
        self.object_distance_entry.grid(row=3, column=1, padx=5, pady=5)
        self.object_distance_button = ctk.CTkButton(control_frame, text="Set Object Distance", command=self.set_object_distance)
        self.object_distance_button.grid(row=3, column=2, padx=5, pady=5)

        # Start/Stop button
        self.toggle_button = ctk.CTkButton(control_frame, text="Start", command=self.toggle_simulation)
        self.toggle_button.grid(row=4, column=1, padx=5, pady=10)

        # Create Speed Label
        self.speed_label = ctk.CTkLabel(self, text="Current Speed: 0 kph", font=("Arial", 24))
        self.speed_label.pack(pady=10)

        # Set up Matplotlib figure and canvas
        self.figure, (self.ax_speed, self.ax_distance) = plt.subplots(2, 1, figsize=(7, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=ctk.BOTH, expand=True)

        # Configure plot lines and axes
        self.speed_line, = self.ax_speed.plot([], [], label='Current Speed')
        self.target_line, = self.ax_speed.plot([], [], label='Target Speed', linestyle='--')
        self.safe_line, = self.ax_distance.plot([], [], label='Safe Distance', linestyle='--')
        self.object_line, = self.ax_distance.plot([], [], label='Object Position')

        # Speed plot configuration
        self.ax_speed.set_ylim(0, 130)
        self.ax_speed.set_xlim(0, 60)
        self.ax_speed.set_xlabel('Time (s)')
        self.ax_speed.set_ylabel('Speed (kph)')
        self.ax_speed.set_title('Speed vs Time')
        self.ax_speed.legend()

        # Distance plot configuration
        self.ax_distance.set_ylim(0, 100)
        self.ax_distance.set_xlim(0, 60)
        self.ax_distance.set_xlabel('Time (s)')
        self.ax_distance.set_ylabel('Distance (m)')
        self.ax_distance.set_title('Safe Distance vs Object Position')
        self.ax_distance.legend()

    def toggle_simulation(self):
        if self.running:
            self.running = False
            self.toggle_button.configure(text="Start")
        else:
            self.running = True
            self.toggle_button.configure(text="Stop")
            self.start_time = time.time()
            self.run_simulation()

    def run_simulation(self):
        if self.running:
            current_time = time.time() - self.start_time
            current_speed, target_speed, d_safe = self.car.update_speed(self.time_step)
            self.speed_label.configure(text=f"Current Speed: {current_speed:.2f} kph")

            self.time_history.append(current_time)
            self.speed_history.append(current_speed)
            self.target_speed_history.append(target_speed)
            self.safe_distance_history.append(d_safe)

            # Update object position correctly when object speed is greater than car speed
            self.car.sensor_data.d_object = self.car.sensor_data.d_object + (self.car.sensor_data.s_object - self.car.current_speed) * self.time_step
            self.object_position_history.append(self.car.sensor_data.d_object)

            # Update the graph
            self.update_graph()

            # Schedule next update
            self.after(int(self.time_step * 1000), self.run_simulation)

    def update_graph(self):
        # Update speed and target speed lines
        self.speed_line.set_data(self.time_history, self.speed_history)
        self.target_line.set_data(self.time_history, self.target_speed_history)

        # Update safe distance and object position lines
        self.safe_line.set_data(self.time_history, self.safe_distance_history)
        self.object_line.set_data(self.time_history, self.object_position_history)

        # Adjust x-axis limits
        if self.time_history[-1] > 60:
            self.ax_speed.set_xlim(self.time_history[-1] - 60, self.time_history[-1])
            self.ax_distance.set_xlim(self.time_history[-1] - 60, self.time_history[-1])

        # Redraw canvas
        self.ax_speed.relim()
        self.ax_speed.autoscale_view()
        self.ax_distance.relim()
        self.ax_distance.autoscale_view()
        self.canvas.draw()

    def set_speed(self):
        try:
            speed = float(self.set_speed_entry.get())
            self.car.set_speed = speed
        except ValueError:
            print("Invalid speed value")

    def set_object_speed(self):
        try:
            speed = float(self.object_speed_entry.get())
            self.car.sensor_data.s_object = speed
        except ValueError:
            print("Invalid object speed value")

    def set_object_distance(self):
        try:
            distance = float(self.object_distance_entry.get())
            self.car.sensor_data.d_object = distance
        except ValueError:
            print("Invalid object distance value")

    def set_initial_speed(self):
        try:
            initial_speed = float(self.initial_speed_entry.get())
            self.car.current_speed = initial_speed
        except ValueError:
            print("Invalid initial speed value")
