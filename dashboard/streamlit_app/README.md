# Streamlit Dashboard

## Purpose
This folder contains the Streamlit user interface for the Terp Protect analytics project.

The Streamlit app provides a lightweight local dashboard for exploring cleaned and modeled UMPD incident data directly from the project repository.

## Current Scope
- Dataset: UMPD Daily Crime and Incident Logs
- Year: 2025
- Main Input File: `dashboard/powerbi/data/incident_detail.csv`

## Planned App Pages
- Executive Overview
- Incident Trends
- Incident Outcomes
- Reporting Delay Analysis
- Location Analysis
- Data Quality

## How to Run
From the project root, run:

`streamlit run dashboard/streamlit_app/app.py`