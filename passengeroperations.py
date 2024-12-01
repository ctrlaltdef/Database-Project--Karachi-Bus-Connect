from PyQt6.QtWidgets import (
    QMainWindow, QTableWidgetItem, QMessageBox, QApplication, QAbstractItemView
)
from PyQt6.uic import loadUi
from utils import database_connection

class RouteBookingPage(QMainWindow):
    def __init__(self, Passenger_id, parent=None):
        super().__init__(parent)
        self.Passenger_id = Passenger_id
        loadUi("passenger1.ui", self)

        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(
            ["Route ID", "Starting Point", "Destination", "Start Time", "End Time", "Status"]
        )

        self.comboBox.currentIndexChanged.connect(self.filter_routes)
        self.comboBox_2.currentIndexChanged.connect(self.filter_routes)
        self.pushButton.clicked.connect(self.show_bus_schedule)

        self.load_dropdowns()
        self.load_routes()

    def load_dropdowns(self):
        connection = database_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT DISTINCT Starting_point FROM Route")
            self.comboBox.addItems([row[0] for row in cursor.fetchall()])

            cursor.execute("SELECT DISTINCT Destination FROM Route")
            self.comboBox_2.addItems([row[0] for row in cursor.fetchall()])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load dropdowns: {e}")
        finally:
            connection.close()

    def load_routes(self, start_point=None, destination=None):
        self.tableWidget.setRowCount(0)
        connection = database_connection()
        cursor = connection.cursor()
        try:
            query = """
                SELECT 
                    Route_id, Starting_point, Destination, Start_time, End_time, Status
                FROM 
                    Route
                WHERE 
                    LOWER(Starting_point) = LOWER(?) 
                    AND LOWER(Destination) = LOWER(?)
            """
            cursor.execute(query, (start_point, destination))
            for row_index, row_data in enumerate(cursor.fetchall()):
                self.tableWidget.insertRow(row_index)
                for col_index, cell_data in enumerate(row_data):
                    self.tableWidget.setItem(row_index, col_index, QTableWidgetItem(str(cell_data)))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load routes: {e}")
        finally:
            connection.close()

    def filter_routes(self):
        start_point = self.comboBox.currentText()
        destination = self.comboBox_2.currentText()
        self.load_routes(start_point, destination)

    def show_bus_schedule(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Warning", "Please select a route to view the bus schedule!")
            return

        route_id = self.tableWidget.item(selected_row, 0).text()
        self.open_bus_schedule(route_id)

    def open_bus_schedule(self, route_id):
        from busschedule import BusSchedulePage
        self.bus_schedule_page = BusSchedulePage(route_id)
        self.bus_schedule_page.show()
        self.close()



