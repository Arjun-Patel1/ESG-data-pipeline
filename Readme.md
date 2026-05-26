# Intelligent Enterprise ESG Data Ingestion Pipeline

An automated, enterprise-grade ETL (Extract, Transform, Load) and data engineering pipeline built to handle unstructured vendor data (such as German SAP extracts), normalize it into a standardized audit ledger, and automatically run anomaly detection using the **Gemini 2.5 Flash LLM**.

---

## 📌 The Problem Solved

In enterprise sustainability reporting (ESG), greenhouse gas emissions data arrives from dozens of external suppliers in completely inconsistent, messy formats. 
* **The Challenges:** 
  * Inconsistent localization (e.g., European formats like `5.000,00` instead of standard floats).
  * Differing units of measurement (Gallons, Cubic Meters, Liters) across different global plants.
  * Lack of structural validation, creating high risk for material misstatements in compliance reporting.
  * Human data entry errors leading to massive anomalies.
  * Missing audit trails when data is edited or manipulated.

---

## 🛠️ The Architecture & Solution

This platform implements a highly reliable **Human-in-the-Loop (HITL) Queue** pattern. Data ingestion is treated as a machine-to-machine background process, while the React UI is strictly reserved for human verification, anomalies, and immutable final locking.

### 1. The Vault (Data Ingestion Layer)
* Implemented a Django REST API endpoint accepting programmatic multi-format inputs (CSV uploads or raw JSON Webhooks).
* Saves the exact raw incoming payload into a PostgreSQL `JSONB` column **before any transformation occurs**. This preserves the raw, untainted proof for external auditors.

### 2. The Engine (Asynchronous Processing Layer)
* Handled data processing asynchronously using **Celery** and **Redis** to ensure the API never blocks or crashes during large file processing.
* Built a deterministic normalization engine that correctly converts localized German notation strings into standard numeric formats and safely unifies mixed volumetric units (like US Gallons) directly into metric Liters.

### 3. The Brain (AI Audit Layer)
* Integrated the state-of-the-art **Gemini 2.5 Flash API** directly inside the background Celery task.
* When a normalized value crosses an anomalous threshold (>2,000 Liters), Gemini automatically audits the record, flags the potential risk of Scope 1 material misstatement, and writes an analytical warning note to the ledger.

### 4. The Ledger & UI (Audit Trail & Verification Layer)
* Utilized `django-simple-history` to automatically generate delta tables tracking who changed what, when, and why for every record.
* Built a high-density React dashboard styled with Tailwind CSS displaying side-by-side comparisons of raw data vs. normalized records, rendering Gemini AI custom alerts natively.
* Added a custom modal confirmation flow enabling human analysts to permanently Approve & Lock the records into the ledger, escalate them, or completely Reject/Purge them.

---

## 💻 Tech Stack

| Layer | Technology Used |
| :--- | :--- |
| **Frontend** | React, Tailwind CSS, Lucide React, Vite |
| **Backend API** | Django, Django REST Framework |
| **Database** | PostgreSQL (`JSONB` storage + relational models) |
| **Task Queue** | Celery, Redis |
| **AI Layer** | Google Gemini 2.5 Flash API |
| **Audit Tracking** | Django Simple History |

---

## 🚀 Getting Started & Installation

### Prerequisites
* Python 3.10+
* Node.js & npm
* Redis Server (Running on `localhost:6379`)
* Google Gemini API Key

### 1. Backend Setup
```bash
# Navigate to backend and activate virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure Environment (Add your Gemini API Key at the bottom of settings.py)
# GEMINI_API_KEY = "AIzaSy..."

# Run migrations and start the server
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
### 2. Celery Worker Setup

In a new terminal window with your virtual environment active:
```
Bash
cd backend
celery -A backend worker -l info --pool=solo
```
3. Frontend Setup
In a third terminal window:
```
Bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173 to view the Data Normalization Queue dashboard.

## 📊 Sample Ingestion Testing (cURL)
To simulate an automated machine-to-machine daily data transmission from an SAP ERP directly into your pipeline:
```
PowerShell
curl.exe -X POST [http://127.0.0.1:8000/api/v1/ingestion/upload/](http://127.0.0.1:8000/api/v1/ingestion/upload/) `
  -F "file=@./dummy_data/sap_export_feb2024.csv" `
  -F "source_name=SAP Plant 4" `
  -F "source_type=CSV_UPLOAD"
```