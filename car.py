"""
This file contains the Car class which is used to control the car's speed and distance.
It uses a PID controller to adjust the speed based on the target speed and a safe distance from the object ahead.

Author: Hamza El Hanbali
Date: 2024-07-28
"""

from PIDController import PIDController
from Sensor import Sensors

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
