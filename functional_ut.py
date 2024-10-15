import unittest
from car import Car

class TestCruiseControl(unittest.TestCase):
    def test_speed_matches_target(self):
        # Set up the car and controller parameters
        initial_speed = 0 # kph
        target_speed = 60 # kph
        kp = 0.5 # proportional gain

        car = Car(target_speed=target_speed)
        car.speed = initial_speed

        # goal is to test if the speed of the car matches the target speed after "enough" time
        timestep = 0.1

        # Calculate the theoretical time to reach the target speed
        tau = 1 / kp

        # 3 time constants is usually enough to reach 95% of the target speed (approx)
        time_to_target = 3 * tau

        # calculate the number of timesteps to reach 95% of the target speed
        nbr_timesteps = int(time_to_target / timestep)
        
        for _ in range(nbr_timesteps):
            car.update_speed(timestep)

        # assert that the speed is within ~5% of the target speed
        self.assertAlmostEqual(car.speed, target_speed, delta=target_speed * 0.05)

if __name__ == "__main__":
    unittest.main()