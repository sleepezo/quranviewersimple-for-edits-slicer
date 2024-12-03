import os
import re
from tkinter import Tk, Canvas, Frame, PhotoImage, Scrollbar, VERTICAL, HORIZONTAL
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def load_and_sort_images(directory):
    """Load and sort images based on their positions."""
    pattern = re.compile(r"Slice (\d+)-(\d+)\.png")
    images = []

    for file in os.listdir(directory):
        match = pattern.match(file)
        if match:
            position, page = map(int, match.groups())
            images.append((position, page, file))
    
    images.sort(key=lambda x: (x[0], x[1]))
    return images

class ImageViewer:
    def __init__(self, directory, max_columns=4):
        self.directory = directory
        self.max_columns = max_columns

        # Initialize Tkinter window
        self.root = Tk()
        self.root.title("Quran Images Viewer (Scroll, and Select)")
        
        # Create Canvas and Scrollbars
        self.canvas = Canvas(self.root, width=800, height=600)
        self.scrollbar_y = Scrollbar(self.root, orient=VERTICAL, command=self.canvas.yview)
        self.scrollbar_x = Scrollbar(self.root, orient=HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        self.frame = Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.canvas.pack(fill="both", expand=True, side="left")
        self.scrollbar_y.pack(fill="y", side="right")
        self.scrollbar_x.pack(fill="x", side="bottom")
        
        # Initialize storage for images and widgets
        self.photo_images = []
        self.img_labels = []
        self.reload_images()

        # Bind scrolling
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

    def reload_images(self):
        """Reload images in the viewer."""
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.photo_images.clear()
        self.img_labels.clear()
        images = load_and_sort_images(self.directory)
        row, col = 0, self.max_columns - 1
        for _, _, file in images:
            filepath = os.path.join(self.directory, file)
            img = PhotoImage(file=filepath)
            self.photo_images.append(img)
            label = Canvas(self.frame, width=img.width(), height=img.height(), bd=0, highlightthickness=0)
            label.create_image(0, 0, anchor="nw", image=img)
            label.grid(row=row, column=col)
            label.bind("<Button-1>", lambda event, f=filepath: self.on_image_click(f))
            self.img_labels.append(label)
            col -= 1
            if col < 0:
                col = self.max_columns - 1
                row += 1
        self.frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_image_click(self, filepath):
        """Handle image click events."""
        print(f"Selected image: {filepath}")

    def on_mouse_wheel(self, event):
        """Handle scrolling."""
        if event.state & 0x1:  # Shift key for horizontal scroll
            self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
        else:  # Vertical scroll
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def run(self):
        self.root.mainloop()

class DirectoryWatcher(FileSystemEventHandler):
    def __init__(self, image_viewer):
        self.image_viewer = image_viewer

    def on_any_event(self, event):
        """Reload images on any file system event."""
        self.image_viewer.reload_images()

if __name__ == "__main__":
    directory = "./SQ Pages (KDN Baru) - 202"  # Change this to your actual folder path
    image_viewer = ImageViewer(directory, max_columns=7)
    event_handler = DirectoryWatcher(image_viewer)
    observer = Observer()
    observer.schedule(event_handler, path=directory, recursive=False)
    observer.start()
    try:
        image_viewer.run()
    finally:
        observer.stop()
        observer.join()
