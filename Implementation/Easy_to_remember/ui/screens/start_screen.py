# This class is for dealing with a start screen in ui

import tkinter as tk

class StartScreen:
    def __init__(self, root, on_phone, on_plate):
        self.root = root
        self.on_phone = on_phone
        self.on_plate = on_plate

    def render(self):
        tk.Label(self.root, text="Welcome to smart number finder!",font=("Arial", 18)).pack(pady=40)

        tk.Button(self.root, text="Find your number", command=self.on_phone, font=("Arial", 14)).pack()

        tk.Button(self.root, text="Find your number plate", command=self.on_plate, font=("Arial", 14)).pack()
