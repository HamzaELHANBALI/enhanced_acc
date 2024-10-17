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
