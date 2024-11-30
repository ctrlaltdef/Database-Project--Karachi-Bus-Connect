from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox, QApplication, QAbstractItemView
from PyQt6.uic import loadUi
from utils import database_connection
import sys

class StopManagementPage(QMainWindow):
    def __init__(self, admin_id, parent=None):
        super(StopManagementPage, self).__init__(parent)
        self.admin_id = admin_id
        loadUi("StopManagement.ui", self)
        print("UI Loaded Successfully")

        self.stopsRoutetable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.stopsTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.createStopbtn.clicked.connect(self.create_stop)
        self.updateStopbtn.clicked.connect(self.update_stop)
        self.deletestopbtn.clicked.connect(self.delete_stop)
        self.Assignbtn.clicked.connect(self.add_stop_to_route)
        self.deletebtn.clicked.connect(self.delete_route_stop)
        self.dashboardBtn.clicked.connect(self.go_to_dashboard)

        self.load_stops()
        self.load_routes_and_stops_dropdown()
        self.load_routes_stops_table()

        self.stopsTable.cellClicked.connect(self.populate_update_fields)

    def load_stops(self):
        self.stopsTable.setRowCount(0)  
        self.stopsTable.setColumnCount(4)  
        self.stopsTable.setHorizontalHeaderLabels(["Stop ID", "Estimated Reaching Time", "Stop Name", "Location"])
        connection = database_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM Stop")
            rows = cursor.fetchall()
            self.stopsTable.setRowCount(len(rows))
            for row_index, row_data in enumerate(rows):
                for col_index, cell_data in enumerate(row_data):
                    item = QTableWidgetItem(str(cell_data))
                    self.stopsTable.setItem(row_index, col_index, item)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load stops: {e}")
        finally:
            connection.close()

    def load_routes_stops_table(self):
        self.stopsRoutetable.setRowCount(0)  
        self.stopsRoutetable.setColumnCount(2)  
        self.stopsRoutetable.setHorizontalHeaderLabels(["Stop ID", "Route ID"])
        connection = database_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("select * from Route_stop  order by route_id, stop_id")
            rows = cursor.fetchall()
            self.stopsRoutetable.setRowCount(len(rows))
            for row_index, row_data in enumerate(rows):
                for col_index, cell_data in enumerate(row_data):
                    item = QTableWidgetItem(str(cell_data))
                    self.stopsRoutetable.setItem(row_index, col_index, item)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load stops: {e}")
        finally:
            connection.close()

    def load_routes_and_stops_dropdown(self):
        connection = database_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT Route_id FROM Route")
            routes = cursor.fetchall()
            self.RouteIDcomboBox.addItems([str(route[0]) for route in routes])

            cursor.execute("SELECT Stop_id FROM Stop")
            stops = cursor.fetchall()
            self.StopIDcomboBox.addItems([str(stop[0]) for stop in stops])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load routes/stops: {e}")
        finally:
            connection.close()

    def populate_update_fields(self, row):
        stop_id = self.stopsTable.item(row, 0).text()
        stop_name = self.stopsTable.item(row, 2).text()
        estimated_time = self.stopsTable.item(row, 1).text()
        location = self.stopsTable.item(row, 3).text()

        self.stopidLinedit.setText(stop_id)
        self.ustop_namelineEdit.setText(stop_name)
        self.uestimatedlineEdit.setText(estimated_time)
        self.uLoclineEdit.setText(location)

    def create_stop(self):
        stop_name = self.cstop_namelineEdit.text()
        estimated_time = self.cestimatedlineEdit.text()
        location = self.cLoclineEdit.text()

        if not stop_name or not estimated_time or not location:
            self.show_error_message("Please fill all fields.")
            return

        connection = database_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO Stop (Estimated_Reaching_Time, Stop_name, Location)
                VALUES (?, ?, ?)
            """, (estimated_time, stop_name, location))
            connection.commit()
            self.load_stops()
            self.show_info_message("Stop created successfully.")
            self.cstop_namelineEdit.clear()
            self.cestimatedlineEdit.clear()
            self.cLoclineEdit.clear()
        except Exception as e:
            connection.rollback()
            self.show_error_message(f"Error creating stop: {e}")
        finally:
            connection.close()

    def update_stop(self):
        stop_id = self.stopidLinedit.text()
        stop_name = self.ustop_namelineEdit.text()
        estimated_time = self.uestimatedlineEdit.text()
        location = self.uLoclineEdit.text()

        if not stop_id or not stop_name or not estimated_time or not location:
            self.show_error_message("Please fill all fields.")
            return

        connection = database_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE Stop
                SET Stop_name = ?, Estimated_Reaching_Time = ?, Location = ?
                WHERE Stop_id = ?
            """, (stop_name, estimated_time, location, stop_id))
            connection.commit()
            self.load_stops()
            self.show_info_message("Stop updated successfully.")
        except Exception as e:
            connection.rollback()
            self.show_error_message(f"Error updating stop: {e}")
        finally:
            connection.close()

    def delete_stop(self):
        selected_row = self.stopsTable.currentRow()
        if selected_row == -1:
            self.show_error_message("Please select a stop to delete.")
            return

        stop_id = self.stopsTable.item(selected_row, 0).text()

        connection = database_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM Route_Stop WHERE Stop_id = ?", (stop_id,))
            cursor.execute("DELETE FROM Bus_Stop WHERE Stop_id = ?", (stop_id,))
            cursor.execute("DELETE FROM Stop WHERE Stop_id = ?", (stop_id,))
            connection.commit()
            self.load_stops()
            self.show_info_message("Stop deleted successfully.")
        except Exception as e:
            connection.rollback()
            self.show_error_message(f"Error deleting stop: {e}")
        finally:
            connection.close()

    def add_stop_to_route(self):
        route_id = self.RouteIDcomboBox.currentText()
        stop_id = self.StopIDcomboBox.currentText()

        connection = database_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO Route_Stop (Route_id, Stop_id)
                VALUES (?, ?)
            """, (route_id, stop_id))
            connection.commit()
            self.load_routes_stops_table()
            self.show_info_message("Stop added to route successfully.")
        except Exception as e:
            connection.rollback()
            self.show_error_message(f"Error adding stop to route: {e}")
        finally:
            connection.close()

    def delete_route_stop(self):
        selected_row = self.stopsRoutetable.currentRow()
        if selected_row == -1:
            self.show_error_message("Please select a stop-route assignment to delete.")
            return

        stop_id = self.stopsRoutetable.item(selected_row, 0).text()
        route_id = self.stopsRoutetable.item(selected_row, 1).text()

        connection = database_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                DELETE FROM Route_Stop
                WHERE Stop_id = ? AND Route_id = ?
            """, (stop_id, route_id))
            connection.commit()
            self.load_routes_stops_table()
            self.show_info_message("Stop-route assignment deleted successfully.")
        except Exception as e:
            connection.rollback()
            self.show_error_message(f"Error deleting stop-route assignment: {e}")
        finally:
            connection.close()

    def go_to_dashboard(self):
        from Admin import AdminDashboard
        self.dashboard_window = AdminDashboard(admin_id=self.admin_id)
        self.dashboard_window.show()
        self.close()

    def show_error_message(self, message):
        QMessageBox.critical(self, "Error", message)

    def show_info_message(self, message):
        QMessageBox.information(self, "Info", message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StopManagementPage(admin_id=12345)
    window.show()
    sys.exit(app.exec())
