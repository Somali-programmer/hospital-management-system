import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import hashlib

# Set page configuration
st.set_page_config(
    page_title="Hospital Patient Management System",
    page_icon="🏥",
    layout="wide"
)

# Initialize database
def init_db():
    conn = sqlite3.connect('hospital_management.db')
    cursor = conn.cursor()
    
    # Create tables (same as your desktop app)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT UNIQUE,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            contact TEXT,
            address TEXT,
            blood_type TEXT,
            medical_history TEXT,
            registered_date TEXT
        )
    ''')
    
    # Add other tables as needed
    conn.commit()
    return conn

# Main application
def main():
    st.title("🏥 Hospital Patient Management System")
    st.sidebar.title("Navigation")
    
    # Initialize database
    conn = init_db()
    
    # Navigation menu
    menu = ["Dashboard", "Patient Management", "Appointments", "Billing", "Reports"]
    choice = st.sidebar.selectbox("Select Module", menu)
    
    if choice == "Dashboard":
        show_dashboard(conn)
    elif choice == "Patient Management":
        show_patient_management(conn)
    elif choice == "Appointments":
        show_appointments(conn)
    elif choice == "Billing":
        show_billing(conn)
    elif choice == "Reports":
        show_reports(conn)

def show_dashboard(conn):
    st.header("Dashboard")
    
    # Get statistics
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM patients")
    total_patients = cursor.fetchone()[0]
    
    st.metric("Total Patients", total_patients)
    
    # Recent patients
    st.subheader("Recent Patients")
    cursor.execute("SELECT * FROM patients ORDER BY registered_date DESC LIMIT 10")
    recent_patients = cursor.fetchall()
    
    if recent_patients:
        df = pd.DataFrame(recent_patients, columns=["ID", "Patient ID", "Name", "Age", "Gender", "Contact", "Address", "Blood Type", "Medical History", "Registered Date"])
        st.dataframe(df)
    else:
        st.info("No patients registered yet.")

def show_patient_management(conn):
    st.header("Patient Management")
    
    # Patient registration form
    with st.form("patient_form"):
        st.subheader("Register New Patient")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name")
            age = st.number_input("Age", min_value=0, max_value=150, value=0)
            gender = st.selectbox("Gender", ["", "Male", "Female", "Other"])
            contact = st.text_input("Contact Number")
        
        with col2:
            address = st.text_area("Address")
            blood_type = st.selectbox("Blood Type", ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"])
            medical_history = st.text_area("Medical History")
        
        submitted = st.form_submit_button("Register Patient")
        
        if submitted:
            if name and age > 0 and contact:
                # Generate patient ID
                patient_id = f"P{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO patients (patient_id, name, age, gender, contact, address, blood_type, medical_history, registered_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (patient_id, name, age, gender, contact, address, blood_type, medical_history, datetime.now().date().isoformat())
                    )
                    conn.commit()
                    st.success(f"Patient registered successfully! Patient ID: {patient_id}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.error("Please fill in all required fields (Name, Age, Contact)")
    
    # Patient list
    st.subheader("Patient Records")
    
    # Search functionality
    search_term = st.text_input("Search patients by name or ID")
    
    cursor = conn.cursor()
    if search_term:
        cursor.execute(
            "SELECT * FROM patients WHERE name LIKE ? OR patient_id LIKE ? ORDER BY registered_date DESC",
            (f"%{search_term}%", f"%{search_term}%")
        )
    else:
        cursor.execute("SELECT * FROM patients ORDER BY registered_date DESC")
    
    patients = cursor.fetchall()
    
    if patients:
        df = pd.DataFrame(patients, columns=["ID", "Patient ID", "Name", "Age", "Gender", "Contact", "Address", "Blood Type", "Medical History", "Registered Date"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No patients found.")

# Add other functions for appointments, billing, etc.
def show_appointments(conn):
    st.header("Appointment Management")
    st.info("Appointment module under development")

def show_billing(conn):
    st.header("Billing Management")
    st.info("Billing module under development")

def show_reports(conn):
    st.header("Reports and Analytics")
    st.info("Reports module under development")

if __name__ == "__main__":
    main()