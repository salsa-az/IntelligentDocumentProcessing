# Intelligent Document Processing - Insurance Claims System

A Vue.js frontend with Flask backend for processing insurance claims using Azure Document Intelligence and AI analysis.

## Quick Setup

### Backend (Flask API)
```bash
# 1. Create virtual environment
python -m venv idp-venv

# 2. Activate virtual environment
.\idp-venv\Scripts\Activate.ps1  # Windows PowerShell
# source idp-venv/bin/activate    # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
# Create .env file with your Azure credentials:
# BLOB_STRING_CONECTION=your_blob_connection_string
# AZURE_STORAGE_CONTAINER_NAME=your_container_name
# COSMOS_DB_URI=your_cosmos_db_uri
# COSMOS_DB_KEY=your_cosmos_db_key
# COSMOS_DB_DATABASE_NAME=your_database_name

# 5. Start Flask server
python endpoint/app.py
```

### Frontend (Vue.js)
```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```

## Access URLs
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000

## Test Credentials

### Customer Login
- **Email**: `customer@example.com`
- **Password**: `password123`
- **Role**: Customer (can submit claims)

### Approver Login
- **Email**: `approver@example.com`
- **Password**: `password123`
- **Role**: Approver (can review/approve claims)

## Features
- 📄 Document upload and AI analysis (Invoice, Doctor Forms, Lab Reports)
- 🏥 Hospital name extraction from invoices
- 📊 Claim status tracking and progress timeline
- 🤖 AI-powered claim analysis and recommendations
- 💬 Insurance chatbot support
- 👥 Role-based access (Customer/Approver views)

## Tech Stack
- **Frontend**: Vue.js 3, TailwindCSS, Vite
- **Backend**: Flask, Python
- **Cloud**: Azure Document Intelligence, Azure Cosmos DB, Azure Blob Storage
- **AI**: LangChain, OpenAI GPT

---
