import pyodbc
import sys
from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox, QWidget
from PyQt6.uic import loadUi

server = 'localhost'
database = 'KBusConnect'  # Name of your Northwind database
use_windows_authentication = False  # Set to True to use Windows Authentication
username = 'sa'  # Specify a username if not using Windows Authentication
password = 'Fall2022.dbms'  # Specify a password if not using Windows Authentication


# Create the connection string based on the authentication method chosen
if use_windows_authentication:
    connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
else:
    connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

# Establish a connection to the database
connection = pyodbc.connect(connection_string)

# Create a cursor to interact with the database
cursor = connection.cursor()

# add check of whether the user already exists...
class DriverSignup(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("driver_signup.ui", self)
        self.alreadyaccbtn.clicked.connect(self.go_to_commonlogin)
        self.signupBtn.clicked.connect(self.driver_registration)

    def go_to_commonlogin(self):
        from MergeLogin import CommonLogin 
        self.common_window = CommonLogin()
        self.common_window.show()
        self.close()

    def driver_registration(self):
        # Retrieve input values from the UI
        name = self.Name.text()
        cnic = self.CNIC.text()
        phone_number = self.PhoneNum.text()
        password = self.Pass.text()
        confirm_password = self.confirmPass.text()
        terms_checked = self.agree_checkbox.isChecked()
        area = self.area_combobox.currentText()

        # Validation checks
        if not name or not cnic or not phone_number or not password or not confirm_password or not area:
            QMessageBox.warning(self, "Warning", "Please fill in all the fields!")
            return

        if not terms_checked:
            QMessageBox.warning(self, "Warning", "You must agree to the terms and conditions to proceed.")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Warning", "Passwords do not match!")
            return

        try:
            station_query = "SELECT Station_id FROM station_area WHERE station_name = ?"
            cursor.execute(station_query, (area,))
            station_id_result = cursor.fetchone()  # Retrieve the first matching record
            
            if station_id_result:  # Check if a Station_id was found
                station_id = station_id_result[0]  # Extract Station_id from the result tuple
                
            # Insert driver details into the database
            query = """
                INSERT INTO Driver (Name, CNIC, phone, Password, Account_status, Station_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (name, cnic, phone_number, password,"Active", station_id))
            connection.commit()
            driver_query = "SELECT Driver_id FROM Driver WHERE name = ? AND cnic = ? AND phone = ? AND password = ? AND station_id = ?"
            cursor.execute(driver_query, (name, cnic, phone_number, password, station_id))
            driver_id_result = cursor.fetchone()
            
            if driver_id_result:
                driver_id = driver_id_result[0]
                QMessageBox.information(self, "Success", f"Driver registration successful! Your Driver ID is {driver_id}")
                self.go_to_commonlogin()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Registration failed: {e}")


class DriverDashboard(QMainWindow):
    def __init__(self, driver_id):
        super().__init__()
        loadUi("drivers_screen.ui", self)
        self.driver_id = driver_id
        self.set_driver_id()
        self.display_bus_ids()
        self.Buses_assigned.currentTextChanged.connect(self.display_routes)


    def set_driver_id(self):
        self. Driver_ID_display.setText(f"Driver ID: {self.driver_id}")
    
    def display_bus_ids(self):
        
        # Fetch buses assigned to the driver
        query = "SELECT Bus_id FROM Bus_Driver WHERE Driver_id = ?"
        cursor.execute(query, (self.driver_id,))
        bus_ids = [str(row[0]) for row in cursor.fetchall()]

        # Clear the combobox and add bus IDs
        self.Buses_assigned.clear()
        self.Buses_assigned.addItems(bus_ids)
        
    def display_routes(self):
        try:
            selected_bus_id = self.bus_combobox.currentText()

            if selected_bus_id:
                # Fetch routes for the selected bus ID
                query = "SELECT Route_name FROM Route WHERE Bus_id = ?"
                cursor.execute(query, (selected_bus_id,))
                routes = [f"{row[1]} - {row[2]}" for row in cursor.fetchall()] 

                # Clear and populate the routes dropdown or list
                self.routes_combobox.clear()
                self.routes_combobox.addItems(routes)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch routes: {e}")




