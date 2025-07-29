# 🌟 APE Dashboard

Welcome to the **APE Dashboard** — a simple, beautiful way to explore Absolute Pose Error results and plots!

---

## 🚀 Quick Start

Follow these steps to get up and running in minutes:

### 1️⃣ Install Python

Make sure you have **Python 3.7 or higher** installed.  
[Download Python here](https://www.python.org/downloads/) if you need it.

### 2️⃣ Install Dependencies

Open your terminal in this project folder and run:

```sh
pip install -r requirements.txt
```

### 3️⃣ Prepare Your Data

Put these files and folders in the same directory as `app.py`:

- `ape_results.json` — your APE results data
- `plots/` — folder with PDF plots
- `plots_previews/` — folder with preview PNG images (generate these with `convert_pdfs_to_pngs.py`)

### 4️⃣ Launch the Dashboard

Start the dashboard with:

```sh
streamlit run app.py
```

### 5️⃣ Enjoy!

Open the link Streamlit gives you (usually [http://localhost:8501](http://localhost:8501)) in your browser.  
Explore, visualize, and download your results with ease!

---

## 💡 Need Help?

- To generate plot previews, use [`convert_pdfs_to_pngs.py`](convert_pdfs_to_pngs.py).
- If you run into trouble, check your Python version and that all dependencies are installed.

---

Happy exploring!
