import cv2
import glob
import numpy as np
import tkinter as tk
from PIL import ImageTk, Image
from tkinter import filedialog, StringVar


class Colors:
    # Color constants
    FRAME_BACKGROUND = "#D3D3D3"
    FRAME_BACKGROUND_BGR = (211, 211, 211)


class Dims:
    # Dimension constants
    WINDOW_MIN_WIDTH = 650
    WINDOW_MIN_HEIGHT = 400
    IMG_FRAME_WIDTH = 300
    IMG_FRAME_HEIGHT = 220


class App(tk.Tk):
    def __init__(self):
        # Set up main window
        super().__init__()
        self.title("Reverse Image Search")
        self.geometry(f"{Dims.WINDOW_MIN_WIDTH + 50}x{Dims.WINDOW_MIN_HEIGHT + 50}")
        self.minsize(Dims.WINDOW_MIN_WIDTH, Dims.WINDOW_MIN_HEIGHT)

        # Configure grid layout
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=4)

        # Add image frames
        self.left_frame = tk.Frame(self, width=Dims.IMG_FRAME_WIDTH, height=Dims.IMG_FRAME_HEIGHT, bg=Colors.FRAME_BACKGROUND)
        self.left_frame.grid(column=0, row=1, pady=5)
        self.right_frame = tk.Frame(self, width=Dims.IMG_FRAME_WIDTH, height=Dims.IMG_FRAME_HEIGHT, bg=Colors.FRAME_BACKGROUND)
        self.right_frame.grid(column=1, row=1, pady=5)

        # Add buttons
        self.select_image_button = tk.Button(self, text="Select Image", command=self.select_image)
        self.select_image_button.grid(column=0, row=2, sticky=tk.N)
        self.select_folder_button = tk.Button(self, text="Select Folder", command=self.select_folder)
        self.select_folder_button.grid(column=1, row=2, sticky=tk.N)
        self.find_closest_match_button = tk.Button(self, text="Find Closest Match", command=self.find_closest_match)
        self.find_closest_match_button.grid(row=3, sticky=tk.N, columnspan=2, pady=10)

        # Add text labels
        self.image_text = StringVar()
        image_text_label = tk.Label(self, textvariable=self.image_text)
        image_text_label.grid(column=0, row=0, sticky=tk.S)
        self.folder_text = StringVar()
        folder_text_label = tk.Label(self, textvariable=self.folder_text)
        folder_text_label.grid(column=1, row=0, sticky=tk.S)

        # Variables for file paths and images
        self.image_path = None
        self.image = None
        self.image_label = None
        self.tk_image = None
        self.folder_path = None
        self.folder_name = None
        self.result_image_path = None
        self.result_image = None
        self.result_image_label = None
        self.result_tk_image = None
        self.recent_path = None

    def select_image(self):
        """Handle image selection from file directory"""
        # Get image selection
        initial_dir = self.recent_path if self.recent_path else None
        image_path = filedialog.askopenfilename(filetypes=[("image files", (".png", ".jpg"))], initialdir=initial_dir)

        if image_path:
            self.image_path = image_path
            self.recent_path = self.image_path
            self.image = cv2.imread(self.image_path)
            image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

            # Change displayed image size to keep UI consistent
            padded_img = add_image_padding(
                image_rgb, Dims.IMG_FRAME_WIDTH / Dims.IMG_FRAME_HEIGHT, Colors.FRAME_BACKGROUND_BGR)
            img = Image.fromarray(padded_img).resize((Dims.IMG_FRAME_WIDTH, Dims.IMG_FRAME_HEIGHT))

            # Show selected image
            self.tk_image = ImageTk.PhotoImage(image=img)
            if self.image_label:
                self.image_label.destroy()
            self.image_label = tk.Label(self.left_frame, image=self.tk_image, text="")
            self.image_label.pack()

            # Show image file name
            displayed_img_name = self.image_path[self.image_path.rfind('/') + 1:]
            if len(displayed_img_name) > 28:
                displayed_img_name = displayed_img_name[:17] + "..." + displayed_img_name[-8:]
            self.image_text.set("Selected Image: " + displayed_img_name)
            print(self.image_path)

    def select_folder(self):
        """Handle folder selection from file directory"""
        # Get folder selection
        initial_dir = self.recent_path if self.recent_path else None
        folder_path = filedialog.askdirectory(initialdir=initial_dir)

        if folder_path:
            self.folder_path = folder_path
            self.recent_path = self.folder_path
            # Show selected folder name
            self.folder_name = self.folder_path[self.folder_path.rfind('/') + 1:]
            displayed_folder_name = self.folder_name
            if len(displayed_folder_name) > 30:
                displayed_folder_name = displayed_folder_name[:19] + "..." + displayed_folder_name[-8:]
            self.folder_text.set("Selected Folder: " + displayed_folder_name)
            print(self.folder_path)
            if self.result_image_label:
                self.result_image_label.pack_forget()

    def find_closest_match(self):
        """Search for the closest image and display the result"""
        # Check if an image is not selected
        if self.image_path is None:
            self.image_text.set("No image selected")
        # Check if a folder is not selected
        if self.folder_path is None:
            self.folder_text.set("No folder selected")

        if self.image_path and self.folder_path:
            # Get filenames and images from folder
            filenames = glob.glob(f"{self.folder_path}/*.png") + glob.glob(f"{self.folder_path}/*.jpg")
            filenames.sort()
            folder_images = []
            ind = 0
            print("Loading Images...")
            while ind < len(filenames):
                img = cv2.imread(filenames[ind])
                if img is not None:
                    folder_images.append(img)
                    ind += 1
                else:
                    filenames.pop(ind)

            # Search folder for most similar image
            print("Searching...")
            result_index = get_most_similar_image(self.image, folder_images, compare_with_color=True)
            result_rgb = cv2.cvtColor(cv2.imread(filenames[result_index]), cv2.COLOR_BGR2RGB)
            self.result_image_path = filenames[result_index]
            self.result_image = result_rgb
            print("Image Path: " + self.result_image_path)

            # Change displayed image size
            padded_result_img = add_image_padding(
                self.result_image, Dims.IMG_FRAME_WIDTH / Dims.IMG_FRAME_HEIGHT, Colors.FRAME_BACKGROUND_BGR)
            img = Image.fromarray(padded_result_img).resize((Dims.IMG_FRAME_WIDTH, Dims.IMG_FRAME_HEIGHT))

            # Show result
            self.result_tk_image = ImageTk.PhotoImage(image=img)
            if self.result_image_label:
                self.result_image_label.destroy()
            self.result_image_label = tk.Label(self.right_frame, image=self.result_tk_image, text="")
            self.result_image_label.pack()

            # Show image file path
            folder_name = self.folder_name
            file_name = self.result_image_path[self.result_image_path.rfind('/') + 1:]
            if (len(folder_name) + len(file_name)) > 30:
                if len(folder_name) > 15:
                    folder_name = folder_name[:4] + "..." + folder_name[-8:]
                if len(file_name) > 15:
                    file_name = file_name[:4] + "..." + file_name[-8:]
            self.folder_text.set("Closest Match: " + folder_name + "/" + file_name)


def add_image_padding(image, frame_ratio, padding_color=(0, 0, 0)):
    """Return an image with color padding to match a dimension ratio"""
    height, width, _ = image.shape
    image_ratio = width / height

    if image_ratio == frame_ratio:
        return image
    # If image is taller than frame, pad the sides
    if image_ratio < frame_ratio:
        new_width = int(height * frame_ratio)
        padding = int((new_width - width) / 2)
        padded_image = cv2.copyMakeBorder(image, 0, 0, padding, padding, cv2.BORDER_CONSTANT, value=padding_color)
    # If image is wider than frame, pad the top and bottom
    else:
        new_height = int(width / frame_ratio)
        padding = int((new_height - height) / 2)
        padded_image = cv2.copyMakeBorder(image, padding, padding, 0, 0, cv2.BORDER_CONSTANT, value=padding_color)
    return padded_image


def get_most_similar_image(image, candidates, compare_with_color=False):
    """Return index of most similar image in candidates"""
    image_height, image_width, _ = image.shape
    scaled_width = 32
    scaled_height = int(scaled_width * (image_height / image_width))
    scaled_image = cv2.resize(image, (scaled_width, scaled_height), interpolation=cv2.INTER_AREA)
    image_index, closest_match = 0, 1000000

    # Compare with every candidate image
    for i in range(len(candidates)):
        # Scale candidate image to dimensions of selected image
        scaled_candidate = cv2.resize(candidates[i], (scaled_width, scaled_height), interpolation=cv2.INTER_AREA)
        # Get comparison score
        comparison = mse(scaled_image, scaled_candidate, compare_with_color)
        if comparison < closest_match:
            closest_match = comparison
            image_index = i
        # If images are nearly identical, stop searching
        if closest_match < 200:
            break
    print("Lowest Difference: " + str(closest_match))
    print("Image Index: " + str(image_index))
    return image_index


def mse(image_1, image_2, compare_with_color):
    """Return the difference between two images, calculated by the Mean Squared Error"""
    if not compare_with_color:
        # Convert to grayscale if faster performance is needed
        image_1 = cv2.cvtColor(image_1, cv2.COLOR_BGR2GRAY)
        image_2 = cv2.cvtColor(image_2, cv2.COLOR_BGR2GRAY)

    # Calculate the Mean Squared Error of the two images
    # (similar images will have a lower error value)
    difference = np.sum((image_1.astype("float") - image_2.astype("float")) ** 2)
    difference /= float(image_1.shape[0] * image_1.shape[1])
    return difference


if __name__ == "__main__":
    app = App()
    app.mainloop()
