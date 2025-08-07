import streamlit as st
import os
import google.generativeai as genai
from db_connection import fetch_cheque_details
import app  # Import UI module

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Load Custom CSS
app.load_css("styles.css")

# Sidebar Navigation
page = app.render_sidebar()

if page == ":material/home: Home":
    app.render_home()
elif page == ":material/receipt_long: Extract":
    app.render_extract()
elif page == ":material/monitoring: Dashboard":
    data = fetch_cheque_details()
    if data is None or data.empty:
        st.warning(" No cheque data available.")
    else:
        app.render_dashboard(data)  
elif page == ":material/insights: Analytics":
    app.render_analytics()  
