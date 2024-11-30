from utils import database_connection
import sys
from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox, QWidget
from PyQt6.uic import loadUi
from RouteManagement import RouteManagementPage
from StopManagement import StopManagementPage
from BusManagement import BusManagementPage
from BusRouteDriverAssignment import BusRouteDriverPage
from DriverManagement import DriverManagementPage
from PassengerManagement import PassengerManagementPage

class AdminSignup(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("Adminsignup.ui", self)
        self.populate_station_combobox()
        self.signupbtn.clicked.connect(self.signup_admin)
        self.alreadybtn.clicked.connect(self.go_to_login)

    def populate_station_combobox(self):
        connection = database_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT station_id, station_name FROM STATION_area")
            stations = cursor.fetchall()
            self.StationcomboBox.clear()
            if not stations:
                QMessageBox.warning(self, "Warning", "No stations found in the database.")
                return
            for station_id, station_name in stations:
                self.StationcomboBox.addItem(station_name, station_id)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load stations: {e}")
        finally:
            connection.close()

    def signup_admin(self):
        import re
        name = self.namelineEdit.text()
        email = self.emaillineEdit.text()
        phone = self.phonelineEdit.text()
        password = self.passlineEdit.text()
        confirmpass = self.confirmPasslineEdit.text()
        station_id = self.StationcomboBox.currentData()
        if not self.iagreecheckbox.isChecked():
            QMessageBox.warning(self, "Warning", "You must agree to the terms and conditions to register.")
            return
        if not name or not email or not phone or not password or not confirmpass or not station_id:
            QMessageBox.warning(self, "Warning", "Please fill in all fields!")
            return
        if password != confirmpass:
            QMessageBox.warning(self, "Warning", "Passwords do not match!")
            return
        if len(password) < 8 or not any(char.isdigit() for char in password):
            QMessageBox.warning(self, "Warning", "Password must be at least 8 characters long and include a number.")
            return
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            QMessageBox.warning(self, "Warning", "Invalid email format!")
            return
        if not phone.isdigit():
            QMessageBox.warning(self, "Warning", "Phone number must contain only digits.")
            return
        connection = database_connection()
        cursor = connection.cursor()
        try:
            query = """
            INSERT INTO Transport_operator (Name, Email, Phone, Password, Station_id)
            VALUES (?, ?, ?, ?, ?);
            """
            cursor.execute(query, (name, email, phone, password, station_id))
            connection.commit()
            cursor.execute("SELECT MAX(Operator_ID) AS LastOperatorID FROM Transport_operator")
            admin_id = cursor.fetchone()[0]
            if admin_id is None:
                raise Exception("Failed to retrieve the last inserted operator ID")
            QMessageBox.information(self, "Success", f"Operator registered successfully with ID: {admin_id}!")
            self.go_to_dashboard(admin_id=admin_id)
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                QMessageBox.warning(self, "Warning", "This email is already registered!")
            else:
                QMessageBox.critical(self, "Error", f"Failed to register admin: {e}")
        finally:
            connection.close()

    def go_to_login(self):
        self.login_window = AdminLogin()
        self.login_window.show()
        self.close()

    def go_to_dashboard(self, admin_id):
        self.dashboard_window = AdminDashboard(admin_id=admin_id)
        self.dashboard_window.show()
        self.close()

class AdminLogin(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("common_login.ui", self)
        self.Loginbtn.clicked.connect(self.login_admin)
        self.newUserbtn.clicked.connect(self.go_to_signup)

    def login_admin(self):
        user_id = self.IDlineEdit.text()
        password = self.passLinedit.text()
        role = self.role_combobox.currentText()
        if not user_id or not password:
            QMessageBox.warning(self, "Warning", "Please fill in both ID and Password!")
            return
        connection = database_connection()
        cursor = connection.cursor()
        try:
            if role == "Admin":
                query = "SELECT Operator_id FROM Transport_operator WHERE Operator_id = ? AND password = ?"
            elif role == "Driver":
                query = "SELECT Driver_ID FROM Driver WHERE Driver_ID = ? AND Password = ?"
            else:
                query = "SELECT Passenger_ID FROM Passenger WHERE Passenger_ID = ? AND Password = ?"
            cursor.execute(query, (user_id, password))
            result = cursor.fetchone()
            if result:
                admin_id = result[0]
                QMessageBox.information(self, "Success", "Login successful!")
                self.go_to_dashboard(admin_id=admin_id)
            else:
                QMessageBox.warning(self, "Error", "Invalid credentials or user does not exist.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to login: {e}")
        finally:
            connection.close()

    def go_to_dashboard(self, admin_id=None):
        self.dashboard_window = AdminDashboard(admin_id=admin_id)
        self.dashboard_window.show()
        self.close()

    def go_to_signup(self):
        self.login_window = AdminSignup()
        self.login_window.show()
        self.close()

class AdminDashboard(QMainWindow):
    def __init__(self, admin_id, parent= None):
        super(AdminDashboard, self).__init__(parent)
        self.admin_id = admin_id
        loadUi("DashboardAdmin.ui", self)
        self.setup_ui()

    def setup_ui(self):
        if self.admin_id:
            self.adidtxtbrowser.setText(f"{self.admin_id}")
        self.route_man.clicked.connect(self.showRouteManagement)
        self.stop_man.clicked.connect(self.showStopManagement)
        self.busroutedriver.clicked.connect(self.showBusRouteDriver)
        self.bus_man.clicked.connect(self.showBusManagement)
        self.driver_man.clicked.connect(self.showDriverManagement)
        self.pass_man.clicked.connect(self.showPassengerManagement)

    def showRouteManagement(self):
        self.route_window = RouteManagementPage(admin_id=self.admin_id)
        self.route_window.show()
        self.close()
    
    def showStopManagement(self):
        self.stop_window = StopManagementPage(admin_id=self.admin_id)
        self.stop_window.show()
        self.close()

    def showBusRouteDriver(self):
        self.bus_route_window = BusRouteDriverPage(admin_id=self.admin_id)
        self.bus_route_window.show()
        self.close()

    def showBusManagement(self):
        self.bus_window = BusManagementPage(admin_id=self.admin_id)
        self.bus_window.show()
        self.close()

    def showDriverManagement(self):
        self.driver_window = DriverManagementPage(admin_id=self.admin_id)
        self.driver_window.show()
        self.close()

    def showPassengerManagement(self):
        self.passenger_window = PassengerManagementPage(admin_id=self.admin_id)
        self.passenger_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminSignup()
    window.show()
    sys.exit(app.exec())
