import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.uic import loadUi

class HomePage(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("homepage.ui", self)
        self.adminbtn.clicked.connect(self.go_to_admin_signup)
        self.driverbtn.clicked.connect(self.go_to_driver_functions) 
        self.passgrbtn.clicked.connect(self.go_to_passenger_functions) 

    def go_to_admin_signup(self):
        from Admin import AdminSignup 
        self.admin_window = AdminSignup()
        self.admin_window.show()
        self.close()

    def go_to_driver_functions(self):
        from Driver import DriverSignup
        self.driver_window = DriverSignup()
        self.driver_window.show()
        self.close()

    def go_to_passenger_functions(self):
        pass  

if __name__ == "__main__":
    app = QApplication(sys.argv)
    homepage = HomePage()
    homepage.show()
    sys.exit(app.exec())
