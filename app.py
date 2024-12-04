import streamlit as st
import pyodbc
import hashlib
import pandas as pd

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
    cursor.execute("SELECT ref_source, source_field, source_value, target_field, target_value, comments, sha_hash FROM dbo.reference_data")
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    return pd.DataFrame.from_records(rows, columns=columns)

# Function to update a record in the reference_data table
def update_reference_data(conn, updated_data):
    cursor = conn.cursor()
    for index, row in updated_data.iterrows():
        cursor.execute(
            "UPDATE dbo.reference_data "
            "SET ref_source = ?, source_field = ?, source_value = ?, target_field = ?, target_value = ?, comments = ? "
            "WHERE sha_hash = ?",
            (row['ref_source'], row['source_field'], row['source_value'], row['target_field'], row['target_value'], row['comments'], row['sha_hash'])
        )
    conn.commit()

# Function to delete a record from the reference_data table
def delete_reference_data(conn, sha_hash):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dbo.reference_data WHERE sha_hash = ?", (sha_hash,))
    conn.commit()

# Streamlit UI
st.title("Reference Data Management App")

# Input form for adding new reference data
st.subheader("Add New Reference Data")
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

# Display existing records by default and enable editing only
st.subheader("Existing Records")
conn = get_db_connection()
data = fetch_reference_data(conn)

if not data.empty:
    # Display editable table but disable adding new rows
    edited_data = st.data_editor(
        data,
        key="data_editor",
        num_rows="fixed",  # Disable adding new rows
        use_container_width=True
    )

    # Save changes
    if st.button("Save Changes"):
        update_reference_data(conn, edited_data)
        st.success("Changes saved successfully!")

    # Delete selected row
    delete_index = st.number_input("Enter the row index to delete:", min_value=0, max_value=len(data) - 1, step=1)
    if st.button("Delete Selected Row"):
        sha_hash_to_delete = data.iloc[delete_index]['sha_hash']
        delete_reference_data(conn, sha_hash_to_delete)
        st.success("Row deleted successfully!")
else:
    st.write("No records found.")

conn.close()
