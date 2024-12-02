from utils import database_connection
import sys
import pyodbc
from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox, QWidget, QComboBox
from PyQt6.uic import loadUi

connection = database_connection()
cursor = connection.cursor()



class CommonLogin(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("common_login.ui", self)
        self.Loginbtn.clicked.connect(self.login)
        self.newUserbtn.clicked.connect(self.signup)


    def signup(self):
        from Driver import DriverSignup
        self.driver_window = DriverSignup()
        self.driver_window.show()
        self.close()

    def login(self):
            check = str(10)
            user_id = self.IDlineEdit.text()
            password = self.passLinedit.text()
            role = self.role_combobox.currentText()

            if not user_id or not password:
                QMessageBox.warning(self, "Warning", "Please fill in both ID and Password!")
                return

            try:
                if role == "Admin":
                    query = "SELECT Operator_id FROM Transport_operator WHERE Operator_id = ? AND password = ?"
                    check = "Admin"
                elif role == "Driver":
                    query = "SELECT Driver_id FROM Driver WHERE Driver_ID = ? AND Password = ?"
                    check = "Driver"
                else:
                    query = "SELECT Passenger_ID FROM Passenger WHERE Passenger_ID = ? AND Password = ?"
                    check = "Passenger"

                cursor.execute(query, (user_id, password))
                result = cursor.fetchone()

                if result:
                    ## implement admin logic here
                    # if (check == "Admin"):
                    #     admin_id = result[0]  # Fetch the admin ID
                    #     QMessageBox.information(self, "Success", "Login successful!")
                    #     from Admin import AdminSignup
                    #     admin_window = AdminSignup()  # Create an instance of AdminSignup if needed
                    #     admin_window.go_to_dashboard(admin_id=admin_id)  # Call the function directly with the admin ID
                    #     self.close()

                    if (check == "Driver"):
                        driver_id = result[0]
                        QMessageBox.information(self, "Success", "Login successful!")
                        from Driver import DriverDashboard
                        self.driver_window = DriverDashboard(driver_id)  
                        self.driver_window.show()
                        self.close()
                    
                    ## implement passenger logic here
                    # elif (check == "Passenger")
                        
                else:
                    QMessageBox.warning(self, "Error", "Invalid credentials or user does not exist.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to login: {e}")
            # finally:
            #     connection.close()