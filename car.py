"""
Car class for Cruise Control Simulation

Author: @Hamza EL HANBALI
Date: 12/10/2024
"""

from pid_controller import PIDController

class Car:
    def __init__(self, target_speed):
        self.speed = 0
        self.target_speed = target_speed # target speed is the speed that the car is supposed to be driving at
        self.set_speed = 0 # set speed is the speed that the driver wants the car to be driving at
        self.pid = PIDController(kp=0.5, ki=0, kd=0)

    def update_speed(self, dt):
        error = self.target_speed - self.speed
        acceleration = self.pid.compute(error, dt)
        self.speed += acceleration * dt
        self.speed = max(0, min(self.speed, 130))  # Limit speed between 0 and 130 kph
        return self.speed