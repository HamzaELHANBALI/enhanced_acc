import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Your existing classes here

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
        self.sensor_data = Sensors(time_step=time_step, s_object=10, d_object=50)  # Object driving at 40 kph, 60 meters ahead of the ego vehicle
        self.pid_controller = PIDController(kp=0.5, ki=0, kd=0)
        self.current_speed = current_speed
        self.set_speed = set_speed
        self.target_speed = min(set_speed, self.sensor_data.s_object)
    
    def compute_safe_distance(self, object_speed, object_position):
        # Compute required stopping distance assuming a constant deceleration of -4 m/s^2 and
        ReactionTime = 1 # average reaction time of 1 second
        ComfortableDeceleration = 4 # 4 m/s^2

        relative_speed = self.current_speed - object_speed

        # Secure the division
        if abs(relative_speed) < 0.001:  # If relative speed is very close to zero
            TimeToCollision = float('inf')  # Assume no collision
        else:
            TimeToCollision = object_position / relative_speed

        TimeToStop = abs(self.current_speed / (- ComfortableDeceleration))
        safe_distance = self.current_speed * (TimeToCollision + TimeToStop + ReactionTime)
        return safe_distance

    def update_speed(self, time_step):
        if self.sensor_data.is_object_ahead:
            d_safe = self.compute_safe_distance(self.sensor_data.s_object, self.sensor_data.d_object)
            if d_safe < self.sensor_data.d_object:
                d_error = d_safe - self.sensor_data.d_object
                s_target_desired = self.sensor_data.s_object - self.pid_controller.kp * d_error
            else:
                s_target_desired = min(self.set_speed, self.sensor_data.s_object)

        s_error = s_target_desired - self.current_speed
        s_acceleration = self.pid_controller.compute_throttle(s_error, time_step)
        self.current_speed += s_acceleration * time_step
        self.current_speed = max(0, min(self.current_speed, 130))  # Limit speed between 0 and 130 kph
        return self.current_speed, s_target_desired

# Simulation parameters
car = Car(current_speed=20, set_speed=20, time_step=0.1) # 20 m/s

start_time = time.time()
time_values = []
speed_values = []
target_speed_values = []
object_position_values = []
current_time = 0

# Plot setup
fig, ax = plt.subplots(2, 1, figsize=(10, 8))

# Speed plot setup
ax[0].set_xlim(0, 50)  # Set time axis limit
ax[0].set_ylim(0, 130)  # Set speed axis limit (0 to 130 kph)
ax[0].set_xlabel('Time (s)')
ax[0].set_ylabel('Speed (kph)')
ax[0].set_title('Real-Time Speed and Target Speed Simulation')
line_speed, = ax[0].plot([], [], 'b-', linewidth=2, label='Current Speed')
line_target_speed, = ax[0].plot([], [], 'r--', linewidth=2, label='Target Speed')
ax[0].legend()

# Object position plot setup
ax[1].set_xlim(0, 50)  # Set time axis limit
ax[1].set_ylim(0, 100)  # Set distance axis limit (0 to 100 meters)
ax[1].set_xlabel('Time (s)')
ax[1].set_ylabel('Object Position (m)')
ax[1].set_title('Object Position Over Time')
line_object_position, = ax[1].plot([], [], 'g-', linewidth=2, label='Object Position')
ax[1].legend()

# Update function for animation
def update(frame):
    current_time = time.time() - start_time
    current_speed, target_speed = car.update_speed(car.sensor_data.time_step)
    car.sensor_data.d_object = car.sensor_data.d_object + ((current_speed - car.sensor_data.s_object)* car.sensor_data.time_step)
    current_time += car.sensor_data.time_step

    # Update data lists
    time_values.append(current_time)
    speed_values.append(current_speed)
    target_speed_values.append(target_speed)
    object_position_values.append(car.sensor_data.d_object)

    # Update the line data
    line_speed.set_data(time_values, speed_values)
    line_target_speed.set_data(time_values, target_speed_values)
    line_object_position.set_data(time_values, object_position_values)

    # Adjust x-axis limits dynamically
    if current_time > ax[0].get_xlim()[1]:
        ax[0].set_xlim(0, ax[0].get_xlim()[1] + 10)
        ax[1].set_xlim(0, ax[1].get_xlim()[1] + 10)

    return line_speed, line_target_speed, line_object_position

# Create animation
ani = FuncAnimation(fig, update, frames=None, blit=True, interval=100)

plt.tight_layout()
plt.show()