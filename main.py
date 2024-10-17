"""
This project is a simulation of an enhanced cruise control system that includes the ability to handle both distance and speed control.
It provides a GUI for the user to interact with the simulation and control the car's speed, inject objects into the simulation and control the distance between the car and the object.
This a follow up to the original cruise control project which was a simple system that just controlled the speed of the car : https://github.com/HamzaELHANBALI/Basic_ACC

Author: Hamza El Hanbali
Date: 2024-07-28
"""

from CruiseControlApp import CruiseControlApp

# Run the application
if __name__ == "__main__":
    app = CruiseControlApp()
    app.mainloop()
