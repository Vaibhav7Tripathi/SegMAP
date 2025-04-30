import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.core.clipboard import Clipboard
from kivy.core.image import Image as CoreImage
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.graphics.transformation import Matrix

import requests
from io import BytesIO
from PIL import Image as PILImage
import xml.etree.ElementTree as ET

# Placeholder for model loading and segmentation
def load_pretrained_model():
    # Implement model loading here
    pass

def segment_image(pil_image):
    # Implement image segmentation here
    # For demonstration, returning the original image
    return pil_image

class LayerCheckbox(BoxLayout):
    """Custom widget for layer selection with a checkbox and label."""
    selected = False
    layer_name = StringProperty("")

    def __init__(self, layer_name, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 30
        self.layer_name = layer_name

        self.checkbox = CheckBox()
        self.checkbox.bind(active=self.on_checkbox_active)
        self.add_widget(self.checkbox)

        self.label = Label(text=layer_name, halign='left', valign='middle')
        self.label.bind(size=self.label.setter('text_size'))
        self.add_widget(self.label)

    def on_checkbox_active(self, checkbox, value):
        self.selected = value

class WMSImageFetcherApp(App):
    zoom_scale = NumericProperty(1.0)  # Use NumericProperty instead of FloatProperty

    def build(self):
        self.title = "WMS Image Fetcher with Kivy"

        # Default values
        self.default_bbox = "-180,-90,180,90"
        self.default_crs = "EPSG:4326"
        self.default_format = "image/png"

        # Initialize model (placeholder)
        load_pretrained_model()

        main_layout = BoxLayout(orientation='horizontal')

        # Side Panel Layout
        side_panel = BoxLayout(orientation='vertical', size_hint=(0.3, 1), padding=10, spacing=10)

        # Base URL Input
        self.base_url_input = TextInput(
            hint_text="Base WMS URL",
            size_hint=(1, None),
            height=40
        )
        side_panel.add_widget(self.base_url_input)

        # Fetch Layers Button
        fetch_layers_btn = Button(
            text="Fetch Layers",
            size_hint=(1, None),
            height=40
        )
        fetch_layers_btn.bind(on_press=self.fetch_layers)
        side_panel.add_widget(fetch_layers_btn)

        # Layers Display
        layers_label = Label(text="Available Layers:", size_hint=(1, None), height=30, halign='left', valign='middle')
        layers_label.bind(size=layers_label.setter('text_size'))
        side_panel.add_widget(layers_label)

        self.layers_container = BoxLayout(orientation='vertical', size_hint_y=None)
        self.layers_container.bind(minimum_height=self.layers_container.setter('height'))

        scroll_view = ScrollView(size_hint=(1, 0.3))
        scroll_view.add_widget(self.layers_container)
        side_panel.add_widget(scroll_view)

        # CRS Input
        self.crs_input = TextInput(
            hint_text=f"CRS (default: {self.default_crs})",
            size_hint=(1, None),
            height=40
        )
        side_panel.add_widget(self.crs_input)

        # Bounding Box Input
        self.bbox_input = TextInput(
            hint_text=f"Bounding Box (default: {self.default_bbox})",
            size_hint=(1, None),
            height=40
        )
        side_panel.add_widget(self.bbox_input)

        # Image Format Input
        self.format_input = TextInput(
            hint_text=f"Image Format (default: {self.default_format})",
            size_hint=(1, None),
            height=40
        )
        side_panel.add_widget(self.format_input)

        # Generate URL Button
        generate_url_btn = Button(
            text="Generate URL",
            size_hint=(1, None),
            height=40
        )
        generate_url_btn.bind(on_press=self.generate_wms_url)
        side_panel.add_widget(generate_url_btn)

        # URL Display
        self.url_display = TextInput(
            text="",
            readonly=True,
            size_hint=(1, None),
            height=60,
            multiline=True
        )
        side_panel.add_widget(self.url_display)

        # Copy URL Button
        copy_url_btn = Button(
            text="Copy URL",
            size_hint=(1, None),
            height=40
        )
        copy_url_btn.bind(on_press=self.copy_wms_url)
        side_panel.add_widget(copy_url_btn)

        # Fetch Image Button
        fetch_image_btn = Button(
            text="Fetch Image",
            size_hint=(1, None),
            height=40
        )
        fetch_image_btn.bind(on_press=self.fetch_image)
        side_panel.add_widget(fetch_image_btn)

        # Zoom Buttons Layout
        zoom_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=40, spacing=10)
        zoom_in_btn = Button(text="+", size_hint=(0.5, 1))
        zoom_in_btn.bind(on_press=self.zoom_in)
        zoom_layout.add_widget(zoom_in_btn)

        zoom_out_btn = Button(text="-", size_hint=(0.5, 1))
        zoom_out_btn.bind(on_press=self.zoom_out)
        zoom_layout.add_widget(zoom_out_btn)
        side_panel.add_widget(zoom_layout)

        # Segmentation Button
        segment_image_btn = Button(
            text="Segment Image",
            size_hint=(1, None),
            height=40
        )
        segment_image_btn.bind(on_press=self.segment_image)
        side_panel.add_widget(segment_image_btn)

        # Add side panel to main layout
        main_layout.add_widget(side_panel)

        # Image Display Area
        image_layout = FloatLayout()
        self.image_widget = Image(
            source='',
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0}
        )
        image_layout.add_widget(self.image_widget)
        main_layout.add_widget(image_layout)

        return main_layout

    def fetch_layers(self, instance):
        """Fetch available layers from the WMS server."""
        base_url = self.base_url_input.text.strip()
        if not base_url:
            self.show_popup("Error", "Please enter the Base WMS URL.")
            return

        request_url = f"{base_url}?service=WMS&version=1.3.0&request=GetCapabilities"

        try:
            response = requests.get(request_url)
            if response.status_code == 200:
                layers = self.parse_layers(response.content)
                if layers:
                    self.display_layers(layers)
                else:
                    self.show_popup("Error", "No layers found in the GetCapabilities response.")
            else:
                self.show_popup("Error", f"Failed to fetch layers. Status code: {response.status_code}")
        except Exception as e:
            self.show_popup("Error", f"Error fetching layers: {str(e)}")

    def parse_layers(self, xml_content):
        """Parse XML to extract layer names."""
        try:
            root = ET.fromstring(xml_content)
            namespaces = {'wms': 'http://www.opengis.net/wms'}
            layers = []
            for layer in root.findall('.//wms:Layer/wms:Layer', namespaces):
                name = layer.find('wms:Name', namespaces)
                if name is not None and name.text:
                    layers.append(name.text)
            return layers
        except ET.ParseError:
            self.show_popup("Error", "Failed to parse GetCapabilities XML.")
            return []

    def display_layers(self, layers):
        """Display layers with checkboxes."""
        self.layers_container.clear_widgets()
        for layer in layers:
            layer_checkbox = LayerCheckbox(layer_name=layer)
            self.layers_container.add_widget(layer_checkbox)

    def generate_wms_url(self, instance):
        """Generate WMS URL based on user input or default values."""
        base_url = self.base_url_input.text.strip()
        if not base_url:
            self.show_popup("Error", "Please enter the Base WMS URL.")
            return

        # Get selected layers
        selected_layers = [child.layer_name for child in self.layers_container.children if child.selected]
        if not selected_layers:
            self.show_popup("Error", "Please select at least one layer.")
            return
        layers = ",".join(selected_layers)

        # Get other parameters with defaults
        bbox = self.bbox_input.text.strip() if self.bbox_input.text.strip() else self.default_bbox
        crs = self.crs_input.text.strip() if self.crs_input.text.strip() else self.default_crs
        image_format = self.format_input.text.strip() if self.format_input.text.strip() else self.default_format

        # Construct the URL
        self.wms_url = (
            f"{base_url}?service=WMS&version=1.3.0&request=GetMap&layers={layers}&bbox={bbox}&width=800&height=600&crs={crs}&format={image_format}"
        )

        self.url_display.text = self.wms_url

    def copy_wms_url(self, instance):
        """Copy the generated WMS URL to the clipboard."""
        Clipboard.copy(self.url_display.text)
        self.show_popup("Success", "WMS URL copied to clipboard.")

    def fetch_image(self, instance):
        """Fetch the image from the generated WMS URL."""
        try:
            response = requests.get(self.wms_url)
            if response.status_code == 200:
                image_data = BytesIO(response.content)
                pil_image = PILImage.open(image_data)
                self.display_fetched_image(pil_image)
            else:
                self.show_popup("Error", f"Failed to fetch image. Status code: {response.status_code}")
        except Exception as e:
            self.show_popup("Error", f"Error fetching image: {str(e)}")

    def display_fetched_image(self, pil_image):
        """Display the fetched image in the Kivy app."""
        pil_image.save("fetched_image.png")  # Save temporarily
        self.image_widget.source = "fetched_image.png"
        self.image_widget.reload()

    def zoom_in(self, instance):
        """Zoom in on the image."""
        self.zoom_scale *= 1.2
        self.image_widget.size = (self.image_widget.width * self.zoom_scale, self.image_widget.height * self.zoom_scale)
        self.image_widget.reload()

    def zoom_out(self, instance):
        """Zoom out on the image."""
        self.zoom_scale /= 1.2
        self.image_widget.size = (self.image_widget.width * self.zoom_scale, self.image_widget.height * self.zoom_scale)
        self.image_widget.reload()

    def segment_image(self, instance):
        """Segment the displayed image using the loaded model."""
        if self.image_widget.source:
            pil_image = PILImage.open("fetched_image.png")
            segmented_image = segment_image(pil_image)  # Placeholder for segmentation
            segmented_image.save("segmented_image.png")  # Save the segmented image
            self.image_widget.source = "segmented_image.png"
            self.image_widget.reload()
        else:
            self.show_popup("Error", "No image to segment.")

    def show_popup(self, title, message):
        """Show a popup with a message."""
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=message))
        close_button = Button(text="Close", size_hint=(1, None), height=40)
        content.add_widget(close_button)

        popup = Popup(title=title, content=content, size_hint=(0.8, 0.5))
        close_button.bind(on_press=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    WMSImageFetcherApp().run()