# This class if for the suggestion screen ui
import tkinter as tk

from ui.ui_helpers.input_validator import InputValidator
from application.modes.plate_mode import PlateMode


class SuggestionScreen:
    def __init__(self, root, mode, state, on_back, on_search, on_suggest_similar, on_choose, on_uppercase=None, explanations=None):

        self.root = root
        self.mode = mode
        self.state = state
        self.on_back = on_back
        self.on_search = on_search
        self.on_suggest_similar = on_suggest_similar
        self.on_choose = on_choose
        self.on_uppercase = on_uppercase
        self.explanations = explanations
        self.pattern_entry = None

    def render(self):

        tk.Button(self.root, text="Back", command=self.on_back).pack(anchor="w", padx=10, pady=5)
        
        # Recent choice of item shown
        info_text = []
        if self.state.get("last_choice"):
            info_text.append(f"Previously chosen: {self.state['last_choice']}")
        if self.state.get("last_search"):
            info_text.append(f"Previous input: {self.state['last_search']}")
        if self.state.get("last_similar"):
            info_text.append(f"Previous pick of similar: {self.state['last_similar']}")

        if info_text:
            info_frame = tk.Frame(self.root, bd=1, relief="solid", padx=10, pady=6)
            info_frame.pack(fill="x", padx=10, pady=(5, 10))
            for line  in info_text:
                tk.Label(info_frame, text=line, anchor="w", font=("Arial", 10)).pack(anchor="w")


        if isinstance(self.mode, PlateMode):
            title = "Suggested number plates: "
            input_text = "Enter your desired plate pattern: "
        else:
            title = "Suggested phone numbers: "
            input_text = "Enter your desired numeric pattern: "

        tk.Label(self.root, text=title, font=("Arial", 16)).pack(pady=10)

        perfect, close = self.mode.get_top_suggestions(15)

        # Temporarily excluding with a normalized form
        excluded_key = None
        if self.state.get("exclude_raw") is not None:
            excluded_key = InputValidator.normalize_key(self.state['exclude_raw'])

        if excluded_key is not None:
            perfect = [item for item in perfect if InputValidator.normalize_key(item.raw) != excluded_key]
            close = [item for item in close if InputValidator.normalize_key(item.raw) != excluded_key]

        perfect = perfect[:5]
        remaining = 5 - len(perfect)
        close = close[:max(0, remaining)]

        perfect_label, close_label, no_perfect = self.get_section_labels()

        # Show perfect suggestions
        tk.Label(self.root, text=perfect_label, font=("Arial", 16)).pack(pady=(10, 5))
        if not perfect:
            tk.Label(self.root, text=no_perfect, font=("Arial", 16)).pack(pady=(10, 5))
        else:
            for item in perfect:
                self.make_suggestions(item)

        # Show close matches only
        if len(perfect) < 5 and close and close_label:
            tk.Label(self.root, text=close_label, font=("Arial", 16)).pack(pady=(10, 5))
            for item in close:
                self.make_suggestions(item)

        # Custom input
        tk.Label(self.root, text=input_text).pack()
        self.pattern_entry = tk.Entry(self.root, width=20)
        self.pattern_entry.pack()
        self.pattern_entry.bind("<Return>", lambda event: self.on_search())

        if isinstance(self.mode, PlateMode) and self.on_uppercase:
            self.pattern_entry.bind("<KeyRelease>", self.on_uppercase)

        tk.Button(self.root, text="Search", command=self.on_search).pack(pady=5)
        return self.pattern_entry


 # Suggestions
    def make_suggestions(self, item):
        frame = tk.Frame(self.root)
        frame.pack(pady=5)

        text_frame = tk.Frame(frame)
        text_frame.pack(side="left")

        description = item.explanation if hasattr(item, "explanation") else ""
        if self.explanations and not description:
            description = self.explanations.describe_object(self.mode, item)
        
        tk.Label(text_frame, text=item.raw, width=20, anchor="w").pack(anchor="w")
        tk.Label(text_frame, text=description, font=("Arial", 9), fg="grey").pack(anchor="w")

        tk.Button(frame, text="Suggest similar", command=lambda i=item: self.on_suggest_similar(i)).pack(side="left", padx=5)
        tk.Button(frame, text="I choose this one!", command=lambda i=item: self.on_choose(i)).pack(side="left", padx=5)


    def get_section_labels(self):

        if isinstance(self.mode, PlateMode):
            if getattr(self.mode,  "current_pattern", None):
                return "Perfect matches: ", "Close matches: ", "No exact matches."
            return "Top suggestions: ", " ", ""

        if getattr(self.mode, "current_pattern", None):
            return "Contains your pattern: ", "Other suggestions: ", "No exact matches."

        return "Top suggestions: ", "More suggestions: ", "No top suggestions"
    
