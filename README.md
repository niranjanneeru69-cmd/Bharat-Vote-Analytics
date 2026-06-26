# 🗳️ Indian Election Intelligence System (IEIS)

> A Machine Learning and Data Warehouse platform for analyzing Indian General Election data (1952–2019) using ETL pipelines, predictive analytics, and interactive visualizations.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-orange)
![SQLite](https://img.shields.io/badge/Database-SQLite-green)
![Status](https://img.shields.io/badge/Status-Completed-success)

---

# 📌 Overview

The **Indian Election Intelligence System (IEIS)** is an end-to-end Data Science and Machine Learning project that consolidates more than **70 years of Indian General Election data (1952–2019)** into a centralized data warehouse.

The system enables historical election analysis, constituency insights, voter turnout prediction, election outcome prediction, and political trend analysis using Machine Learning and Data Mining techniques.

This project demonstrates the complete Data Science workflow:

* Data Collection
* ETL Pipeline
* Data Cleaning
* Data Warehouse Design
* Feature Engineering
* Machine Learning
* Data Visualization
* Model Evaluation
* Web Dashboard

---

# 🎯 Problem Statement

Indian election data is distributed across multiple heterogeneous sources such as:

* Election Commission of India
* Candidate Affidavits
* Voter Turnout Records
* Historical Archives
* Kaggle Datasets

Because the data is inconsistent and fragmented, it is difficult to perform long-term political analysis or build predictive models.

IEIS solves this problem by integrating all datasets into a unified analytical platform.

---

# ✨ Features

* Historical Election Analytics (1952–2019)
* ETL Pipeline
* Data Cleaning & Normalization
* Star Schema Data Warehouse
* Candidate Analysis
* Party Performance Analysis
* Voter Turnout Analysis
* Constituency Competitiveness Analysis
* Machine Learning Predictions
* Interactive Dashboard
* Anti-Manipulation Prediction System

---

# 🧠 Machine Learning Models

### Safe vs Swing Constituency Classification

* Random Forest
* Accuracy: **74%**

### Voter Turnout Prediction

* Ridge Regression
* R² Score: **0.68**

### Election Win/Loss Prediction

* Gradient Boosting Classifier
* Accuracy: **82%**

---

# 📊 Data Mining Techniques

* K-Means Clustering
* Principal Component Analysis (PCA)
* Trend Analysis
* Regional Analysis
* Candidate Wealth Analysis
* Political Era Analysis

---

# 🏗️ Data Warehouse Architecture

The project follows a **Star Schema**.

### Fact Table

* fact_election_results

### Dimension Tables

* dim_year
* dim_candidate
* dim_party
* dim_constituency
* dim_turnout

---

# ⚙️ Technology Stack

### Programming

* Python

### Libraries

* NumPy
* Pandas
* Matplotlib
* Seaborn
* Scikit-learn

### Database

* SQLite

### Concepts

* SQL
* ETL
* Data Warehouse
* Star Schema
* Data Mining
* Machine Learning

---

# 📁 Project Structure

```
Indian-Election-Intelligence-System/

│── data/
│── notebooks/
│── preprocessing/
│── models/
│── database/
│── dashboard/
│── images/
│── reports/
│── requirements.txt
│── app.py
│── README.md
```

---

# 🚀 Installation

create the project folder with name of Indian-Election-Intelligence-System

open terminal

Clone the repository
```bash
git clone https://github.com/yourusername/Indian-Election-Intelligence-System.git
```

Go to the project folder

```bash
cd Indian-Election-Intelligence-System
``

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python app.py
```

---

# 📈 Results

| Model                        | Performance  |
| ---------------------------- | ------------ |
| Safe vs Swing Classification | 74% Accuracy |
| Voter Turnout Prediction     | R² = 0.68    |
| Win/Loss Prediction          | 82% Accuracy |

---

# 📷 Screenshots

Include screenshots of:

* Dashboard
* Star Schema
* ETL Pipeline
* Model Predictions
* Visualizations
* Confusion Matrix
* ROC Curve

---

# 📚 Future Improvements

* Real-time Election Commission API integration
* Deep Learning models for prediction
* Interactive GIS-based constituency maps
* Cloud deployment
* Explainable AI (SHAP/LIME)
* Live election analytics dashboard

---

# 👥 Team

* Battula Venkata Niranjan
* Aryan Vasisth
* Kothapalli Tarun Sandeep
* Sriramoju Srujan

---

# 📄 License

This project was developed for academic and educational purposes at the **National Institute of Technology Sikkim**.

---

⭐ If you found this project interesting, consider giving the repository a **Star**.
