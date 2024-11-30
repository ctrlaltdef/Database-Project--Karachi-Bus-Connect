from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox, QApplication
from PyQt6.uic import loadUi
from utils import database_connection
import sys

class PassengerManagementPage(QMainWindow):
    def __init__(self, admin_id, parent=None):
        super(PassengerManagementPage, self).__init__(parent)
        self.admin_id = admin_id
        loadUi("passengerManagement.ui", self)

        self.createbtn.clicked.connect(self.create_passenger)
        self.updatepassbtn.clicked.connect(self.update_passenger)
        self.deletebtn.clicked.connect(self.delete_passenger)
        self.dashboard.clicked.connect(self.go_to_dashboard)

        self.passtable.cellClicked.connect(self.populate_update_fields)
        self.load_all_passengers()

    def create_passenger(self):
        name = self.cnamelineEdit.text()
        email = self.cemaillineEdit.text()
        phone = self.cphonelineEdit_2.text()
        password = self.cpasslineEdit.text()

        if not name or not email or not phone or not password:
            self.show_error_message("Please fill all fields.")
            return

        connection = database_connection()
        cursor = connection.cursor()

        try:
            query = """
                INSERT INTO Passenger (Name, Email, Phone, Password)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(query, (name, email, phone, password))
            connection.commit()

            self.show_info_message("Passenger created successfully.")
            self.load_all_passengers()
        except Exception as e:
            connection.rollback()
            self.show_error_message(f"Error creating passenger: {e}")
        finally:
            connection.close()

    def load_all_passengers(self):
        self.passtable.setRowCount(0)
        self.passtable.setColumnCount(5)
        self.passtable.setHorizontalHeaderLabels(["Passenger ID", "Name", "Email", "Phone Number", "Password"])
        connection = database_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT * FROM Passenger")
            rows = cursor.fetchall()

            self.passtable.setRowCount(len(rows))
            for row_index, row_data in enumerate(rows):
                for col_index, cell_data in enumerate(row_data):
                    self.passtable.setItem(row_index, col_index, QTableWidgetItem(str(cell_data)))
        except Exception as e:
            self.show_error_message(f"Failed to load passengers: {e}")
        finally:
            connection.close()
    
    def populate_update_fields(self, row):
        passenger_id = self.passtable.item(row, 0).text()
        passenger_name = self.passtable.item(row, 1).text()
        passenger_email = self.passtable.item(row, 2).text()
        passenger_phone = self.passtable.item(row, 3).text()

        self.passidlineedit.setText(passenger_id)
        self.unamelineEdit.setText(passenger_name)
        self.uemaillineEdit.setText(passenger_email)
        self.uphonelineEdit.setText(passenger_phone)

    def update_passenger(self):
        passenger_id = self.passidlineedit.text()
        name = self.unamelineEdit.text()
        email = self.uemaillineEdit.text()
        phone = self.uphonelineEdit.text()

        if not passenger_id or not name or not email or not phone:
            self.show_error_message("Please fill all fields.")
            return

        connection = database_connection()
        cursor = connection.cursor()

        try:
            query = """
                UPDATE Passenger
                SET Name = ?, Email = ?, Phone = ?
                WHERE Passenger_id = ?
            """
            cursor.execute(query, (name, email, phone, passenger_id))
            connection.commit()

            self.show_info_message("Passenger updated successfully.")
            self.load_all_passengers()
        except Exception as e:
            connection.rollback()
            self.show_error_message(f"Error updating passenger: {e}")
        finally:
            connection.close()

    def delete_passenger(self):
        selected_row = self.passtable.currentRow()
        if selected_row == -1:
            self.show_error_message("Please select a passenger to delete.")
            return

        passenger_id = self.passtable.item(selected_row, 0).text()

        connection = database_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("DELETE FROM Passenger_Route WHERE Passenger_id = ?", (passenger_id,))
            cursor.execute("DELETE FROM Ticket_Booking WHERE Passenger_id = ?", (passenger_id,))
            cursor.execute("DELETE FROM Passenger WHERE Passenger_id = ?", (passenger_id,))
            connection.commit()

            self.show_info_message(f"Passenger with ID {passenger_id} deleted successfully.")
            self.load_all_passengers()
        except Exception as e:
            connection.rollback()
            self.show_error_message(f"Error deleting passenger: {e}")
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
    window = PassengerManagementPage(admin_id=12345)
    window.show()
    sys.exit(app.exec())
