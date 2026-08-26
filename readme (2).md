# 🔥 Thermal Anomaly Detection System
**SIH 26162 | NTRO | AI-Based Detection & Classification of Industrial Fires**

---

## ⚡ Quick Start (5 minutes)

### 1. Setup Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Generate Data & Classify
```bash
# Generate sample data
python data_generator.py

# Run classifier (uses geopandas for accurate distances)
python classifier.py
```

### 3. Launch Dashboard
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## 🏗️ Architecture (Simplified - No FastAPI)

```
data_generator.py  →  data/firms_data.csv + data/industries.csv
        ↓
classifier.py      →  data/classified_fires.csv  (geopandas + confidence scores)
        ↓
app.py (Streamlit) →  🗺️ Interactive Map + 📊 Analytics + 📋 Data Table
```

**Why no FastAPI?** For a 15-hour MVP, Streamlit reading CSVs directly is:
- ✅ One terminal, one command
- ✅ No CORS issues
- ✅ No port conflicts
- ✅ Easier to demo

---

## 📁 File Structure

```
SIH project/
├── app.py                    # Streamlit dashboard (MAIN)
├── classifier.py             # Classification + confidence scoring
├── map_visualization.py      # Folium map with emoji markers
├── data_generator.py         # Sample data (replace with real FIRMS API later)
├── requirements.txt          # Dependencies
├── data/
│   ├── firms_data.csv
│   ├── industries.csv
│   └── classified_fires.csv
└── venv/                     # Virtual environment
```

---

## 🚀 For Real FIRMS Data (Post-Hackathon)

Replace `data_generator.py` with NASA FIRMS API:
```python
import requests
url = "https://firms.modaps.eosdis.nasa.gov/api/area/csv/..."
df = pd.read_csv(url)
```

---

## 🎯 Demo Tips

1. **Pre-load 3-5 case studies** (e.g., Beirut explosion, California wildfires)
2. **Click a marker** → info panel slides in from right
3. **Toggle satellite layer** → show judges real imagery
4. **Export CSV** → proves data export capability
5. **Mention**: "Currently using sample data; ready to integrate real NASA FIRMS API"
