from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox, QApplication
from PyQt6.uic import loadUi
from utils import database_connection
import sys


class BusManagementPage(QMainWindow):
    def __init__(self, admin_id, parent=None):
        super(BusManagementPage, self).__init__(parent)
        self.admin_id = admin_id
        loadUi("BusManagement.ui", self)

        self.createbtn.clicked.connect(self.create_bus)
        self.updatebtn.clicked.connect(self.update_bus)
        self.deletebtn.clicked.connect(self.delete_bus)
        self.dashboardbtn.clicked.connect(self.go_to_dashboard)

        self.bustable.cellClicked.connect(self.populate_update_fields)

        self.load_station_comboboxes()
        self.load_status_comboboxes()
        self.load_all_buses()

    def create_bus(self):
        bus_model = self.cbusmodellineEdit.text()
        maintenance = self.cmaintainenecelineEdit.text()
        capacity = self.ccapacitylineEdit.text()
        status = self.cstatuscombo.currentText()
        station_id = self.cstationcombobox.currentData()

        if not bus_model or not maintenance or not capacity or not status or station_id is None:
            self.show_error_message("Please fill all fields.")
            return

        connection = database_connection()
        cursor = connection.cursor()

        try:
            query = """
                INSERT INTO Bus (bus_model, maintenance, capacity, status, station_id)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(query, (bus_model, maintenance, capacity, status, station_id))
            connection.commit()

            self.show_info_message("Bus created successfully.")
            self.load_all_buses()
        except Exception as e:
            connection.rollback()
            self.show_error_message(f"Error creating bus: {e}")
        finally:
            connection.close()

    def load_all_buses(self):
        self.bustable.setRowCount(0)
        self.bustable.setColumnCount(6)
        self.bustable.setHorizontalHeaderLabels(["Bus ID", "Bus Model", "Maintenance", "Capacity", "Status", "Station ID"])
        connection = database_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT * FROM Bus")
            rows = cursor.fetchall()

            self.bustable.setRowCount(len(rows))
            for row_index, row_data in enumerate(rows):
                for col_index, cell_data in enumerate(row_data):
                    self.bustable.setItem(row_index, col_index, QTableWidgetItem(str(cell_data)))
        except Exception as e:
            self.show_error_message(f"Failed to load buses: {e}")
        finally:
            connection.close()

    def populate_update_fields(self, row):
        bus_id = self.bustable.item(row, 0).text()
        bus_model = self.bustable.item(row, 1).text()
        maintenance = self.bustable.item(row, 2).text()
        capacity = self.bustable.item(row, 3).text()
        status = self.bustable.item(row, 4).text()
        station_id = self.bustable.item(row, 5).text()

        self.busidlineedit.setText(bus_id)
        self.ubusmodellineEdit.setText(bus_model)
        self.umaintainenecelineEdit.setText(maintenance)
        self.ucapacitylineEdit.setText(capacity)

        self.ustatuscombo.setCurrentText(status)

        index = self.ustationcombobox.findData(int(station_id))
        if index != -1:
            self.ustationcombobox.setCurrentIndex(index)

    def update_bus(self):
        bus_id = self.busidlineedit.text()
        bus_model = self.ubusmodellineEdit.text()
        maintenance = self.umaintainenecelineEdit.text()
        capacity = self.ucapacitylineEdit.text()
        status = self.ustatuscombo.currentText()
        station_id = self.ustationcombobox.currentData()

        if not bus_id or not bus_model or not maintenance or not capacity or not status or station_id is None:
            self.show_error_message("Please fill all fields.")
            return

        connection = database_connection()
        cursor = connection.cursor()

        try:
            query = """
                UPDATE Bus
                SET bus_model = ?, maintenance = ?, capacity = ?, status = ?, station_id = ?
                WHERE bus_id = ?
            """
            cursor.execute(query, (bus_model, maintenance, capacity, status, station_id, bus_id))
            connection.commit()

            self.show_info_message("Bus updated successfully.")
            self.load_all_buses()
        except Exception as e:
            connection.rollback()
            self.show_error_message(f"Error updating bus: {e}")
        finally:
            connection.close()

    def delete_bus(self):
        selected_row = self.bustable.currentRow()
        if selected_row == -1:
            self.show_error_message("Please select a bus to delete.")
            return

        bus_id = self.bustable.item(selected_row, 0).text()

        connection = database_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("DELETE FROM Bus_Driver WHERE Bus_id = ?", (bus_id,))
            cursor.execute("DELETE FROM Bus_Route WHERE Bus_id = ?", (bus_id,))
            cursor.execute("DELETE FROM Bus_Stop WHERE Bus_id = ?", (bus_id,))
            cursor.execute("DELETE FROM Bus WHERE Bus_id = ?", (bus_id,))
            connection.commit()

            self.show_info_message(f"Bus with ID {bus_id} deleted successfully.")
            self.load_all_buses()
        except Exception as e:
            connection.rollback()
            self.show_error_message(f"Error deleting bus: {e}")
        finally:
            connection.close()

    def load_station_comboboxes(self):
        connection = database_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT Station_id, Station_name FROM Station_area")
            
            self.cstationcombobox.clear()
            self.ustationcombobox.clear()

            for row in cursor.fetchall():
                self.cstationcombobox.addItem(row[1], row[0])
                self.ustationcombobox.addItem(str(row[0]), row[0])

        except Exception as e:
            self.show_error_message(f"Failed to load stations: {e}")
        finally:
            connection.close()

    def load_status_comboboxes(self):
        self.cstatuscombo.clear()
        self.ustatuscombo.clear()

        statuses = ["Active", "Inactive"]
        self.cstatuscombo.addItems(statuses)
        self.ustatuscombo.addItems(statuses)
    
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
    window = BusManagementPage(admin_id=12345)
    window.show()
    sys.exit(app.exec())

