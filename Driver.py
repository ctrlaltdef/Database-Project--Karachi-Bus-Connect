from utils import database_connection
import sys
import pyodbc
from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox, QWidget, QTableWidgetItem
from PyQt6.uic import loadUi

connection = database_connection()
cursor = connection.cursor()


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
        self.Routes_assigned.currentTextChanged.connect(self.display_stops)
        self.Reached_button.clicked.connect(self.mark_stop_as_reached)

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
        self.display_routes()
        
    def display_routes(self):
        try:
            selected_bus_id = self.Buses_assigned.currentText()

            if selected_bus_id:
                # Fetch routes for the selected bus ID
                query = """
                SELECT R.starting_point, R.Destination
                FROM bus_route BR
                INNER JOIN Route R on R.route_id = BR.route_id
                WHERE Bus_id = ?
                """
                cursor.execute(query, (selected_bus_id,))
                # results = cursor.fetchall()
                results = [f"{row[0]} - {row[1]}" for row in cursor.fetchall()] 

                # Clear and populate the routes dropdown or list
                self.Routes_assigned.clear()
                self.Routes_assigned.addItems(results)

                self.display_stops() 

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch routes: {e}")

    def display_stops(self):
        try:
            selected_route = self.Routes_assigned.currentText()

            if selected_route:
                # Extract the starting point and destination from the selected route
                starting_point, destination = selected_route.split(" - ")

                # Fetch the Route_id based on the selected starting point and destination
                query = """
                SELECT route_id 
                FROM Route
                WHERE starting_point = ? AND destination = ?
                """
                cursor.execute(query, (starting_point, destination))
                route_id_result = cursor.fetchone()

                if route_id_result:
                    route_id = route_id_result[0]

                    # Fetch stops for the selected route
                    query = """
                    SELECT S.stop_name, CONVERT(VARCHAR(8), S.estimated_reaching_time, 108) AS reaching_time
                    FROM Route_Stop RS
                    INNER JOIN Stop S ON RS.stop_id = S.stop_id
                    WHERE RS.route_id = ?
                    """
                    cursor.execute(query, (route_id,))
                    stops = cursor.fetchall()  # Fetch all stops for the route

                    # Clear the table before adding new rows
                    self.Stops_table.setRowCount(0)

                    # Set up the table headers
                    self.Stops_table.setColumnCount(2)
                    self.Stops_table.setHorizontalHeaderLabels(["Stop Name", "Estimated Reaching Time"])

                    # Populate the table with the stops
                    for row_number, (stop_name, reaching_time) in enumerate(stops):
                        self.Stops_table.insertRow(row_number)
                        self.Stops_table.setItem(row_number, 0, QTableWidgetItem(stop_name))
                        self.Stops_table.setItem(row_number, 1, QTableWidgetItem(str(reaching_time)))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch stops: {e}")

    def mark_stop_as_reached(self):
        try:
            # Ensure a stop row is selected
            selected_row = self.Stops_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Warning", "Please select a stop from the table!")
                return

            # Get stop_name and bus_id
            stop_name_item = self.Stops_table.item(selected_row, 0)  
            if not stop_name_item:
                QMessageBox.warning(self, "Warning", "No stop selected!")
                return

            stop_name = stop_name_item.text()
            estimated_time = self.Stops_table.item(selected_row, 1).text()  

            # Get selected bus
            selected_bus = self.Buses_assigned.currentText()
            if not selected_bus:
                QMessageBox.warning(self, "Warning", "No bus is selected!")
                return

            
            bus_id = int(selected_bus)  

            # Fetch stop_id based on the stop_name
            cursor.execute("SELECT Stop_id FROM Stop WHERE Stop_name = ?", (stop_name,))
            stop_id_result = cursor.fetchone()

            if not stop_id_result:
                QMessageBox.critical(self, "Error", "Stop not found!")
                return

            stop_id = stop_id_result[0]

            # Update the d_status 
            update_query = """
            UPDATE Bus_stop
            SET d_status = 'Reached'
            WHERE bus_id = ? AND stop_id = ?
            """
            cursor.execute(update_query, (bus_id, stop_id))
            connection.commit()

            # Apply strikethrough 
            for column in range(self.Stops_table.columnCount()):
                item = self.Stops_table.item(selected_row, column)
                if item:
                    font = item.font()
                    font.setStrikeOut(True)
                    item.setFont(font)

            QMessageBox.information(self, "Success", f"Stop '{stop_name}' marked as reached!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to mark stop as reached: {e}")
