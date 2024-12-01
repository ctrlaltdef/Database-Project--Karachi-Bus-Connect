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
        self.passgrbtn.clicked.connect(self.go_to_passenger_signup)

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

    def go_to_passenger_signup(self):
        from passengersignup import PassengerSignup  # Assuming you have a PassengerSignup class in passengersignup.py
        self.signup_window = PassengerSignup()
        self.signup_window.show()
        self.close()

    def go_to_passenger_functions(self):
        from passengeroperations import RouteBookingPage
        self.route_management_page = RouteBookingPage(Passenger_id = 9001)
        self.route_management_page.show()
        self.close()  
        self.route_management_page.tableWidget.cellDoubleClicked.connect(self.open_bus_schedule)
        
    def open_bus_schedule(self, row, column):
        # Get the selected route ID from the table
        route_id = self.route_management_page.table.item(row, 0).text()
        from busschedule import BusSchedulePage 
        self.bus_schedule_page = BusSchedulePage(route_id)
        self.bus_schedule_page.show()
        self.route_management_page.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    homepage = HomePage()
    homepage.show()
    sys.exit(app.exec())
