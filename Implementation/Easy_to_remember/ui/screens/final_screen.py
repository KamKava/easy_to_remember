# This class is for the final ui screen
import tkinter as tk
from application.modes.plate_mode import PlateMode

class FinalScreen:
    def __init__(self, root, mode, chosen_object, on_back, on_home):
        self.root = root
        self.mode = mode
        self.chosen_object = chosen_object
        self.on_back = on_back
        self.on_home = on_home

    def render(self):
        if isinstance(self.mode, PlateMode):
            message = "Congratulations on your new number plate!"
            chosen_text = "Your chosen plate: "
        else:
            message = "Congratulations on your new phone number!"
            chosen_text = "Your chosen number: "

        tk.Label(self.root, text=f"{message}\n\n{chosen_text}\n\n{self.chosen_object.raw}", font=("Arial", 20, "bold")).pack(pady=20)

        tk.Button(self.root, text="Back", command=self.on_back).pack()
        tk.Button(self.root, text="Home", command=self.on_home).pack()
