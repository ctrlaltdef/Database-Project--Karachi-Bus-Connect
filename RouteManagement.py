from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox, QApplication, QAbstractItemView
from PyQt6.uic import loadUi
from utils import database_connection  
import sys

class RouteManagementPage(QMainWindow):
    def __init__(self, admin_id, parent=None):
        super(RouteManagementPage, self).__init__(parent)
        self.admin_id = admin_id
        loadUi("RouteManagement.ui", self)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.createRoutebtn.clicked.connect(self.create_route)
        self.updateRoutebtn.clicked.connect(self.update_route)
        self.deletebtn.clicked.connect(self.delete_route)
        self.dashboardbtn.clicked.connect(self.go_to_dashboard)
        self.table.cellClicked.connect(self.populate_update_fields)
        self.uStatusComboBox.addItems(["Active", "Inactive"])
        self.cStatuscombobox.addItems(["Active", "Inactive"])
        self.load_routes()

    def load_routes(self):
        self.table.setRowCount(0)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Route ID", "Starting Point", "Destination", "Start Time", "End Time", "Status"])
        connection = database_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM Route")
            rows = cursor.fetchall()
            for row_index, row_data in enumerate(rows):
                self.table.insertRow(row_index)
                for col_index, cell_data in enumerate(row_data):
                    item = QTableWidgetItem(str(cell_data))
                    self.table.setItem(row_index, col_index, item)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load routes: {e}")
        finally:
            connection.close()

    def populate_update_fields(self, row):
        route_id = self.table.item(row, 0).text()
        start_point = self.table.item(row, 1).text()
        destination = self.table.item(row, 2).text()
        start_time = self.table.item(row, 3).text()
        end_time = self.table.item(row, 4).text()
        status = self.table.item(row, 5).text()
        self.urouteIDlineEdit.setText(route_id)
        self.ustartPtlineEdit.setText(start_point)
        self.uDestinationlineEdit.setText(destination)
        self.uStart_timelineEdit.setText(start_time)
        self.uEnd_timelineEdit.setText(end_time)
        self.uStatusComboBox.setCurrentText(status)

    def create_route(self):
        starting_point = self.cstartingPtlinededit.text()
        destination = self.cdestinationLineEdit.text()
        start_time = self.cStartTimelineedit.text()
        end_time = self.cend_timelineedit.text()
        status = self.cStatuscombobox.currentText()
        if not starting_point or not destination or not start_time or not end_time:
            self.show_error_message("Please fill all fields.")
            return
        connection = database_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO Route (Starting_point, Destination, start_time, end_time, status)
                VALUES (?, ?, ?, ?, ?)
            """, (starting_point, destination, start_time, end_time, status))
            cursor.execute("SELECT * FROM Route")
            route = cursor.fetchone()
            if route:
                connection.commit()
                self.load_routes()
                self.show_info_message("Route created successfully.")
        except Exception as e:
            connection.rollback()
            self.show_error_message(f"Error creating route: {e}")
        finally:
            connection.close()

    def update_route(self):
        route_id = self.urouteIDlineEdit.text().strip()
        start_point = self.ustartPtlineEdit.text().strip()
        destination = self.uDestinationlineEdit.text().strip()
        start_time = self.uStart_timelineEdit.text().strip()
        end_time = self.uEnd_timelineEdit.text().strip()
        status = self.uStatusComboBox.currentText().strip()
        if not all([route_id, start_point, destination, start_time, end_time, status]):
            self.show_error_message("Please fill all fields.")
            return
        if not self.validate_time_format(start_time) or not self.validate_time_format(end_time):
            self.show_error_message("Invalid time format. Use HH:MM:SS.")
            return
        connection = database_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE Route
                SET Starting_point = ?, Destination = ?, start_time = ?, end_time = ?, status = ?
                WHERE Route_id = ?
            """, (start_point, destination, start_time, end_time, status, route_id))
            if cursor.rowcount == 0:
                self.show_error_message("No route found with the provided Route ID.")
            else:
                connection.commit()
                self.show_info_message("Route updated successfully.")
                self.load_routes()
        except Exception as e:
            connection.rollback()
            self.show_error_message(f"Error updating route: {e}")
        finally:
            connection.close()

    def validate_time_format(self, time_str):
        import re
        time_pattern = r"^(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d$"
        return re.match(time_pattern, time_str) is not None

    def delete_route(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            self.show_error_message("Please select a route to delete.")
            return
        route_id = self.table.item(selected_row, 0).text()
        connection = database_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM Operator_Route WHERE Route_id = ?", (route_id,))
            cursor.execute("DELETE FROM Route_Stop WHERE Route_id = ?", (route_id,))
            cursor.execute("DELETE FROM Bus_Route WHERE Route_id = ?", (route_id,))
            cursor.execute("DELETE FROM Ticket_Booking WHERE Route_id = ?", (route_id,))
            cursor.execute("DELETE FROM Passenger_route WHERE Route_id = ?", (route_id,))
            cursor.execute("DELETE FROM Route WHERE Route_id = ?", (route_id,))
            connection.commit()
            self.load_routes()
            self.show_info_message("Route deleted successfully.")
        except Exception as e:
            connection.rollback()
            self.show_error_message(f"Error deleting route: {e}")
        finally:
            connection.close()

    def go_to_dashboard(self):
        from Admin import AdminDashboard
        self.dashboard_window = AdminDashboard(admin_id=self.admin_id)
        self.dashboard_window.show()
        self.close()

    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.exec()

    def show_info_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(message)
        msg.setWindowTitle("Info")
        msg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RouteManagementPage(admin_id=12345)
    window.show()
    sys.exit(app.exec())
