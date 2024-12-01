from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt6.uic import loadUi
import sys
from utils import database_connection
from passengeroperations import RouteBookingPage


class PassengerSignup(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("passengersignup.ui", self)

        # Connect buttons to their respective methods
        self.pushButton.clicked.connect(self.signup_passenger)  # Sign Up button
        self.pushButton_2.clicked.connect(self.show_login_screen)  # Already have an account button

    def signup_passenger(self):
        """Handles the passenger signup process."""
        import re

        # Fetch data from input fields
        name = self.lineEdit.text()
        email = self.lineEdit_2.text()
        password = self.lineEdit_3.text()
        confirmpass = self.lineEdit_4.text()
        phone = self.lineEdit_5.text()

        # Validate form inputs
        if not self.checkBox_3.isChecked():
            QMessageBox.warning(self, "Warning", "You must agree to the terms and conditions to register.")
            return

        if not name or not email or not phone or not password or not confirmpass:
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

        # Insert the data into the database
        connection = database_connection()
        cursor = connection.cursor()
        try:
            query = """
            INSERT INTO Passenger (Name, Email, Phone, Password)
            VALUES (?, ?, ?, ?);
            """
            cursor.execute(query, (name, email, phone, password))
            connection.commit()

            # Fetch the newly created Passenger_ID
            cursor.execute("SELECT MAX(Passenger_ID) FROM Passenger")
            passenger_id = cursor.fetchone()[0]

            QMessageBox.information(self, "Success", f"Registration successful! Your Passenger ID is {passenger_id}.")
            self.open_passenger_operations(passenger_id)
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                QMessageBox.warning(self, "Warning", "This email is already registered!")
            else:
                QMessageBox.critical(self, "Error", f"An error occurred: {e}")
        finally:
            connection.close()

    def show_login_screen(self):
        """Navigates to the PassengerLogin screen."""
        self.login_window = PassengerLogin()
        self.login_window.show()
        self.close()

    def open_passenger_operations(self, passenger_id):
        """Opens the RouteBookingPage."""
        self.operations_window = RouteBookingPage(passenger_id)
        self.operations_window.show()
        self.close()


class PassengerLogin(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("common_login.ui", self)

        # Connect buttons to their respective methods
        self.Loginbtn.clicked.connect(self.login_passenger)  # Login button
        self.newUserbtn.clicked.connect(self.show_signup_screen)  # New User button

    def login_passenger(self):
        """Handles passenger login."""
        passenger_id = self.IDlineEdit.text()
        password = self.passLinedit.text()

        if not passenger_id or not password:
            QMessageBox.warning(self, "Warning", "Please fill in both ID and Password!")
            return

        connection = database_connection()
        cursor = connection.cursor()
        try:
            query = "SELECT Passenger_ID FROM Passenger WHERE Passenger_ID = ? AND Password = ?"
            cursor.execute(query, (passenger_id, password))
            result = cursor.fetchone()

            if result:
                QMessageBox.information(self, "Success", "Login successful!")
                self.open_passenger_operations(result[0])
            else:
                QMessageBox.warning(self, "Error", "Invalid credentials!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
        finally:
            connection.close()

    def show_signup_screen(self):
        """Navigates to the PassengerSignup screen."""
        self.signup_window = PassengerSignup()
        self.signup_window.show()
        self.close()

    def open_passenger_operations(self, passenger_id):
        """Opens the RouteBookingPage."""
        self.operations_window = RouteBookingPage(passenger_id)
        self.operations_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PassengerSignup()
    window.show()
    sys.exit(app.exec())
