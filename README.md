# DOH Discharge Data Dashboard

A Python-based web application for visualizing Department of Health (DOH) hospital discharge data. This project utilizes Plotly Dash to create interactive dashboards that analyze demographics, substance use diagnoses, and polysubstance trends.

## 🛠 Tech Stack

  * **Language**: Python 3.x
  * **Framework**: [Plotly Dash](https://dash.plotly.com/)
  * **Data Manipulation**: Pandas
  * **Database**: SQLite
  * **Deployment**: Heroku (implied by `Procfile`)

## 🚀 Getting Started

### Prerequisites

Ensure you have Python installed on your system.

### Installation

1.  **Clone the repository**
    ```
    git clone https://github.com/Trevellp/DOH doh_plotly
    cd doh_plotly
    ```

2.  **Create a Virtual Environment (Optional but Recommended)**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

### Database Setup

If the `discharges.db` file is missing or needs to be refreshed with the latest CSV data:

```bash
python create_db.py
```

*This script will read the source CSV files (`discharge_data_view_demographics.csv`, etc.) and populate the SQLite database.*

Output should be: "Database created: discharges.db"

## 🏃‍♂️ Usage

To run the main dashboard locally:

```bash
python app.py
```

Open your web browser and navigate to `http://127.0.0.1:8050/` to view the dashboard.


### Run the application:
```
python multi_dashboard.py
```

If that gives errors, try:
```
python run_dashboard.py
```

Or use gunicorn (production server):
```
gunicorn multi_dashboard:server
```

### Access the app:
Open your browser to http://127.0.0.1:8050 (or the port shown in the terminal)

## 📊 Data Sources

The application visualizes data related to:

  * **Demographics**: Patient demographic breakdowns.
  * **Diagnoses**: Specific focus on substance use (`diag_su`) and polysubstance occurrences.

## ☁️ Deployment

This project includes a `Procfile`, making it ready for deployment on platforms like **Heroku**.

1.  Create a new Heroku app.
2.  Push the code to Heroku.
    ```bash
    heroku create
    git push heroku main
    ```

## 📂 Project Structure

  * **`app.py` / `app_alt.py`**: Main application entry points.
  * **`multi_dashboard.py`**: Likely the container for handling multiple dashboard views.
  * **`polysubstance_dashboard.py`**: Dashboard specific to analyzing polysubstance use data.
  * **`creative_dashboard.py`**: Dashboard containing creative/experimental visualizations.
  * **`create_db.py`**: Script to initialize and populate the SQLite database from source CSVs.
  * **`discharges.db`**: SQLite database storing the processed discharge data.
  * **`assets/`**: Contains static assets (CSS, images) for the Dash application.
  * **`queries.sql`**: SQL queries used for data extraction and transformation.

## File Structure

### Core Application Files

**`multi_dashboard.py`** - Main application entry point. Creates the Dash app with tabbed navigation between different dashboard views (Discharges, Polysubstance, and optionally Co-occurring). Uses Bootstrap styling and keyboard shortcuts for accessibility.

**`app_alt.py`** - "Discharges (Alt Views)" dashboard page. Displays discharge data related to substance use with various views and interactive graphs. Contains its own layout and callbacks.

**`polysubstance_dashboard.py`** - "Polysubstance Use" dashboard page. Analyzes patients with multiple substance use diagnoses. Includes filtering, charts, and data tables focused on polysubstance patterns.

**`mobile_app.py`** - Mobile-optimized version of the dashboard. Safely imports other dashboard modules and adapts the layout for smaller screens with custom CSS.

**`creative_dashboard.py`** - Alternative creative/experimental dashboard implementation. Uses custom theming and provides different visualizations of the same data.

**`app.py`** - Early/basic dashboard version. Loads data and performs comparisons between distinct counts and raw counts, analyzes duplicates in the data.

### Data & Database Files

**`create_db.py`** - Database initialization script. Loads two CSV files (`discharge_data_view_diag_su.csv` and `discharge_data_view_demographics.csv`), renames columns, and creates a SQLite database (`discharges.db`) with two tables: `diagnoses` and `demographics`.

**`queries.sql`** - Centralized SQL query repository. Contains named SQL queries used throughout the application (e.g., `load_main_data`, `load_polysubstance_data`, `count_by_sex_distinct`). Keeps SQL separate from Python code for easier maintenance.

**`discharges.db`** - SQLite database (created by `create_db.py`) containing the discharge data tables.

**`discharge_data_view_diag_su.csv`** - Source data file containing diagnosis/substance use information (record_id, substance, etc.).

**`discharge_data_view_demographics.csv`** - Source data file containing patient demographics (record_id, county, region, age_group, sex, calendar_year, etc.).

### Utility & Helper Files

**`theme.py`** - Custom Plotly theme configuration. Defines colors, fonts, backgrounds, and styling for all charts. Creates a consistent "doh" template used across dashboards.

**`inspect_columns.py`** - Utility script to inspect and clean CSV column names. Helps verify the structure of the source data files.

**`run_dashboard.py`** - Wrapper script to fix Jupyter/comm compatibility issues in Anaconda environments. Patches the `comm.create_comm` function before importing Dash to prevent `NotImplementedError`.

**`run_app.py`** - Alternative wrapper script (less successful version of `run_dashboard.py`).

### Deployment & Configuration Files

**`Procfile`** - Heroku deployment configuration. Specifies how to run the app in production using gunicorn: `web: gunicorn multi_dashboard:server`.

**`runtime.txt`** - Specifies Python version (3.11.9) for Heroku deployment.

**`requirements.txt`** - Python dependencies list: dash, dash-bootstrap-components, plotly, pandas, numpy, gunicorn.

**`README.md`** - Project documentation with setup and run instructions.

### Assets (CSS)

**`assets/tabs.css`** - Custom styling for tab navigation with brand colors, hover effects, and responsive design.

**`assets/mobile.css`** - Mobile-specific CSS rules that adjust grid layout and component sizing for screens under 768px wide.

### Suppressed Data

**`suppressed_exports/`** - Directory containing CSV files with suppressed data aggregations by different dimensions (age_group, calendar_year, county, sex).




Here is a documentation draft for your `README.md` file. It is based on the file structure (e.g., the `assets` folder and `Procfile` strongly suggest a Plotly Dash application) and the data filenames found in your repository.