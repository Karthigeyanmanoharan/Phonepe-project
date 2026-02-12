# 🚀 PhonePe Transaction Insights Dashboard  

---

## 📌 Project Overview

An end-to-end **Data Engineering + Data Analytics + Visualization** project built using the PhonePe Pulse dataset.

This project extracts raw JSON data, loads it into PostgreSQL, performs SQL analysis, and presents interactive insights using Streamlit with geographical visualizations.

---

## 🎯 Business Objective

With the rapid growth of digital payments in India, this project aims to:

- Analyze transaction growth trends  
- Evaluate insurance penetration across states  
- Study user registration & engagement behavior  
- Identify high-potential expansion regions  
- Provide actionable business insights  

---

## 🏗️ Architecture Overview

```
JSON Data → ETL (Python) → PostgreSQL → SQL Analysis → Streamlit Dashboard
```

---

## 🛠️ Tech Stack

| Category | Tools Used |
|----------|------------|
| Language | Python |
| Database | PostgreSQL |
| ETL | psycopg2 |
| Data Analysis | Pandas |
| Visualization | Matplotlib, Seaborn, Plotly |
| Dashboard | Streamlit |
| Mapping | Plotly Choropleth |

---

## 📂 Project Structure

```
Phonepe_project/
│
├── data/
│   ├── aggregated/
│   ├── map/
│   └── top/
│
├── etl/
│   └── phonepeeETL.py
│
├── app/
│   └── app.py
│
└── README.md
```

---

## 🔄 ETL Pipeline

### 1️⃣ Extraction
- Cloned PhonePe Pulse GitHub repository  
- Parsed nested JSON files  

### 2️⃣ Transformation
- Extracted transaction, insurance, and user metrics 

### 3️⃣ Loading
- Created PostgreSQL tables  
- Inserted cleaned data using psycopg2  
- Applied unique constraints  

```sql
ON CONFLICT (state, year, quarter, transaction_type)
DO NOTHING;
```

---

## 📊 Dashboard Modules

### 📈 1. Transaction Analysis
- Yearly growth trend  
- Quarterly state comparison  
- Transaction type analysis  
- Regional contribution  

### 🛡 2. Insurance Penetration
- Insurance growth trends  
- Top & bottom adoption states  
- Penetration percentage vs total transactions  
- Region-wise distribution  

### 🌍 3. Market Expansion Insights
- Emerging high-growth states  
- Quarterly performance comparison  
- Geographic trend analysis  

### 👥 4. User Registration Analysis
- Top states & districts  
- Year-quarter filters  
- Growth trends  

### 📊 5. User Engagement Strategy
- Registered user growth  
- Regional performance comparison  
- Engagement pattern insights  

---

## 🗺️ Interactive India Map

- State-level choropleth visualization  
- Dynamic color scaling  
- Drill-down state interaction  
- Transaction density representation  

---

## 📈 Key Insights

- Southern and Western regions dominate transaction volume.  
- Insurance penetration remains significantly lower than overall transaction growth.    
- Consistent yearly upward transaction trend observed.  

---

## 💡 Business Recommendations

- Increase insurance cross-selling in high-transaction states.  
- Allocate marketing resources to emerging high-growth states showing consistent transaction acceleration..  
- Allocate expansion budget to high-growth regions.  
- Improve engagement strategies in underperforming areas.  

---

## 🚀 Future Enhancements

- District-level GeoJSON integration  
- Real-time API integration  
- Predictive analytics model  
- Cloud deployment  

---

## 👨‍💻 Author

**KARTHIGEYAN**  


---
