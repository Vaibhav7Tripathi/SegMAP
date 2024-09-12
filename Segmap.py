import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
import numpy as np
from io import BytesIO
from pre_trained_model import load_model  

DEFAULT_BBOX = "-180,-90,180,90"  
MODEL_PATH = r"H:\Pahuni coding\ISRO WMS IMAGE MODEL\SegMap\satellite_standard_unet_100epochs.hdf5"  

class GeoportalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter Geoportal by Stalwarts")
        self.root.state('zoomed')

        self.zoom_level = 1.0
        self.bbox = list(map(float, DEFAULT_BBOX.split(',')))  # Convert bbox to float list
        self.model = None
        self.img = None
        self.segmented_image = None

        self.load_model()
        self.create_widgets()

    def create_widgets(self):
        input_frame = tk.Frame(self.root, bg="#e0f7fa")
        input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=10)

        fields = [
            ("Base WMS URL:", "url_entry"),
            ("Layers:", "layers_entry"),
            ("Bounding Box (bbox):", "bbox_entry"),
            ("Image Format:", "format_entry"),
            ("WMS Version:", "version_entry"),
            ("CRS:", "crs_entry")
        ]

        self.entries = {}

        for i, (label_text, entry_name) in enumerate(fields):
            label = tk.Label(input_frame, text=label_text, bg="#e0f7fa", font=("Arial", 12))
            label.grid(row=i, column=0, sticky=tk.W, padx=10, pady=5)

            entry = tk.Entry(input_frame, width=40, font=("Arial", 12))
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[entry_name] = entry

        self.url_entry = self.entries["url_entry"]
        self.layers_entry = self.entries["layers_entry"]
        self.bbox_entry = self.entries["bbox_entry"]
        self.format_entry = self.entries["format_entry"]
        self.version_entry = self.entries["version_entry"]
        self.crs_entry = self.entries["crs_entry"]

        self.generate_btn = tk.Button(input_frame, text="Generate URL", font=("Arial", 12), bg="#a5d6a7", fg="#2e7d32", command=self.generate_url)
        self.generate_btn.grid(row=6, column=1, pady=10, sticky=tk.E)

        self.url_display = tk.Text(input_frame, height=3, width=50, font=("Arial", 12), state=tk.DISABLED)
        self.url_display.grid(row=7, column=0, columnspan=2, padx=10, pady=5)

        self.copy_btn = tk.Button(input_frame, text="Copy URL", font=("Arial", 12), bg="#a5d6a7", fg="#2e7d32", command=self.copy_url)
        self.copy_btn.grid(row=8, column=1, pady=10, sticky=tk.E)

        self.fetch_btn = tk.Button(input_frame, text="Fetch Image", font=("Arial", 12), bg="#a5d6a7", fg="#2e7d32", command=self.fetch_image)
        self.fetch_btn.grid(row=9, column=1, pady=10, sticky=tk.E)

        self.zoom_in_btn = tk.Button(input_frame, text="Zoom In", font=("Arial", 12), bg="#a5d6a7", fg="#2e7d32", command=self.zoom_in)
        self.zoom_in_btn.grid(row=10, column=1, pady=10, sticky=tk.E)

        self.zoom_out_btn = tk.Button(input_frame, text="Zoom Out", font=("Arial", 12), bg="#a5d6a7", fg="#2e7d32", command=self.zoom_out)
        self.zoom_out_btn.grid(row=11, column=1, pady=10, sticky=tk.E)

        self.canvas = tk.Canvas(self.root, bg="white", cursor="cross")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        x_scroll = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.config(xscrollcommand=x_scroll.set)

        y_scroll = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.canvas.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.config(yscrollcommand=y_scroll.set)

    def load_model(self):
        try:
            weights_path = MODEL_PATH
            self.model = load_model(weights_path)
            messagebox.showinfo("Model Loaded", f"Model architecture loaded and weights loaded from:\n{weights_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model:\n{e}")

    def generate_url(self):
        base_url = self.url_entry.get().strip()
        layers = self.layers_entry.get().strip()
        bbox_input = self.bbox_entry.get().strip()
        img_format = self.format_entry.get().strip()
        version = self.version_entry.get().strip()
        crs = self.crs_entry.get().strip()

        if not all([base_url, layers, crs, img_format, version]):
            messagebox.showerror("Input Error", "Please fill in all required fields.")
            return

        bbox = self.validate_bbox(bbox_input)  
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()

        url = (
            f"{base_url}?service=WMS&request=GetMap&version={version}&layers={layers}&styles="
            f"&crs={crs}&bbox={bbox}&width={width}&height={height}&format={img_format}&transparent=true"
        )

        self.url_display.config(state=tk.NORMAL)
        self.url_display.delete(1.0, tk.END)
        self.url_display.insert(tk.END, url)
        self.url_display.config(state=tk.DISABLED)

    def validate_bbox(self, bbox_input):
        try:
            bbox = list(map(float, bbox_input.split(',')))
            if len(bbox) == 4 and all(-180 <= val <= 180 for val in bbox):
                return ','.join(map(str, bbox))
            else:
                return DEFAULT_BBOX
        except ValueError:
            return DEFAULT_BBOX

    def fetch_image(self):
        if self.model is None:
            messagebox.showerror("Model Error", "Model is not loaded.")
            return

        url = self.url_display.get(1.0, tk.END).strip()

        if not url:
            messagebox.showerror("Error", "URL is empty.")
            return

        try:
            response = requests.get(url)
            response.raise_for_status()

            # Open the image
            self.img = Image.open(BytesIO(response.content))

            # If image is grayscale, convert it to RGB
            if self.img.mode == 'L':
                self.img = self.img.convert('RGB')

            self.display_image()

            self.run_model_on_image(self.img)

        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch image:\n{e}")

    def zoom_in(self):
        self.zoom_level *= 2.0
        self.update_bbox()
        self.fetch_image()

    def zoom_out(self):
        self.zoom_level /= 2.0
        self.update_bbox()
        self.fetch_image()

    def update_bbox(self):
        center_lon = (self.bbox[0] + self.bbox[2]) / 2
        center_lat = (self.bbox[1] + self.bbox[3]) / 2

        lon_span = (self.bbox[2] - self.bbox[0]) / self.zoom_level
        lat_span = (self.bbox[3] - self.bbox[1]) / self.zoom_level

        self.bbox = [
            max(-180, center_lon - lon_span / 2),
            max(-90, center_lat - lat_span / 2),
            min(180, center_lon + lon_span / 2),
            min(90, center_lat + lat_span / 2)
        ]

    def run_model_on_image(self, img):
        try:
            # Convert to grayscale and resize for the model
            grayscale_img = img.convert('L')
            img_array = np.array(grayscale_img.resize((256, 256))) / 255.0
            img_array = np.expand_dims(img_array, axis=-1)  # Add channel dimension for grayscale
            img_array = np.expand_dims(img_array, axis=0)   # Add batch dimension

            # Make prediction using the model
            prediction = self.model.predict(img_array)

            # Process the predicted segmentation map
            segmented_image = np.argmax(prediction, axis=-1).squeeze()
            segmented_image_pil = Image.fromarray(segmented_image.astype(np.uint8) * 255)

            # Resize to match original image size
            self.segmented_image = segmented_image_pil.resize(self.img.size)

            # Display segmented image
            self.display_segmented_image()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to segment image:\n{e}")

    def display_image(self):
        img_width, img_height = self.img.size
        self.canvas.config(scrollregion=(0, 0, img_width, img_height))

        tk_img = ImageTk.PhotoImage(self.img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)
        self.canvas.image = tk_img

    def display_segmented_image(self):
        if self.segmented_image is not None:
            tk_segmented_img = ImageTk.PhotoImage(self.segmented_image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=tk_segmented_img)
            self.canvas.segmented_image = tk_segmented_img

    def copy_url(self):
        url = self.url_display.get(1.0, tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(url)
        messagebox.showinfo("URL Copied", "URL has been copied to clipboard.")


if __name__ == "__main__":
    root = tk.Tk()
    app = GeoportalApp(root)
    root.mainloop()
