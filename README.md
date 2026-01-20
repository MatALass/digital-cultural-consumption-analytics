# Digital Cultural Consumption in France

**EFREI Paris — Data Storytelling Dashboard (Streamlit)**  
Author: *Mathieu Alassoeur*  
Course: Data Visualization & Storytelling — 2025  

---

## Project Overview

This project explores **how socio-demographic characteristics and digital behaviors influence cultural consumption in France**.  
It is based on an open public dataset provided by data.gouv.fr and is presented through an interactive **Streamlit data storytelling dashboard**.

The objective is not only to visualize data, but to **build a structured narrative** that guides the user from raw observations to insights and implications.

**Narrative structure used in the dashboard:**

> Problem → Analysis → Insights → Implications

---

## Dataset

- Source: data.gouv.fr  
- Topic: Digital practices and cultural consumption in France  
- Scope: Socio-demographic variables, digital access, online cultural behaviors  

The dataset is provided in CSV format and processed using Python data analysis tools.

---

## Technologies Used

- Python 3  
- Pandas, NumPy  
- Matplotlib, Seaborn, Plotly  
- Streamlit  
- Jupyter Notebook  

---

## Project Structure

```

Data-viz-dashboard/
│
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── data/                  # Dataset files
├── sections/              # Analysis and visualization logic
├── utils/                 # Helper functions
└── README.md

````

---

## Quick Start

Follow the steps below to run the dashboard locally.

### 1. Clone the repository

```bash
git clone https://github.com/MatALass/Data-viz-dashboard.git
cd Data-viz-dashboard
````

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
```

Activate it:

**macOS / Linux**

```bash
source venv/bin/activate
```

**Windows (PowerShell)**

```bash
venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Check the data

Ensure the dataset files are present in the `data/` directory.
If you use a different dataset or file name, update the paths accordingly in the code.

### 5. Run the Streamlit application

```bash
streamlit run app.py
```

The dashboard will be available at:

```
http://localhost:8501
```

---

## Dashboard Content

The Streamlit application includes:

* Exploratory data analysis
* Interactive visualizations
* Socio-demographic comparisons
* Interpretation of digital cultural behaviors
* A storytelling-driven user flow

---

## Learning Objectives

This project was developed to:

* Apply data visualization best practices
* Build a coherent data storytelling narrative
* Design interactive dashboards with Streamlit
* Translate data insights into societal interpretations
