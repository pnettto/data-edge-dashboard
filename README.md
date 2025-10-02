Data Edge KPI Dashboard (Streamlit)
===================================

A minimal, clean scaffold resembling the provided screenshot. Charts are simple reusable components ready to be wired to outputs from `exploratory_analysis/*`.

Quickstart
----------

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Structure
---------

```
streamlit_app.py
ui/
  components/
    charts.py
  layout/
    sidebar.py
utils/
  data_loader.py
  forecast.py
resources/
  raw_data/
exploratory_analysis/
  osei/
  waldean/
  guillermo/
  pedro/
```