#!/bin/bash

# Ensure the correct permissions for the startup script
chmod +x startup.sh

# Run Streamlit app with the appropriate parameters
streamlit run app.py --server.port=$PORT --server.headless=true --server.enableCORS=false
