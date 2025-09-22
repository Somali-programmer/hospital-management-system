import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
from datetime import datetime, date
import json
import hashlib
import csv
from tkcalendar import DateEntry  # Requires pip install tkcalendar

class HospitalPatientManagementSystem:
    def __init__(self, root):
        """
        Initialize the Hospital Patient Management System.
        
        Parameters:
        root (tk.Tk): The main window of the application
        """
        self.root = root
        self.root.title("Hospital Patient Management System.                       developer by Somali Programmer")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f8ff')  # Alice blue background
        
        # Initialize database
        self.init_db()
        
        # Setup the main interface
        self.setup_ui()
        
        # Load initial data
        self.load_patients()
        
    def init_db(self):
        """
        Initialize the SQLite database and create necessary tables if they don't exist.
        Creates tables for patients, appointments, bills, and users.
        """
        self.conn = sqlite3.connect('hospital_management.db')
        self.cursor = self.conn.cursor()
        
        # Create patients table
        self.cursor.execute('''
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
        
        # Create appointments table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT,
                doctor_name TEXT,
                date TEXT,
                time TEXT,
                reason TEXT,
                status TEXT DEFAULT 'Scheduled',
                FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
            )
        ''')
        
        # Create bills table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT,
                amount REAL,
                date_issued TEXT,
                date_paid TEXT,
                status TEXT DEFAULT 'Unpaid',
                services TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
            )
        ''')
        
        # Create users table for authentication
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT
            )
        ''')
        
        # Insert default admin user if not exists
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
        if self.cursor.fetchone()[0] == 0:
            hashed_password = hashlib.sha256("admin123".encode()).hexdigest()
            self.cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ('admin', hashed_password, 'admin')
            )
        
        self.conn.commit()
    
    def setup_ui(self):
        """
        Set up the user interface with tabs for different functionalities.
        Creates the main notebook (tab control) and adds tabs for each module.
        """
        # Create style for widgets
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        self.root.configure(bg='#f0f8ff')
        style.configure('TNotebook', background='#f0f8ff')
        style.configure('TFrame', background='#f0f8ff')
        style.configure('TLabel', background='#f0f8ff', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10), background='#e1f5fe')
        style.map('TButton', background=[('active', '#b3e5fc')])
        
        # Create notebook (tab control)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create frames for each tab
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.patient_frame = ttk.Frame(self.notebook)
        self.appointment_frame = ttk.Frame(self.notebook)
        self.billing_frame = ttk.Frame(self.notebook)
        self.reports_frame = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.dashboard_frame, text='Dashboard')
        self.notebook.add(self.patient_frame, text='Patient Management')
        self.notebook.add(self.appointment_frame, text='Appointments')
        self.notebook.add(self.billing_frame, text='Billing')
        self.notebook.add(self.reports_frame, text='Reports')
        
        # Setup each tab
        self.setup_dashboard_tab()
        self.setup_patient_tab()
        self.setup_appointment_tab()
        self.setup_billing_tab()
        self.setup_reports_tab()
    
    def setup_dashboard_tab(self):
        """
        Set up the dashboard tab with overview information and statistics.
        Displays key metrics about patients, appointments, and billing.
        """
        # Dashboard title
        title_label = ttk.Label(self.dashboard_frame, text="Hospital Management Dashboard", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Create frames for statistics
        stats_frame = ttk.Frame(self.dashboard_frame)
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        # Get statistics from database
        total_patients = self.get_statistic("SELECT COUNT(*) FROM patients")
        total_appointments = self.get_statistic("SELECT COUNT(*) FROM appointments")
        pending_bills = self.get_statistic("SELECT COUNT(*) FROM bills WHERE status='Unpaid'")
        revenue = self.get_statistic("SELECT SUM(amount) FROM bills WHERE status='Paid'") or 0
        
        # Display statistics
        stats_data = [
            ("Total Patients", total_patients, "#e67104"),
            ("Total Appointments", total_appointments, "#fff3e0"),
            ("Pending Bills", pending_bills, "#ffd519"),
            ("Revenue ($)", revenue, "#e8f5e9")
        ]
        
        for i, (title, value, color) in enumerate(stats_data):
            frame = tk.Frame(stats_frame, bg=color, relief=tk.RAISED, bd=2)
            frame.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            
            ttk.Label(frame, text=title, font=('Arial', 12, 'bold'), background=color).pack(pady=5)
            ttk.Label(frame, text=str(value), font=('Arial', 14), background=color).pack(pady=5)
            
            stats_frame.columnconfigure(i, weight=1)
        
        # Recent activity frame
        activity_frame = ttk.LabelFrame(self.dashboard_frame, text="Recent Activity")
        activity_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create text widget for activity log
        self.activity_text = scrolledtext.ScrolledText(activity_frame, height=10, font=('Arial', 10))
        self.activity_text.pack(fill='both', expand=True, padx=10, pady=10)
        self.activity_text.insert(tk.END, "System initialized at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.activity_text.config(state=tk.DISABLED)
    
    def get_statistic(self, query):
        """
        Execute a SQL query and return a single statistic value.
        
        Parameters:
        query (str): The SQL query to execute
        
        Returns:
        result: The result of the query (single value)
        """
        self.cursor.execute(query)
        result = self.cursor.fetchone()[0]
        return result if result else 0
    
    def setup_patient_tab(self):
        """
        Set up the patient management tab with forms and patient list.
        Includes functionality to add, update, and delete patient records.
        """
        # Create paned window for split view
        paned_window = ttk.PanedWindow(self.patient_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left frame for form
        form_frame = ttk.Frame(paned_window)
        paned_window.add(form_frame, weight=1)
        
        # Right frame for patient list
        list_frame = ttk.Frame(paned_window)
        paned_window.add(list_frame, weight=2)
        
        # Patient form
        form_title = ttk.Label(form_frame, text="Patient Registration Form", font=('Arial', 14, 'bold'))
        form_title.pack(pady=10)
        
        # Form fields
        fields = [
            ("Name", "name_entry"),
            ("Age", "age_entry"),
            ("Gender", "gender_combo"),
            ("Contact", "contact_entry"),
            ("Address", "address_entry"),
            ("Blood Type", "blood_type_combo"),
            ("Medical History", "medical_history_text")
        ]
        
        self.form_widgets = {}
        
        for field, key in fields:
            frame = ttk.Frame(form_frame)
            frame.pack(fill='x', padx=10, pady=5)
            
            ttk.Label(frame, text=field + ":", width=15).pack(side=tk.LEFT)
            
            if key.endswith("_entry"):
                widget = ttk.Entry(frame, width=25)
                widget.pack(side=tk.LEFT, fill='x', expand=True)
                self.form_widgets[key] = widget
            elif key.endswith("_combo"):
                if key == "gender_combo":
                    options = ["Male", "Female", "Other"]
                else:  # blood_type_combo
                    options = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"]
                
                widget = ttk.Combobox(frame, values=options, width=23, state="readonly")
                widget.pack(side=tk.LEFT, fill='x', expand=True)
                self.form_widgets[key] = widget
            elif key.endswith("_text"):
                # For medical history, we'll create a scrolled text in a separate frame
                pass
        
        # Medical history in its own frame
        medical_frame = ttk.Frame(form_frame)
        medical_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(medical_frame, text="Medical History:", width=15).pack(side=tk.LEFT, anchor='n')
        medical_history_text = scrolledtext.ScrolledText(medical_frame, height=4, width=25)
        medical_history_text.pack(side=tk.LEFT, fill='x', expand=True)
        self.form_widgets["medical_history_text"] = medical_history_text
        
        # Button frame
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Register Patient", command=self.register_patient).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update", command=self.update_patient).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_form).pack(side=tk.LEFT, padx=5)
        
        # Patient list
        list_title = ttk.Label(list_frame, text="Patient Records", font=('Arial', 14, 'bold'))
        list_title.pack(pady=10)
        
        # Search frame
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.search_patients)
        
        ttk.Button(search_frame, text="Refresh", command=self.load_patients).pack(side=tk.RIGHT)
        
        # Treeview for patient records
        columns = ("ID", "Name", "Age", "Gender", "Contact", "Registered Date")
        self.patient_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.patient_tree.heading(col, text=col)
            self.patient_tree.column(col, width=100)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.patient_tree.yview)
        self.patient_tree.configure(yscrollcommand=scrollbar.set)
        
        self.patient_tree.pack(side=tk.LEFT, fill='both', expand=True, padx=(10, 0))
        scrollbar.pack(side=tk.RIGHT, fill='y', padx=(0, 10))
        
        # Bind selection event
        self.patient_tree.bind('<<TreeviewSelect>>', self.on_patient_select)
        
        # Delete button
        ttk.Button(list_frame, text="Delete Selected", command=self.delete_patient).pack(pady=5)
    
    def register_patient(self):
        """
        Register a new patient by collecting data from the form and saving to database.
        Validates form data and shows appropriate messages for success or errors.
        """
        # Get data from form
        name = self.form_widgets["name_entry"].get().strip()
        age = self.form_widgets["age_entry"].get().strip()
        gender = self.form_widgets["gender_combo"].get().strip()
        contact = self.form_widgets["contact_entry"].get().strip()
        address = self.form_widgets["address_entry"].get().strip()
        blood_type = self.form_widgets["blood_type_combo"].get().strip()
        medical_history = self.form_widgets["medical_history_text"].get("1.0", tk.END).strip()
        
        # Validate required fields
        if not name or not age or not contact:
            messagebox.showerror("Error", "Name, Age, and Contact are required fields!")
            return
        
        try:
            age = int(age)
            if age <= 0 or age > 150:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Age must be a valid number between 1 and 150!")
            return
        
        # Generate unique patient ID
        patient_id = "P" + datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Insert into database
        try:
            self.cursor.execute(
                "INSERT INTO patients (patient_id, name, age, gender, contact, address, blood_type, medical_history, registered_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (patient_id, name, age, gender, contact, address, blood_type, medical_history, date.today().isoformat())
            )
            self.conn.commit()
            
            messagebox.showinfo("Success", f"Patient registered successfully!\nPatient ID: {patient_id}")
            self.clear_form()
            self.load_patients()
            
            # Log activity
            self.log_activity(f"Registered new patient: {name} (ID: {patient_id})")
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error saving patient: {str(e)}")
    
    def update_patient(self):
        """
        Update an existing patient's record with data from the form.
        Requires a patient to be selected from the list first.
        """
        selection = self.patient_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a patient to update!")
            return
        
        # Get patient ID from selected item
        item = self.patient_tree.item(selection[0])
        patient_id = item['values'][0]
        
        # Get updated data from form
        name = self.form_widgets["name_entry"].get().strip()
        age = self.form_widgets["age_entry"].get().strip()
        gender = self.form_widgets["gender_combo"].get().strip()
        contact = self.form_widgets["contact_entry"].get().strip()
        address = self.form_widgets["address_entry"].get().strip()
        blood_type = self.form_widgets["blood_type_combo"].get().strip()
        medical_history = self.form_widgets["medical_history_text"].get("1.0", tk.END).strip()
        
        # Validate required fields
        if not name or not age or not contact:
            messagebox.showerror("Error", "Name, Age, and Contact are required fields!")
            return
        
        try:
            age = int(age)
            if age <= 0 or age > 150:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Age must be a valid number between 1 and 150!")
            return
        
        # Update database
        try:
            self.cursor.execute(
                "UPDATE patients SET name=?, age=?, gender=?, contact=?, address=?, blood_type=?, medical_history=? WHERE patient_id=?",
                (name, age, gender, contact, address, blood_type, medical_history, patient_id)
            )
            self.conn.commit()
            
            messagebox.showinfo("Success", "Patient record updated successfully!")
            self.load_patients()
            
            # Log activity
            self.log_activity(f"Updated patient record: {name} (ID: {patient_id})")
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error updating patient: {str(e)}")
    
    def delete_patient(self):
        """
        Delete the selected patient record from the database.
        Asks for confirmation before deleting to prevent accidental deletions.
        """
        selection = self.patient_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a patient to delete!")
            return
        
        # Get patient details from selected item
        item = self.patient_tree.item(selection[0])
        patient_id, name = item['values'][0], item['values'][1]
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete patient {name} (ID: {patient_id})?"):
            return
        
        # Delete from database
        try:
            self.cursor.execute("DELETE FROM patients WHERE patient_id=?", (patient_id,))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Patient record deleted successfully!")
            self.clear_form()
            self.load_patients()
            
            # Log activity
            self.log_activity(f"Deleted patient record: {name} (ID: {patient_id})")
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error deleting patient: {str(e)}")
    
    def clear_form(self):
        """
        Clear all input fields in the patient registration form.
        """
        for key, widget in self.form_widgets.items():
            if key.endswith("_entry"):
                widget.delete(0, tk.END)
            elif key.endswith("_combo"):
                widget.set('')
            elif key.endswith("_text"):
                widget.delete("1.0", tk.END)
    
    def load_patients(self):
        """
        Load patient records from the database and display them in the treeview.
        """
        # Clear existing data
        for item in self.patient_tree.get_children():
            self.patient_tree.delete(item)
        
        # Fetch patients from database
        try:
            self.cursor.execute("SELECT patient_id, name, age, gender, contact, registered_date FROM patients ORDER BY registered_date DESC")
            rows = self.cursor.fetchall()
            
            for row in rows:
                self.patient_tree.insert('', tk.END, values=row)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading patients: {str(e)}")
    
    def search_patients(self, event=None):
        """
        Search for patients based on the text in the search entry.
        Filters the patient list in real-time as the user types.
        
        Parameters:
        event: The key release event that triggered the search
        """
        query = self.search_entry.get().strip()
        
        # Clear existing data
        for item in self.patient_tree.get_children():
            self.patient_tree.delete(item)
        
        # Fetch filtered patients from database
        try:
            if query:
                search_pattern = f"%{query}%"
                self.cursor.execute(
                    "SELECT patient_id, name, age, gender, contact, registered_date FROM patients WHERE name LIKE ? OR patient_id LIKE ? OR contact LIKE ? ORDER BY registered_date DESC",
                    (search_pattern, search_pattern, search_pattern)
                )
            else:
                self.cursor.execute("SELECT patient_id, name, age, gender, contact, registered_date FROM patients ORDER BY registered_date DESC")
            
            rows = self.cursor.fetchall()
            
            for row in rows:
                self.patient_tree.insert('', tk.END, values=row)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error searching patients: {str(e)}")
    
    def on_patient_select(self, event):
        """
        Handle event when a patient is selected from the list.
        Populates the form with the selected patient's data.
        
        Parameters:
        event: The selection event that was triggered
        """
        selection = self.patient_tree.selection()
        if not selection:
            return
        
        # Get patient ID from selected item
        item = self.patient_tree.item(selection[0])
        patient_id = item['values'][0]
        
        # Fetch complete patient data
        try:
            self.cursor.execute("SELECT * FROM patients WHERE patient_id=?", (patient_id,))
            patient = self.cursor.fetchone()
            
            if patient:
                # Populate form with patient data
                self.clear_form()
                
                self.form_widgets["name_entry"].insert(0, patient[2])
                self.form_widgets["age_entry"].insert(0, str(patient[3]))
                self.form_widgets["gender_combo"].set(patient[4] or "")
                self.form_widgets["contact_entry"].insert(0, patient[5] or "")
                self.form_widgets["address_entry"].insert(0, patient[6] or "")
                self.form_widgets["blood_type_combo"].set(patient[7] or "")
                self.form_widgets["medical_history_text"].insert("1.0", patient[8] or "")
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading patient details: {str(e)}")
    
    def setup_appointment_tab(self):
        """
        Set up the appointments tab with scheduling functionality.
        Includes forms to create, update, and manage patient appointments.
        """
        # Appointment management UI will be implemented here
        label = ttk.Label(self.appointment_frame, text="Appointment Management - Under Construction", font=('Arial', 14))
        label.pack(pady=50)
    
    def setup_billing_tab(self):
        """
        Set up the billing tab with invoice creation and payment processing.
        Includes forms to create bills, record payments, and view billing history.
        """
        # Billing management UI will be implemented here
        label = ttk.Label(self.billing_frame, text="Billing Management - Under Construction", font=('Arial', 14))
        label.pack(pady=50)
    
    def setup_reports_tab(self):
        """
        Set up the reports tab with various reporting options.
        Includes patient statistics, financial reports, and export functionality.
        """
        # Reports UI will be implemented here
        label = ttk.Label(self.reports_frame, text="Reports and Analytics - Under Construction", font=('Arial', 14))
        label.pack(pady=50)
    
    def log_activity(self, message):
        """
        Log an activity message to the dashboard activity log.
        
        Parameters:
        message (str): The activity message to log
        """
        self.activity_text.config(state=tk.NORMAL)
        self.activity_text.insert(tk.END, f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")
        self.activity_text.see(tk.END)  # Auto-scroll to bottom
        self.activity_text.config(state=tk.DISABLED)
    
    def __del__(self):
        """
        Destructor to ensure database connection is closed when the application exits.
        """
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    """
    Main function to initialize and run the Hospital Patient Management System.
    Creates the main window and starts the Tkinter event loop.
    """
    root = tk.Tk()
    app = HospitalPatientManagementSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()