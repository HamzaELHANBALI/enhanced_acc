class Sensors:
    def __init__(self, time_step, s_object, d_object):
        self.is_object_ahead = True
        self.s_object = s_object
        self.d_object = d_object
        self.time_step = time_step
