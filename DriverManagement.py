from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox, QAbstractItemView, QApplication
from PyQt6.uic import loadUi
from utils import database_connection
import sys

class DriverManagementPage(QMainWindow):
    def __init__(self, admin_id, parent=None):
        super(DriverManagementPage, self).__init__(parent)
        self.admin_id = admin_id
        loadUi("drivermanagement.ui", self)
        print("UI Loaded Successfully")

        self.driverstable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.driverstable.cellClicked.connect(self.populate_update_fields)
        self.createdriverbtn.clicked.connect(self.create_driver)
        self.updatedriverbtn.clicked.connect(self.update_driver)
        self.deletebtn.clicked.connect(self.delete_driver)
        self.dashboardbtn.clicked.connect(self.go_to_dashboard) 

        self.load_drivers()
        self.load_station_combobox()
        self.load_account_status_combobox()
    
    def load_station_combobox(self):
        connection = database_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT Station_id, Station_name FROM Station_area")
            self.cstationcombobox.clear()
            self.ustationidcombobox.clear()
            for row in cursor.fetchall():
                self.cstationcombobox.addItem(row[1], row[0])  
                self.ustationidcombobox.addItem(str(row[0]), row[0])
        except Exception as e:
            self.show_error_message(f"Failed to load stations: {e}")
        finally:
            connection.close()

    def load_account_status_combobox(self):
        self.caccstatuscombobox.clear()
        self.uaccstatuscombobox.clear()
        self.caccstatuscombobox.addItem("Active")
        self.caccstatuscombobox.addItem("Inactive")
        self.uaccstatuscombobox.addItem("Active")
        self.uaccstatuscombobox.addItem("Inactive")

    def load_drivers(self):
        self.driverstable.setRowCount(0)
        self.driverstable.setColumnCount(7)  
        self.driverstable.setHorizontalHeaderLabels(["Driver ID", "Name", "CNIC", "Phone Number", "Password", "Account Status", "Station ID"])
        connection = database_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT * FROM Driver")
            rows = cursor.fetchall()
            self.driverstable.setRowCount(len(rows))
            for row_index, row_data in enumerate(rows):
                for col_index, cell_data in enumerate(row_data):
                    self.driverstable.setItem(row_index, col_index, QTableWidgetItem(str(cell_data)))
        except Exception as e:
            self.show_error_message(f"Failed to load driver data: {e}")
        finally:
            connection.close()

    def create_driver(self):
        name = self.cnamelineEdit.text()
        cnic = self.cCniclineEdit.text()
        phone = self.cphonelineEdit.text()
        password = self.cpasswordlineedit.text()
        account_status = self.caccstatuscombobox.currentText()
        station_id = self.cstationcombobox.currentData()

        if not name or not cnic or not phone or not password or not account_status or not station_id:
            self.show_error_message("Please fill all fields.")
            return

        connection = database_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                INSERT INTO Driver (NAME, CNIC, phone, password, Account_status, Station_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, cnic, phone, password, account_status, station_id))
            connection.commit()
            self.show_info_message("Driver created successfully.")
            self.load_drivers()
        except Exception as e:
            connection.rollback()
            self.show_error_message(f"Error creating driver: {e}")
        finally:
            connection.close()

    def populate_update_fields(self, row):
        driver_id = self.driverstable.item(row, 0).text()
        driver_name = self.driverstable.item(row, 1).text()
        driver_cnic = self.driverstable.item(row, 2).text()
        driver_phone = self.driverstable.item(row, 3).text()
        driver_account_status = self.driverstable.item(row, 5).text()
        station_id = self.driverstable.item(row, 6).text()

        self.udriveridlineedit.setText(driver_id)
        self.unamelineEdit.setText(driver_name)
        self.uCniclineEdit.setText(driver_cnic)
        self.uphonelineEdit.setText(driver_phone)

        if driver_account_status == "Active":
            self.uaccstatuscombobox.setCurrentText("Active")
        elif driver_account_status == "Inactive":
            self.uaccstatuscombobox.setCurrentText("Inactive")

        index = self.ustationidcombobox.findData(station_id)
        if index != -1:
            self.ustationidcombobox.setCurrentIndex(index)

    def update_driver(self):
        driver_id = self.udriveridlineedit.text()
        name = self.unamelineEdit.text()
        cnic = self.uCniclineEdit.text()
        phone = self.uphonelineEdit.text()
        account_status = self.uaccstatuscombobox.currentText()
        station_id = self.ustationidcombobox.currentData()

        if not driver_id or not name or not cnic or not phone or not account_status or not station_id:
            self.show_error_message("Please fill all fields.")
            return

        connection = database_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                UPDATE Driver
                SET NAME = ?, CNIC = ?, phone = ?, Account_status = ?, Station_id = ?
                WHERE Driver_id = ?
            """, (name, cnic, phone, account_status, station_id, driver_id))
            connection.commit()
            self.show_info_message(f"Driver ID {driver_id} updated successfully.")
            self.load_drivers()
        except Exception as e:
            connection.rollback()
            self.show_error_message(f"Error updating driver: {e}")
        finally:
            connection.close()

    def delete_driver(self):
        selected_row = self.driverstable.currentRow()
        if selected_row == -1:
            self.show_error_message("Please select a driver to delete.")
            return

        driver_id = self.driverstable.item(selected_row, 0).text()

        connection = database_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("DELETE FROM Bus_Driver WHERE Driver_id = ?", (driver_id,))
            cursor.execute("DELETE FROM Driver WHERE Driver_id = ?", (driver_id,))
            connection.commit()
            self.show_info_message(f"Driver ID {driver_id} deleted successfully.")
            self.load_drivers()
        except Exception as e:
            connection.rollback()
            self.show_error_message(f"Error deleting driver: {e}")
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
    window = DriverManagementPage(admin_id=12345)
    window.show()
    sys.exit(app.exec())
