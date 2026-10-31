# 🚀 AI Business Intelligence Dashboard

An AI-powered Business Intelligence Dashboard that transforms raw datasets into meaningful insights through data cleaning, analysis, dynamic visualizations, and interactive reporting.

The application allows users to upload datasets and explore their data through an intuitive web-based dashboard, helping make data-driven decisions easier.

## 🌐 Live Demo

**Live Application:** https://ai-business-intelligence-dashboard-v53z.onrender.com

**GitHub Repository:** https://github.com/rupesh1226/AI-Business-Intelligence-Dashboard

## ✨ Features

- **Dataset Upload:** Upload CSV and Excel datasets.
- **Data Cleaning:** Process and clean uploaded datasets using Python and Pandas.
- **Dynamic Database Storage:** Store uploaded datasets in MySQL with dynamically created tables.
- **Automated Metadata Management:** Maintain dataset information and column details in MySQL.
- **Data Profiling:** Generate useful information about uploaded datasets.
- **Interactive Dashboard:** Explore datasets through a web-based dashboard.
- **Dynamic Visualizations:** Generate charts and graphical representations of data.
- **API Integration:** Connect the frontend with backend services using FastAPI.
- **Cloud Deployment:** Host the application using Render and Aiven Cloud MySQL.

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, FastAPI |
| Data Analysis | Pandas |
| Database | MySQL |
| ORM | SQLAlchemy |
| Visualization | Chart.js |
| Cloud Database | Aiven |
| Deployment | Render |
| Version Control | Git, GitHub |

## 🏗️ System Architecture

The application follows a simple data-processing workflow:

1. User uploads a CSV or Excel dataset.
2. FastAPI receives and processes the uploaded file.
3. Pandas performs data cleaning and preparation.
4. SQLAlchemy dynamically creates a MySQL table with a primary key.
5. Dataset information and column metadata are stored in MySQL.
6. The dashboard retrieves the processed data.
7. Interactive visualizations help users explore the dataset.

## 📂 Project Structure

```text
AI-Business-Intelligence-Dashboard/
│
├── backend/
│   └── app/
│       ├── main.py
│       ├── database.py
│       ├── models.py
│       │
│       ├── routes/
│       │   ├── upload.py
│       │   └── dashboard.py
│       │
│       └── services/
│           ├── cleaning.py
│           ├── dataset.py
│           └── profiler.py
│
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   │
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       └── app.js
│
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/rupesh1226/AI-Business-Intelligence-Dashboard.git
```

### 2. Navigate to the Project

```bash
cd AI-Business-Intelligence-Dashboard
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root and configure your MySQL connection:

```env
DATABASE_URL=mysql+pymysql://username:password@host:port/defaultdb
```

Use your own database credentials. Never commit your `.env` file or database passwords to GitHub.

### 6. Run the Application

From the project root, execute:

```bash
uvicorn app.main:app --app-dir backend --reload
```

### 7. Open the Application

- Frontend: http://127.0.0.1:8000
- API Documentation: http://127.0.0.1:8000/docs
- Health Check: http://127.0.0.1:8000/health

## ☁️ Cloud Deployment

This project is deployed using:

- **Render:** Hosts the FastAPI application and frontend.
- **Aiven:** Provides managed MySQL database hosting.

The application uses environment variables for database configuration and a CA certificate for secure SSL database connectivity.

Database tables are automatically initialized during application startup using SQLAlchemy's `Base.metadata.create_all()`.

## 🔒 Security

- Database credentials are configured through environment variables.
- Database connections use SSL.
- Sensitive configuration files should not be committed to the repository.
- `.env` and database certificate files should be excluded from Git.

## 🎯 Project Objective

The main objective of this project is to simplify business data analysis by providing an accessible platform where users can upload datasets, process data, store information, and explore insights through interactive visualizations.

## 🚀 Future Enhancements

- AI-powered insights and recommendations.
- Natural Language Querying (Ask questions about your data).
- Automated chart recommendations.
- Advanced filtering and drill-down analysis.
- Export dashboard reports as PDF.
- User authentication and role-based access.
- Support for larger datasets and optimized processing.

## 👨‍💻 Developer

**Roopesh Thimmapathini**

B.Tech – Data Science | Pragati Engineering College

**Interests:** Data Analytics, Artificial Intelligence, Full Stack Development and Business Intelligence.

**Portfolio:** https://rupesh1226.github.io/

---

⭐ If you find this project interesting, consider giving the repository a star!
