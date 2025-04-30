# SegMAP

SegMAP is a cross-platform desktop application designed to perform **on-device semantic segmentation** of satellite and web map images using a **U-Net based model**. It is capable of fetching images from any valid **WMS (Web Map Service)** server and exporting geospatial segmentation results in **GeoJSON format**.

> 🚀 Built for Smart India Hackathon 2024  
> 🧠 Team Stalwarts | Problem Statement ID: 1735 | Theme: Smart Automation

---

## 🔍 Features

- **Supervised segmentation** of satellite and aerial imagery using U-Net.
- **Tkinter-based interface** for platform-independent usability.
- **Dynamic map fetching** from any WMS server.
- **Export segmented results** in GeoJSON format.
- Designed for **non-technical users** with easy input and interaction.

---

## 🛠 Technical Overview

- Interface developed using **Python Tkinter**.
- Semantic segmentation via **multi-layer U-Net** trained on aerial imagery.
- Achieves **91.7% accuracy** after 50 epochs on benchmark data.
- Dynamically fetches map tiles based on user-defined coordinates.
- Uses **on-device GPU** for segmentation.

---

## 🧪 How It Works

1. **User inputs**: WMS base URL, version, format, CRS, bounding box.
2. **URL endpoint** is generated from input.
3. **Map image** is fetched from WMS.
4. **User zooms** or pans to desired region.
5. **Segmentation** is performed using local U-Net model.
6. **Output is exported** in geospatial formats like GeoJSON.

---

## 🔧 Tools Integrated

- Zoom with tap (mobile) or mouse scroll (desktop)
- Layer management dropdown
- Map state bookmarking
- Segmented object percentage calculator
- Label opacity adjustment
- Text prompts to extract specific features

---

## 📦 Dataset

- Base Dataset:  
  [Semantic Segmentation of Aerial Imagery (Kaggle)](https://www.kaggle.com/datasets/humansintheloop/semantic-segmentation-of-aerial-imagery)

- Custom Dataset:  
  Under development to increase accuracy by 6–7% and range by 400–500m.

---

## 💡 Impact

- Helps **WebGIS developers** automate segmentation of remote sensing data.
- Works with **any valid WMS server**, not tied to one provider.
- **On-device** execution with GPU support ensures responsive UI/UX.
- Combines **fetch + segment** — unlike other tools that do only one.

---

## 📜 License

This project is licensed under the BSD 3-Clause License.

---

## 👥 Team

**Team Name:** Stalwarts  
**Event:** Smart India Hackathon 2024  
**Category:** Software  
**PS Title:** On-device semantic segmentation of WMS services with geospatial data export  
**Team ID:** 4470
