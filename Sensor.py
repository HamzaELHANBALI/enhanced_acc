"""
This file contains the Sensors class which is used to detect objects ahead of the car and the distance between the car and the object.

Author: Hamza El Hanbali
Date: 2024-07-28
"""

class Sensors:
    def __init__(self, time_step, s_object, d_object):
        self.is_object_ahead = True
        self.s_object = s_object
        self.d_object = d_object
        self.time_step = time_step
