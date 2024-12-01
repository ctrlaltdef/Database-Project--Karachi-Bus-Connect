from PyQt6.QtWidgets import (
    QMainWindow, QTableWidgetItem, QMessageBox, QApplication
)
from PyQt6.uic import loadUi
from utils import database_connection

class BusSchedulePage(QMainWindow):
    def __init__(self, route_id, parent=None):
        super(BusSchedulePage, self).__init__(parent)
        self.route_id = route_id  # The route_id passed from the RouteBookingPage
        loadUi("passenger2.ui", self)  
        
        # Set up the table widget to display bus schedule
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["Bus ID", "Bus Model", "Capacity", "Status", "Driver"])

        # Load bus schedule data based on the selected route
        self.load_bus_schedule()

    def load_bus_schedule(self):
        """Fetch and display bus schedule for the selected route."""
        connection = database_connection()
        cursor = connection.cursor()
        try:
            # SQL query to fetch bus schedule data based on the route_id
            query = """
                SELECT 
                    Bus.Bus_id,
                    Bus.Bus_model,
                    Bus.capacity,
                    Bus.status,
                    Driver.Name AS Driver_Name
                FROM 
                    Bus_Route
                JOIN Bus ON Bus_Route.Bus_id = Bus.Bus_id
                JOIN Bus_Driver ON Bus.Bus_id = Bus_Driver.Bus_id
                JOIN Driver ON Bus_Driver.Driver_id = Driver.Driver_id
                WHERE Bus_Route.Route_id = ?
            """
            cursor.execute(query, (self.route_id,))
            buses = cursor.fetchall()

            # If no buses are found for the given route, show a message
            if not buses:
                QMessageBox.information(self, "No Bus Available", "No buses are available for the selected route.")
            
            # Populate the table with bus schedules
            for row_index, row_data in enumerate(buses):
                self.tableWidget.insertRow(row_index)
                for col_index, cell_data in enumerate(row_data):
                    self.tableWidget.setItem(row_index, col_index, QTableWidgetItem(str(cell_data)))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load bus schedules: {e}")
        finally:
            connection.close()

if __name__ == "__main__":
    app = QApplication([])
    route_id = 17627  # Example route_id, this would come from RouteBookingPage
    window = BusSchedulePage(route_id)
    window.show()
    app.exec()
