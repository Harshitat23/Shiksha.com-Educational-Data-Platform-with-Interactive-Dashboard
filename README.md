# EduData Explorer – A Full-Stack Educational Data Platform

EduData Explorer is an end-to-end educational data platform that automates the extraction, structuring, querying, and visualization of college and course information from Shiksha.com. Designed for students, researchers, career counselors, and data enthusiasts, this project empowers users with real-time education data analytics through a robust web scraping engine, RESTful API, and interactive Streamlit dashboard.

# 🎯 Project Motivation

In India and globally, students often struggle with scattered, inconsistent, or outdated college data. This project aims to:
1) Centralize verified information from Shiksha.com
2) Provide intelligent tools to filter, compare, and visualize educational options
3) Help students and parents make data-informed academic decisions
4) Support educational data science use cases for rankings, trends, and cost analysis

# 🚀 Features

🧾 Web Scraping Engine

1) Scrapes college-level and course-level data from Shiksha.com
2) Extracts: College name, Location, Fees (min-max), Courses, Rankings (e.g., NIRF), Accreditation (AICTE, UGC, etc.)
3) Implements: requests with retries, BeautifulSoup parsing, Rate-limiting and polite scraping (delay between requests), JSON/XML export options, Logging for all scraping events and errors

# 📊 Streamlit Dashboard

A modern and user-friendly frontend with:

🔍 College search and dynamic filtering

📍 Location-based filtering and map plots

💰 Fee range sliders and course filters

⭐ Multi-college comparison charts

📈 Trend visualizations for rankings, popularity, and fees

🔄 Real-time updates using the FastAPI endpoints

# 📌 Use Cases

🧑‍🎓 Students comparing colleges across cities or streams

🏫 Career counselors presenting college options to clients

📈 Educational researchers analyzing fee/rank trends

📊 Visualization projects in data science or ML models

# ⚙️ Installation & Setup

1. Clone the Repository
   
git clone https://github.com/your-username/edudata-explorer.git
cd edudata-explorer

2. Install Dependencies
   
pip install -r requirements.txt

3. Run the Scraper
   
python scraper/shiksha_scraper.py

4. Start the API Server
   
uvicorn api.main:app --reload

6. Launch the Streamlit Dashboard
   
streamlit run frontend/dashboard.py
