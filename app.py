import streamlit as st
import pyodbc
import hashlib

# Function to generate SHA2 hash
def generate_sha(ref_source, source_field, source_value, target_field):
    data = f"{ref_source}|{source_field}|{source_value}|{target_field}"
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

# Function to establish a database connection
def get_db_connection():
    server = 'edf2.database.windows.net'
    database = 'edf'
    username = 'radheybaps'  # Replace with your Azure SQL username
    password = 'kAlAm@100'  # Replace with your Azure SQL password
    driver = '{ODBC Driver 17 for SQL Server}'
    connection_string = f"""
        DRIVER={driver};
        SERVER={server};
        DATABASE={database};
        UID={username};
        PWD={password};
        Encrypt=yes;
        TrustServerCertificate=no;
        Connection Timeout=30;
    """
    return pyodbc.connect(connection_string)

# Function to insert data into the reference_data table
def insert_reference_data(conn, ref_source, source_field, source_value, target_field, target_value, comments, sha_hash):
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM dbo.reference_data WHERE sha_hash = ?", (sha_hash,))
    if cursor.fetchone():
        return False
    cursor.execute(
        "INSERT INTO dbo.reference_data (ref_source, source_field, source_value, target_field, target_value, comments, sha_hash) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (ref_source, source_field, source_value, target_field, target_value, comments, sha_hash)
    )
    conn.commit()
    return True

# Function to fetch all records from the reference_data table
def fetch_reference_data(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dbo.reference_data")
    return cursor.fetchall()

# Streamlit UI
st.title("Reference Data Management App")

ref_source = st.text_input("Reference Source")
source_field = st.text_input("Source Field")
source_value = st.text_input("Source Value")
target_field = st.text_input("Target Field")
target_value = st.text_input("Target Value")
comments = st.text_area("Comments")

if st.button("Submit"):
    conn = get_db_connection()
    sha_hash = generate_sha(ref_source, source_field, source_value, target_field)
    if insert_reference_data(conn, ref_source, source_field, source_value, target_field, target_value, comments, sha_hash):
        st.success("Data inserted successfully!")
    else:
        st.error("Duplicate entry detected.")
    conn.close()

if st.checkbox("Show Existing Records"):
    conn = get_db_connection()
    data = fetch_reference_data(conn)
    st.write("Existing Records:")
    for row in data:
        st.write(row)
    conn.close()
