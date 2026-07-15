# Terp Protect: Setup and Execution Guide

## Overview

This guide explains how to install the project dependencies, run the complete Terp Protect data pipeline, and launch the Streamlit dashboard.

Terp Protect processes publicly available University of Maryland Police Department incident and arrest records through an automated workflow that:

1. collects or loads source data
2. cleans and standardizes incident records
3. cleans and standardizes arrest records
4. creates analytical categories and quality indicators
5. builds the SQLite database
6. creates reusable SQL views
7. exports analytical outputs
8. launches an interactive Streamlit dashboard

---

## 1. Prerequisites

Before running the project, confirm that the following tools are installed:

- Python 3.10 or newer
- pip
- Git
- a terminal or command prompt
- a modern web browser

Optional tools:

- Visual Studio Code
- DB Browser for SQLite
- GitHub Desktop

Check the installed Python version:

    python --version

On systems where Python is accessed using `python3`, run:

    python3 --version

Check the installed pip version:

    pip --version

---

## 2. Download the Project

Clone the GitHub repository:

    git clone <repository-url>

Move into the project directory:

    cd Terp-Protect

Replace `<repository-url>` with the actual GitHub repository URL.

Alternatively, download the repository as a ZIP file from GitHub, extract it, and open the extracted `Terp-Protect` folder in a terminal.

---

## 3. Create a Virtual Environment

Creating a virtual environment is recommended because it keeps the project dependencies separate from other Python installations.

### Windows

Create the environment:

    python -m venv .venv

Activate it:

    .venv\Scripts\activate

### macOS or Linux

Create the environment:

    python3 -m venv .venv

Activate it:

    source .venv/bin/activate

After activation, the terminal should display `.venv` near the command prompt.

---

## 4. Install Dependencies

Install the required Python packages:

    pip install --upgrade pip

    pip install -r requirements.txt

The `requirements.txt` file contains the packages required for:

- data extraction
- data cleaning
- database creation
- SQL processing
- analytical calculations
- chart generation
- Streamlit dashboard execution

---

## 5. Project Structure

The main project structure is:

    Terp-Protect/
    │
    ├── README.md
    ├── SETUP.md
    ├── requirements.txt
    ├── run_pipeline.py
    │
    ├── dashboard/
    │   └── streamlit_app/
    │       ├── app.py
    │       ├── components/
    │       └── sections/
    │
    ├── data/
    ├── database/
    ├── docs/
    ├── outputs/
    └── scripts/

### Folder Purpose

| Folder | Purpose |
|---|---|
| `dashboard/` | Contains the Streamlit dashboard application |
| `data/` | Stores raw, intermediate, and cleaned datasets |
| `database/` | Stores database files, schema scripts, and SQL views |
| `docs/` | Contains the project report, analytical summary, and data dictionary |
| `outputs/` | Stores generated analytical exports and pipeline outputs |
| `scripts/` | Contains data extraction, transformation, database, and analysis scripts |

---

## 6. Run the Complete Pipeline

From the project root directory, run:

    python run_pipeline.py

On systems that use `python3`, run:

    python3 run_pipeline.py

The pipeline should be executed from the project root so that all relative file paths resolve correctly.

### Pipeline Responsibilities

The pipeline performs the major project stages in sequence:

1. processes incident source records
2. processes arrest source records
3. standardizes crime, location, outcome, and charge categories
4. calculates reporting-delay fields
5. creates data-quality indicators
6. creates the SQLite database
7. loads cleaned records into database tables
8. creates analytical SQL views
9. exports dashboard-ready datasets and analytical outputs

### Successful Completion

A successful run should display progress messages in the terminal and complete without an unhandled error.

Generated files will be placed in the appropriate project folders, including:

- `data/`
- `database/`
- `outputs/`

Do not manually modify generated files unless the project documentation specifically identifies them as editable inputs.

---

## 7. Launch the Streamlit Dashboard

Run the complete pipeline before launching the dashboard.

From the project root directory, execute:

    python -m streamlit run dashboard/streamlit_app/app.py

On systems that use `python3`, execute:

    python3 -m streamlit run dashboard/streamlit_app/app.py

Streamlit will display a local address similar to:

    http://localhost:8501

Open the address in a web browser if it does not open automatically.

---

## 8. Dashboard Sections

The Streamlit application contains the following analytical sections:

| Section | Purpose |
|---|---|
| Command Center | Summarizes major incident, outcome, location, delay, and coverage metrics |
| Time and Seasonality | Analyzes calendar months, academic periods, weekdays, and hours |
| Location Analysis | Compares detailed locations and standardized location groups |
| Incident Outcomes | Examines case dispositions and outcomes across crime groups |
| Reporting Delay | Measures how quickly incidents were reported |
| Arrest Analysis | Examines arrest records, charge categories, and incident-to-arrest matching |
| Data Quality | Displays primary field checks and records requiring review |

Dashboard filters affect the applicable analytical views.

Leave a filter empty to include all available values for that field.

---

## 9. Recommended Execution Order

Use the following order whenever the source data or transformation logic changes:

1. activate the virtual environment
2. install or update dependencies
3. run `run_pipeline.py`
4. confirm that the pipeline completes successfully
5. launch the Streamlit dashboard
6. review the Data Quality section
7. verify the dashboard metrics and charts

Typical commands:

    source .venv/bin/activate

    pip install -r requirements.txt

    python run_pipeline.py

    python -m streamlit run dashboard/streamlit_app/app.py

On Windows, activate the environment using:

    .venv\Scripts\activate

---

## 10. Updating the Project

When the source data or project logic changes:

1. place the updated source data in the expected project location
2. avoid changing required source column names unless the transformation scripts are also updated
3. run the complete pipeline again
4. verify the generated database and analytical outputs
5. launch the dashboard
6. review the Data Quality section
7. confirm that headline metrics remain internally consistent

The dashboard should not be treated as updated until the pipeline has been rerun successfully.

---

## 11. Common Troubleshooting

### Python Is Not Recognized

Try:

    python3 --version

If neither `python` nor `python3` works, install Python and ensure that it is added to the system path.

---

### Virtual Environment Does Not Activate

On Windows PowerShell, script execution may be restricted.

Temporarily allow activation for the current terminal session:

    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

Then run:

    .venv\Scripts\activate

---

### Required Package Is Missing

Reinstall all dependencies:

    pip install -r requirements.txt

For a specific missing package:

    pip install package-name

After installing the package, rerun the failed command.

---

### Streamlit Command Is Not Recognized

Use the module-based command:

    python -m streamlit run dashboard/streamlit_app/app.py

This is more reliable than calling `streamlit` directly.

---

### Dashboard Cannot Find a File

Confirm that:

- the terminal is open in the project root directory
- the complete pipeline has already been run
- expected generated files exist
- project folders have not been renamed
- relative paths in the scripts have not been changed

Run:

    python run_pipeline.py

Then restart the dashboard.

---

### Database Table or View Is Missing

Run the complete pipeline again:

    python run_pipeline.py

The database-building stage should recreate the required tables and analytical views.

If the problem continues, confirm that the SQL scripts exist in the expected database folder and that the pipeline completed without an earlier error.

---

### Dashboard Shows Old Data

Stop the Streamlit application using `Ctrl + C`.

Run the pipeline again:

    python run_pipeline.py

Restart the dashboard:

    python -m streamlit run dashboard/streamlit_app/app.py

Refresh the browser after the dashboard restarts.

---

### Port 8501 Is Already in Use

Run Streamlit on another port:

    python -m streamlit run dashboard/streamlit_app/app.py --server.port 8502

Then open:

    http://localhost:8502

---

### Charts or Styles Do Not Load Correctly

Try the following:

1. stop the Streamlit application
2. clear the browser cache
3. restart the dashboard
4. open the dashboard in a private browser window
5. confirm that all dependencies are installed

---

## 12. Data Quality Verification

After running the pipeline, review the Data Quality section of the dashboard.

Confirm that:

- incident identifiers are available
- occurrence datetimes are valid
- reported datetimes are valid
- reporting delays are non-negative
- arrest identifiers are available
- arrest datetimes are valid
- charge descriptions are available
- records requiring review remain visible

Invalid reporting-delay records are retained for transparency but excluded from reporting-delay calculations.

The data-quality pass rate measures configured completeness and format checks. It does not prove that every source value is factually correct.

---

## 13. Important Usage Notes

### Run From the Project Root

Always execute pipeline and dashboard commands from the main `Terp-Protect` directory.

### Run the Pipeline Before the Dashboard

The dashboard depends on processed data and database outputs generated by the pipeline.

### Preserve the Folder Structure

Moving scripts, renaming folders, or changing generated-file locations may break relative paths.

### Do Not Edit Generated Outputs Manually

Generated datasets, exports, and database files should be recreated through the pipeline.

### Review Public-Record Limitations

The project uses public UMPD records and may not contain every field or operational detail available in internal systems.

---

## 14. Responsible Use

Terp Protect is intended for:

- descriptive analysis
- database learning
- reporting
- data-quality review
- process improvement
- public-safety trend exploration

It is not intended for:

- predicting individual behavior
- assigning personal risk scores
- profiling individuals or demographic groups
- automated enforcement decisions
- drawing causal conclusions from descriptive data

---

## 15. Stop the Dashboard

To stop the Streamlit application, return to the terminal and press:

    Ctrl + C

---

## 16. Deactivate the Virtual Environment

When finished, deactivate the environment:

    deactivate

---

## Additional Documentation

For more information, refer to:

- `README.md` for the project overview
- `docs/ANALYTICAL_SUMMARY.md` for the main analytical findings
- `docs/DATA_DICTIONARY.md` for field and metric definitions
- `docs/Terp_Protect_Project_Report.pdf` for the complete project report