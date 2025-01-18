import tkinter as tk
from tkinter import PhotoImage, Label, Button, Canvas, ttk
import datetime
import os
from PIL import ImageGrab

class BlackboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackboard")
        self.root.geometry("1050x570+150+50")
        self.root.configure(bg="#272827")
        self.root.resizable(False, False)

        self.current_x = 1
        self.current_y = 1
        self.color = 'white'
        self.current_value = tk.DoubleVar(value=2)  # Default value for the slider
        self.typing_mode = False

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        self.image_icon = PhotoImage(file="logo.png")
        self.root.iconphoto(False, self.image_icon)
        
        self.color_box = PhotoImage(file="color_section.png")
        Label(self.root, image=self.color_box, bg="#272827").place(x=10, y=10)

        self.brush_icon = PhotoImage(file="brush.png")  
        Button(self.root, image=self.brush_icon, bg="#FFFFFF", bd=0, command=self.activate_brush).place(x=30, y=350)
        
        self.type_icon = PhotoImage(file="type.png")
        Button(self.root, image=self.type_icon, bg="#FFFFFF", bd=0, command=self.activate_text).place(x=30, y=350+45)
        
        self.eraser = PhotoImage(file="erase.png")
        Button(self.root, image=self.eraser, bg="#FFFFFF", bd=0, command=self.new_canvas).place(x=30, y=350+45*2)

        self.save_icon = PhotoImage(file="save.png")
        Button(self.root, image=self.save_icon, bg="#CBCBCB", bd=0, command=self.save_image).place(x=990, y=522)

        self.colors = Canvas(self.root, bg="#000000", width=37, height=307, bd=0) 
        self.colors.place(x=30, y=35) 
        self.display_palette()

        self.canvas = Canvas(self.root, bg="#000000", width=930, height=500, bd=0, cursor="dot")
        self.canvas.place(x=100, y=10)
        self.canvas.bind("<Button-1>", self.locate_xy)
        self.canvas.bind("<B1-Motion>", self.add_line)

        self.color_indicator = Canvas(self.root, width=50, height=50, bg="#272827", highlightthickness=0)
        self.color_indicator.place(x=500, y=518)  # Place it in the middle of the board

        slider = ttk.Scale(self.root, from_=1, to=30, variable=self.current_value, orient='horizontal', command=self.slider_changed)
        slider.place(x=30, y=530)

        self.value_label = ttk.Label(self.root, text=f"{self.get_current_value():.2f}")
        self.value_label.place(x=27, y=550)

        # Initial update of the color indicator
        self.root.update_idletasks()  # Ensure the canvas is rendered before updating
        self.update_color_indicator()

    def locate_xy(self, event):
        """Locate the current x and y coordinates."""
        self.current_x = event.x
        self.current_y = event.y

    def add_line(self, event):
        """Draw a line on the canvas."""
        if not self.typing_mode:  # Only allow drawing if not in typing mode
            self.canvas.create_line((self.current_x, self.current_y, event.x, event.y), fill=self.color, width=self.get_current_value(),
                                    capstyle=tk.ROUND, smooth=True)
            self.current_x = event.x
            self.current_y = event.y

    def show_color(self, new_color):
        """Change the current drawing color."""
        self.color = new_color
        self.update_color_indicator()

    def new_canvas(self):
        """Clear the canvas."""
        self.canvas.delete("all")
        self.display_palette()

    def display_palette(self):
        """Display the color palette."""
        colors = [
            ("black", "black"), ("#8B76E9", "purple"), ("#EA2081", "pink"),
            ("crimson", "crimson"), ("#EEA705", "gold"), ("#F7FF00", "yellow"),
            ("lime", "green"), ("#52BCFF", "blue"), ("lightgray", "lightgray"),
            ("white", "white")
        ]
        for i, (color_code, color_name) in enumerate(colors):
            y0 = 10 + i * 30
            y1 = y0 + 20
            id = self.colors.create_rectangle((10, y0, 30, y1), fill=color_code, outline="white")
            self.colors.tag_bind(id, "<Button-1>", lambda event, color=color_code: self.show_color(color))

    def update_color_indicator(self):
        """Update the color indicator circle."""
        size = self.current_value.get()
        self.color_indicator.delete("all")
        center_x = self.color_indicator.winfo_width() // 2
        center_y = self.color_indicator.winfo_height() // 2
        self.color_indicator.create_oval(center_x - size // 2, center_y - size // 2, center_x + size // 2, center_y + size // 2, fill=self.color, outline=self.color)

    def get_current_value(self):
        """Get the current value of the slider."""
        return self.current_value.get()

    def slider_changed(self, event):
        """Handle slider value change."""
        self.value_label.configure(text=f"{self.get_current_value():.2f}")
        self.update_color_indicator()
    
    def activate_brush(self):
        """Activate brush mode."""
        self.typing_mode = False
        self.canvas.bind("<Button-1>", self.locate_xy)
        self.canvas.bind("<B1-Motion>", self.add_line)
        self.canvas.config(cursor="dot")

    def activate_text(self):
        """Activate text mode."""
        self.typing_mode = True
        self.canvas.bind("<Button-1>", self.create_text)
        self.canvas.unbind("<B1-Motion>")
        self.canvas.config(cursor="xterm")

    def create_text(self, event):
        """Create a text entry widget at the clicked location on the canvas."""
        if not self.typing_mode:
            return

        x, y = event.x, event.y
        font_size = int(self.get_current_value())  # Use slider value for font size
        font = ("Arial", font_size)
        text = tk.StringVar()
        
        entry = tk.Entry(self.canvas, textvariable=text, font=font, bg="black", fg=self.color, insertbackground=self.color)
        entry.place(x=x, y=y)
        
        # Bind Return key to finish_text
        entry.bind("<Return>", lambda e: self.finish_text(e, entry, x, y))
        
        # Bind FocusOut event to finalize text when clicking outside
        entry.bind("<FocusOut>", lambda e: self.finish_text(e, entry, x, y))
        
        entry.focus_set()  # Set focus to the entry widget

    def finish_text(self, event, entry, x, y):
        """Finalize the text input and display it on the canvas."""
        text = entry.get()
        
        if text:  # Only create text if there is something entered
            font_size = int(self.get_current_value())  # Use slider value for font size
            self.canvas.create_text(x, y, text=text, font=("Arial", font_size), fill=self.color, anchor="nw")
        
        entry.destroy()  # Remove the entry widget

    def save_image(self):
        """Capture and save the canvas content as a PNG image."""
        x = self.root.winfo_rootx() + self.canvas.winfo_x()
        y = self.root.winfo_rooty() + self.canvas.winfo_y()
        x1 = x + self.canvas.winfo_width()
        y1 = y + self.canvas.winfo_height()
        image = ImageGrab.grab(bbox=(x, y, x1, y1))

        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{current_time}_blackboard.png"
        
        file_path = os.path.join(os.path.expanduser("~"), "Desktop", filename)
        image.save(file_path, "PNG", dpi=(150, 150))

if __name__ == "__main__":
    root = tk.Tk()
    app = BlackboardApp(root)
    root.mainloop()
