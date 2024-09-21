import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import requests
from io import BytesIO
from PIL import Image, ImageTk
import xml.etree.ElementTree as ET

class WMSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SegMAP-Stalwarts")
        self.root.geometry("1600x900")  # Larger canvas for image display
        self.root.configure(bg='#c5defb')  # Light background color

        # Main frame for the entire app
        self.main_frame = tk.Frame(self.root, bg='#E8E8E8')
        self.main_frame.pack(fill=tk.BOTH, padx=1.5, pady=1.5, expand=True)

        # Small input box area at the lower corner for WMS input details and buttons
        self.input_frame = tk.Frame(self.main_frame, bg='#F0F0F0', width=300, height=500)
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # Get Capabilities section above the input fields
        tk.Button(self.input_frame, text="Get Capabilities", command=self.get_capabilities, bg='#fbc5d2', fg='black', bd=0, relief='flat', height=1, width=20).grid(row=0, column=0, padx=2, pady=2,sticky=tk.W)
        tk.Label(self.input_frame, text="Available Layers:", bg='#fcfbfc').grid(row=0, column=1, padx=2, pady=2,sticky=tk.W)
        self.layer_listbox = tk.Listbox(self.input_frame, height=3, width=70, bg='#fcfbfc')
        self.layer_listbox.grid(row=0, column=2, padx=2, pady=2, sticky=tk.W)

        # Input fields and text display grouped together
        tk.Label(self.input_frame, text="Base WMS URL:", bg='#fcfbfc').grid(row=1, column=0, sticky=tk.W)
        self.wms_url_entry = tk.Entry(self.input_frame, width=50)
        self.wms_url_entry.grid(row=1, column=0, columnspan=2, padx=2, pady=2)

        tk.Label(self.input_frame, text="Layers (comma separated):", bg='#fcfbfc').grid(row=2, column=0, sticky=tk.W)
        self.layers_entry = tk.Entry(self.input_frame, width=50)
        self.layers_entry.grid(row=2, column=0, columnspan=2, padx=2, pady=2)

        tk.Label(self.input_frame, text="Bounding Box (xmin, ymin, xmax, ymax):", bg='#fcfbfc').grid(row=3, column=0, sticky=tk.W)
        self.bbox_entry = tk.Entry(self.input_frame, width=50)
        self.bbox_entry.grid(row=3, column=0, columnspan=2, padx=2, pady=2)

        # New SRS input field1
        tk.Label(self.input_frame, text="SRS (e.g., EPSG:4326):", bg='#fcfbfc').grid(row=4, column=0, sticky=tk.W)
        self.srs_entry = tk.Entry(self.input_frame, width=50)
        self.srs_entry.grid(row=4, column=0, columnspan=2, padx=2, pady=2)

        # New Image Format input field
        tk.Label(self.input_frame, text="Image Format (e.g., image/png):", bg='#fcfbfc').grid(row=5, column=0, sticky=tk.W)
        self.format_entry = tk.Entry(self.input_frame, width=50)
        self.format_entry.grid(row=5, column=0, columnspan=2, padx=2, pady=2)

        # Buttons for URL generation, copy, and image fetching
        self.generate_url_button = tk.Button(self.input_frame, text="Generate URL", command=self.generate_url, bg='#fbc5d2', fg='black', bd=0, relief='flat', height=1, width=20)
        self.generate_url_button.grid(row=6, column=0, padx=5, pady=10, sticky=tk.W)

        tk.Label(self.input_frame, text="Generated URL:", bg='#ebab91').grid(row=7, column=0, sticky=tk.W)
        self.url_display = tk.Text(self.input_frame, height=3, width=70, wrap=tk.WORD, bg='#fcfbfc')
        self.url_display.grid(row=7, column=1, padx=2, pady=2)

        self.copy_url_button = tk.Button(self.input_frame, text="Copy URL", command=self.copy_url, bg='#fbc5d2', fg='black', bd=0, relief='flat', height=1, width=20)
        self.copy_url_button.grid(row=8, column=0, padx=2, pady=2, sticky=tk.W)

        self.fetch_button = tk.Button(self.input_frame, text="Fetch Image", command=self.fetch_image, bg='#fbc5d2', fg='black', bd=0, relief='flat', height=1, width=20)
        self.fetch_button.grid(row=8, column=1, padx=2, pady=2, sticky=tk.W)

        # Larger canvas for displaying the image
        self.image_canvas = tk.Canvas(self.main_frame, bg='white')
        self.image_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Buttons for model loading and segmentation at the bottom
        self.load_model_button = tk.Button(self.input_frame, text="Load Model", command=self.load_model, bg='#fbc5d2', fg='black', bd=0, relief='flat', height=1, width=20)
        self.load_model_button.grid(row=9, column=0, padx=5, pady=5, sticky=tk.W)

        self.segment_button = tk.Button(self.input_frame, text="Segment Image", command=self.segment_image, bg='#fbc5d2', fg='black', bd=0, relief='flat', height=1, width=20)
        self.segment_button.grid(row=9, column=1, padx=5, pady=5, sticky=tk.W)

        # Variables for model and image
        self.model = None
        self.zoom_factor = 1.2
        self.image = None
        self.current_bbox = [-180, -90, 180, 90]  # Default bbox

    def get_capabilities(self):
        wms_url = self.wms_url_entry.get()
        if not wms_url:
            messagebox.showerror("Error", "Enter the WMS URL first.")
            return

        params = {
            "service": "WMS",
            "request": "GetCapabilities"
        }

        try:
            response = requests.get(wms_url, params=params)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            namespaces = {'wms': 'http://www.opengis.net/wms'}

            layers = root.findall(".//wms:Layer/wms:Name", namespaces=namespaces)
            self.layer_listbox.delete(0, tk.END)
            for layer in layers:
                self.layer_listbox.insert(tk.END, layer.text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get capabilities: {e}")

    def generate_url(self):
        """Generate the WMS URL based on user inputs."""
        wms_url = self.wms_url_entry.get()
        layers = self.layers_entry.get()
        bbox = self.bbox_entry.get()
        srs = self.srs_entry.get() or "EPSG:4326"  # Default SRS
        image_format = self.format_entry.get() or "image/png"  # Default format

        width = self.image_canvas.winfo_width() or 800
        height = self.image_canvas.winfo_height() or 600

        # Construct the WMS URL
        url = (f"{wms_url}?service=WMS&version=1.1.1&request=GetMap"
               f"&layers={layers}&bbox={bbox}&width={width}&height={height}"
               f"&srs={srs}&format={image_format}")

        self.url_display.delete(1.0, tk.END)
        self.url_display.insert(tk.END, url)

    def fetch_image(self):
        """Fetch the image using the generated WMS URL."""
        wms_url = self.url_display.get("1.0", tk.END).strip()
        if not wms_url:
            messagebox.showerror("Error", "Generate the URL first.")
            return

        try:
            response = requests.get(wms_url)
            response.raise_for_status()

            image_data = BytesIO(response.content)
            self.image = Image.open(image_data)

            # Display the fetched image on the canvas
            self.display_image(self.image)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch image: {e}")

    def display_image(self, image):
        # Resize image to fit the canvas if needed
        width, height = self.image_canvas.winfo_width(), self.image_canvas.winfo_height()
        resized_image = image.resize((width, height), Image.ANTIALIAS)
        self.tk_image = ImageTk.PhotoImage(resized_image)

        self.image_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.image_canvas.image = self.tk_image  # Keep a reference

    def copy_url(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.url_display.get("1.0", tk.END).strip())
        self.root.update()  # To ensure clipboard contents persist

    def load_model(self):
        pass  # Implement as needed

    def segment_image(self):
        pass  # Implement as needed


if __name__ == "__main__":
    root = tk.Tk()
    app = WMSApp(root)
    root.mainloop()
