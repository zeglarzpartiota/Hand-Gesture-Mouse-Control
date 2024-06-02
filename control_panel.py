import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from PIL import Image, ImageTk


class GestureControlPanel:
    def __init__(self):
        self.img_scale_factor = 8

        # INTERFACE STATE DEFINES
        self.is_running = True  # flag to stop the program
        self.debug = False
        self.show_camera = False
        self.show_command = False
        self.command_button = None
        self.smoothing = 5.0

        # BUTTONS
        self.show_camera_button = None
        self.used_command_button = None
        self.debug_mode_button = None
        self.movement_smoothing_label = None

    def run(self):
        # WINDOW PROPERTIES
        master = ThemedTk(theme="arc")
        master.geometry("640x300")
        master.title("Hand Gesture Mouse Control Panel")
        # self.master.iconbitmap("imgs/icon.ico")
        master.protocol("WM_DELETE_WINDOW", self.close_window)  # Closing protocol

        # WINDOW TITLE
        title_label = ttk.Label(master=master, text="Hand Gesture Mouse Control Panel", font=("", 20))
        title_label.pack()

        # RIGHT HAND COMMANDS INFO
        commands_info_frame = ttk.Frame(master, relief="flat", borderwidth=2)
        commands_info_frame.pack(pady=10, padx=10)

        right_hand_commands_label = ttk.Label(
            master=commands_info_frame,
            text="Right Hand Gestures",
            justify="center",
            anchor="center",
        )
        right_hand_commands_label.pack(pady=5)

        # RIGHT HAND GESTURES LABELS
        self.create_gesture_label(commands_info_frame, "images/move.png", "Move", 100)
        self.create_gesture_label(commands_info_frame, "images/left_click.png", "Left Click", 100)
        self.create_gesture_label(commands_info_frame, "images/right_click.png", "Right click", 100)
        self.create_gesture_label(commands_info_frame, "images/drag.png", "Drag", 100)
        self.create_gesture_label(commands_info_frame, "images/scroll.png", "Scroll", 100)

        # SETTINGS FRAME
        settings_frame = ttk.Frame(master=master, borderwidth=2)
        settings_frame.pack(pady=10, padx=10)

        # Show camera
        self.show_camera_button = ttk.Checkbutton(
            master=settings_frame,
            text="Toggle Camera",
            command=self.toggle_show_camera,
        )
        self.show_camera_button.pack(side="left")

        # Show used command
        self.used_command_button = ttk.Checkbutton(
            master=settings_frame,
            text="Toggle Command",
            command=self.toggle_show_command,
            state="disabled",
        )
        self.used_command_button.pack(side="left")

        # Show debug mode
        self.debug_mode_button = ttk.Checkbutton(
            master=settings_frame,
            text="Toggle Debug",
            command=self.toggle_debug_mode
        )
        self.debug_mode_button.pack(side="left")

        # Adjust movement smoothing
        movement_smoothing_frame = ttk.Frame(settings_frame, borderwidth=2)
        movement_smoothing_frame.pack(side="left", padx=10)

        self.movement_smoothing_label = ttk.Label(
            movement_smoothing_frame,
            text=f"Smoothing: {self.smoothing:.1f}"
        )
        self.movement_smoothing_label.pack()

        movement_smoothing_slider = ttk.Scale(
            master=movement_smoothing_frame,
            from_=1.0,
            to=20.0,
            orient="horizontal",
            command=self.toggle_movement_smoothing,
        )
        movement_smoothing_slider.pack()

        # Exit button
        exit_button = ttk.Button(
            master=master,
            text="Exit",
            command=self.close_window,
            width=10
        )
        exit_button.pack(pady=10)

        master.mainloop()

    def load_image(self, image_path, width_factor, height_factor):
        # PREPARES AN IMAGE TO BE USED IN TKINTER
        open_image = Image.open(image_path)
        resized_image = open_image.resize((self.img_scale_factor * width_factor, self.img_scale_factor * height_factor))
        image = ImageTk.PhotoImage(resized_image)
        return image

    def create_gesture_label(self, frame, image_path, text, label_width):
        gesture_label = ttk.Label(master=frame, width=label_width)
        gesture_label.pack(side="left", padx=15, anchor="center")

        # Load and resize image
        gesture_icon = self.load_image(image_path, 5, 8)

        # Image Label
        image_label = ttk.Label(master=gesture_label, image=gesture_icon, anchor="center")
        image_label.image = gesture_icon
        image_label.pack()

        # Text Label
        text_label = ttk.Label(master=gesture_label, text=text, anchor="center")
        text_label.pack()

        return gesture_label

    def close_window(self):
        self.is_running = False
        self.master.destroy()

    def toggle_show_camera(self):
        self.show_camera = not self.show_camera
        if self.used_command_button:
            self.used_command_button.config(
                state=tk.NORMAL if self.show_camera else tk.DISABLED
            )
        print("Show camera:", "On" if self.show_camera else "Off")

    def toggle_debug_mode(self):
        self.debug = not self.debug
        print("Debug mode:", "On" if self.debug else "Off")

    def toggle_show_command(self):
        self.show_command = not self.show_command
        print("Show command:", "On" if self.show_command else "Off")

    def toggle_movement_smoothing(self, value):
        self.smoothing = float(value)
        self.movement_smoothing_label.config(text=f"Smoothing: {self.smoothing:.1f}")


if __name__ == "__main__":
    GestureControlPanel().run()
