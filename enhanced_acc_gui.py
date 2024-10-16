import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import time

class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0
        self.prev_error = 0

    def compute_throttle(self, error, time_step):
        self.integral += error * time_step
        derivative = (error - self.prev_error) / time_step
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.prev_error = error
        return output

class Sensors:
    def __init__(self, time_step, s_object, d_object):
        self.is_object_ahead = True
        self.s_object = s_object
        self.d_object = d_object
        self.time_step = time_step

class Car:
    def __init__(self, current_speed, set_speed, time_step=0.1):
        self.sensor_data = Sensors(time_step=time_step, s_object=30, d_object=30)
        self.pid_controller = PIDController(kp=0.8, ki=0, kd=0)
        self.current_speed = current_speed
        self.set_speed = set_speed

    def compute_safe_distance(self):
        reaction_time = 1.5
        comfortable_deceleration = 4
        reaction_distance = self.current_speed * (1000 / 3600) * reaction_time
        braking_distance = (self.current_speed * (1000 / 3600))**2 / (2 * comfortable_deceleration)
        return reaction_distance + braking_distance

    def update_speed(self, time_step):

        # TODO: Obj must be within a distance to be considered ahead and consider its speed
        # Compute the safe distance
        d_safe = self.compute_safe_distance()
        d_error = self.sensor_data.d_object - d_safe
        
        # Fix the target speed logic
        if d_error < 0:
            # If d_error is negative, slow down (reduce target speed)
            s_target_desired = self.sensor_data.s_object - 2
        else:
            s_target_desired = min(self.set_speed, self.sensor_data.s_object)

        # Implement rate limiter for s_target_desired
        max_change = 2  # Maximum change allowed in m/s
        previous_target = getattr(self, 'previous_target', self.current_speed)
        
        # Convert speeds from kph to m/s for calculation
        current_target_ms = s_target_desired * (1000 / 3600)
        previous_target_ms = previous_target * (1000 / 3600)
        
        # Limit the change
        if abs(current_target_ms - previous_target_ms) > max_change:
            if current_target_ms > previous_target_ms:
                current_target_ms = previous_target_ms + max_change
            else:
                current_target_ms = previous_target_ms - max_change
        
        # Convert back to kph
        s_target_desired = current_target_ms * (3600 / 1000)
        
        # Store the new target for next iteration
        self.previous_target = s_target_desired

        print(f"Current Speed: {self.current_speed:.2f}, Target Speed: {s_target_desired:.2f}, "
              f"d_error: {d_error:.2f}, d_safe: {d_safe:.2f}, Object Speed: {self.sensor_data.s_object:.2f}")

        # Calculate speed error
        s_error = s_target_desired - self.current_speed

        # Compute acceleration based on PID
        s_acceleration = self.pid_controller.compute_throttle(s_error, time_step)

        # Update the current speed
        self.current_speed += s_acceleration * time_step
        self.current_speed = max(0, min(self.current_speed, 130))  # Limit speed between 0 and 130 kph

        return self.current_speed, s_target_desired, d_safe

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

# Run the application
if __name__ == "__main__":
    app = CruiseControlApp()
    app.mainloop()
