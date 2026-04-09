import tkinter as tk 
from tkinter import messagebox
from tkinter import ttk

from ui.ui_helpers.explanations import Explanations
from ui.screens.start_screen import StartScreen
from ui.screens.final_screen import FinalScreen
from ui.screens.suggestion_screen import SuggestionScreen
from ui.ui_helpers.input_validator import InputValidator
from ui.ui_helpers.user_action_log import UserActionLog
from application.modes.phone_mode import PhoneMode
from application.modes.plate_mode import PlateMode

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart number finder")
        self.root.geometry("800x650")

        print("\n SYSTEM INITIALIZING ")

        # Phone number or num plates mode
        self.mode_setting = None
        self.pattern_entry = None
        self.exclude_raw = None
        self.last_choice = None
        self.last_search = None
        self.last_similar = None
        self.phone_mode_cache = None
        self.plate_mode_cache = None
        self.logger = UserActionLog()
        self.show_start_screen()
        self.explanations = Explanations()
       
    # Loading functionality
    def show_loading(self, text="Loading..."):
        self.clear_screen()

        container = tk.Frame(self.root)
        container.pack(expand=True)

        tk.Label(container, text=text,font=("Arial", 18)).pack(pady=(30, 10))
        tk.Label(container, text="Please wait...",font=("Arial", 18)).pack(pady=(0, 10))

        progress = ttk.Progressbar(container, mode="indeterminate", length=280)
        progress.pack(pady=(0, 20))
        progress.start(10)

    # Call for a start screen
    def show_start_screen(self):
        self.clear_screen()
        self.exclude_raw = None
        self.last_choice = None
        self.last_search = None
        self.last_similar = None
        StartScreen(
            self.root,
            on_phone=self.init_phone_mode,
            on_plate=self.init_plate_mode
        ).render()


    # Loading screen for when the user picks the mode and the system gets data from database
    def load_mode(self, mode_type):
        if mode_type == "phone":
            print("\nPHONE NUMBER MODE SELECTED ")
            self.show_loading("Loading phone numbers...")
            self.root.update_idletasks()
            self.root.update()

            if self.phone_mode_cache is None:
                self.phone_mode_cache = PhoneMode()

            self.mode_setting = self.phone_mode_cache
        elif mode_type == "plate":
            print("\nNUMBER PLATE MODE SELECTED ")
            self.show_loading("Loading number plates...")
            self.root.update_idletasks()
            self.root.update()

            if self.plate_mode_cache is None:
                self.plate_mode_cache = PlateMode()

            self.mode_setting = self.plate_mode_cache
        self.show_suggestions()

    # Phone mode
    def init_phone_mode(self):
        self.load_mode("phone")

    # Plate mode
    def init_plate_mode(self):
        self.load_mode("plate")

    # Show suggestions screen with current state
    def show_suggestions(self):
        self.clear_screen()
        
        screen = SuggestionScreen(
            root=self.root,
            mode=self.mode_setting,
            state={
                "exclude_raw": self.exclude_raw,
                "last_choice": self.last_choice,
                "last_search": self.last_search,
                "last_similar": self.last_similar,
            },
            on_back=self.show_start_screen,
            on_search=self.search_pattern,
            on_suggest_similar=self.suggest_similar,
            on_choose=self.choose_number,
            on_uppercase=self.force_uppercase_entry,
            explanations=self.explanations,
        )
        self.pattern_entry = screen.render()
        self.exclude_raw = None
        

    # Input uppercase letters
    def force_uppercase_entry(self, event=None):
        if self.pattern_entry is None:
            return
        
        current = self.pattern_entry.get()
        upper = current.upper()

        if current != upper:
            cursor_position = self.pattern_entry.index(tk.INSERT)
            self.pattern_entry.delete(0, tk.END)
            self.pattern_entry.insert(0, upper)
            self.pattern_entry.icursor(cursor_position)
    

# Search for simmilar numbers to users input
    def search_pattern(self):
        if self.pattern_entry is None:
            return
        
        pattern = self.pattern_entry.get().strip()
        
        # Input validation
        if isinstance(self.mode_setting, PlateMode):
            valid, result = InputValidator.validate_plate_pattern(pattern)
        else:
            valid, result = InputValidator.validate_phone_pattern(pattern)

        # Error message
        if not valid:
            messagebox.showerror("Invalid input", result)
            return

        cleaned_pattern = result

        # reset past similar item and store current
        self.exclude_raw = None
        self.last_similar = None
        self.last_search = cleaned_pattern
        self.logger.save("search", cleaned_pattern, self.get_mode_name())
        
        print(f"User searching for pattern: {cleaned_pattern}")
        
        # update mode with new search pattern
        if isinstance(self.mode_setting, PlateMode):
            self.mode_setting.update_from_user_pattern(cleaned_pattern)
        else:
            self.mode_setting.update_from_pattern(cleaned_pattern)

        # refresh  suggestions
        self.show_suggestions()


    # User actions
    # Similar suggestion
    def suggest_similar(self, item):
        print(f"\nUser clicked suggest similar for: {item.raw}")
        self.exclude_raw = item.raw
        self.last_similar = item.raw
        
        # Update the search
        if isinstance(self.mode_setting, PlateMode):
            self.mode_setting.update_from_similar_item(item.raw)
        else:
            self.mode_setting.update_from_pattern(item.digits)
            
        if hasattr(self.mode_setting, "update_preferences"):
            self.mode_setting.update_preferences(item)
            
        self.show_suggestions()

    # Item was chosen
    def choose_number(self, item):
        print(f"\nUser chose: {item.raw}")
        self.last_choice = item.raw
        self.logger.save("choose", item.raw, self.get_mode_name())
        
        # Mark item as taken
        if hasattr(self.mode_setting, "mark_taken"):
            self.mode_setting.mark_taken(item)
        
        if hasattr(self.mode_setting, "update_preferences"):
            self.mode_setting.update_preferences(item)
        self.show_final_screen(item)

    # Current mode name 
    def get_mode_name(self):
        return "plate" if isinstance(self.mode_setting, PlateMode) else "phone"

    # Final screen
    def show_final_screen(self, chosen_object):
        self.clear_screen()
        FinalScreen(
            self.root,
            mode=self.mode_setting,
            chosen_object=chosen_object,
            on_back=self.show_suggestions,
            on_home=self.show_start_screen,
        ).render()

    #  Clear screen   
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# Close app
def on_close():
    try:
        if app.phone_mode_cache is not None:
            app.phone_mode_cache.close()
        if app.plate_mode_cache is not None:
            app.plate_mode_cache.close()
    finally:
        root.destroy()




if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

