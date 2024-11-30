from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox, QAbstractItemView, QApplication
from PyQt6.uic import loadUi
from utils import database_connection  
import sys

class BusRouteDriverPage(QMainWindow):
    def __init__(self, admin_id, parent=None):
        super(BusRouteDriverPage, self).__init__(parent)
        self.admin_id = admin_id
        loadUi("AssignBusRouteDriver.ui", self)
        print("UI Loaded Successfully")
        
        self.tabelViewAssign.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.busroutetable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.busdrivertable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        self.assignbtnbusdriver.clicked.connect(self.assign_bus_driver)  
        self.deletebtnbusdriver.clicked.connect(self.delete_bus_driver)  
        self.assignbtnbusroute.clicked.connect(self.assign_bus_route)  
        self.deletebtnbusroute.clicked.connect(self.delete_bus_route) 
        self.dashboardbtn.clicked.connect(self.go_to_dashboard)

        self.load_comboboxes()
        self.load_bus_route_table()
        self.load_bus_driver_table()
        self.load_assignments()

    def load_comboboxes(self):
        """ Load Bus IDs, Driver IDs, and Route IDs into their respective comboboxes """
        connection = database_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT Bus_id FROM Bus")
            self.buscomboBox.clear()
            for row in cursor.fetchall():
                self.buscomboBox.addItem(str(row[0]))

            
            cursor.execute("SELECT Bus_id FROM Bus")
            self.buscomboBox_2.clear()
            for row in cursor.fetchall():
                self.buscomboBox_2.addItem(str(row[0]))
            
            cursor.execute("SELECT Driver_id FROM Driver")
            self.drivercomboBox.clear()
            for row in cursor.fetchall():
                self.drivercomboBox.addItem(str(row[0]))

            cursor.execute("SELECT Route_id FROM Route")
            self.routecomboBox.clear()
            for row in cursor.fetchall():
                self.routecomboBox.addItem(str(row[0]))
        except Exception as e:
            self.show_error_message(f"Failed to load data: {e}")
        finally:
            connection.close()

    def load_assignments(self):
        """ Load the joined table (Bus, Route, Driver) into the assignments table """
        self.tabelViewAssign.setRowCount(0)  
        self.tabelViewAssign.setColumnCount(3)  
        self.tabelViewAssign.setHorizontalHeaderLabels(["Bus ID", "Route ID", "Driver ID"])
        connection = database_connection()
        cursor = connection.cursor()

        try:
            query = """
                SELECT BD.Bus_id, BR.Route_id, BD.Driver_id
                FROM Bus_Driver BD
                JOIN Bus_Route BR ON BD.Bus_id = BR.Bus_id
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            self.tabelViewAssign.setRowCount(len(rows))
            for row_index, row_data in enumerate(rows):
                for col_index, cell_data in enumerate(row_data):
                    self.tabelViewAssign.setItem(row_index, col_index, QTableWidgetItem(str(cell_data)))
        except Exception as e:
            self.show_error_message(f"Failed to load assignments: {e}")
        finally:
            connection.close()
    
    def load_bus_route_table(self):
        """ Load the Bus_Route table into the busroutetable """
        self.busroutetable.setRowCount(0)  
        self.busroutetable.setColumnCount(2)  
        self.busroutetable.setHorizontalHeaderLabels(["Bus ID", "Route ID"])
        connection = database_connection()
        cursor = connection.cursor()

        try:
            query = "SELECT * FROM Bus_Route"
            cursor.execute(query)
            rows = cursor.fetchall()

            self.busroutetable.setRowCount(len(rows))
            for row_index, row_data in enumerate(rows):
                for col_index, cell_data in enumerate(row_data):
                    self.busroutetable.setItem(row_index, col_index, QTableWidgetItem(str(cell_data)))
        except Exception as e:
            self.show_error_message(f"Failed to load bus route data: {e}")
        finally:
            connection.close()

    def load_bus_driver_table(self):
        """ Load the Bus_Driver table into the busdrivertable """
        self.busdrivertable.setRowCount(0)  
        self.busdrivertable.setColumnCount(2)  
        self.busdrivertable.setHorizontalHeaderLabels(["Bus ID", "Driver ID"])
        connection = database_connection()
        cursor = connection.cursor()

        try:
            query = "SELECT * FROM Bus_Driver"
            cursor.execute(query)
            rows = cursor.fetchall()

            self.busdrivertable.setRowCount(len(rows))
            for row_index, row_data in enumerate(rows):
                for col_index, cell_data in enumerate(row_data):
                    self.busdrivertable.setItem(row_index, col_index, QTableWidgetItem(str(cell_data)))
        except Exception as e:
            self.show_error_message(f"Failed to load bus driver data: {e}")
        finally:
            connection.close()

    def assign_bus_route(self):
        """ Assign a bus to a route """
        bus_id = self.buscomboBox_2.currentText()
        route_id = self.routecomboBox.currentText()

        if not bus_id or not route_id:
            self.show_error_message("Please select a Bus ID and Route ID.")
            return

        connection = database_connection()
        cursor = connection.cursor()

        try:
            query = "SELECT COUNT(*) FROM Bus_Route WHERE Bus_ID = ? AND Route_ID = ?"
            cursor.execute(query, (bus_id, route_id))
            exists = cursor.fetchone()[0] > 0

            if exists:
                self.show_error_message(f"Bus ID {bus_id} is already assigned to Route ID {route_id}.")
                return

            query_insert = "INSERT INTO Bus_Route (Bus_ID, Route_ID) VALUES (?, ?)"
            cursor.execute(query_insert, (bus_id, route_id))

            connection.commit()
            self.show_info_message(f"Bus ID {bus_id} and Route ID {route_id} assigned successfully.")
            self.load_bus_route_table() 
            self.load_assignments()  
        except Exception as e:
            connection.rollback()
            self.show_error_message(f"Error assigning bus to route: {e}")
        finally:
            connection.close()

    def assign_bus_driver(self):
        """ Assign a bus to a driver """
        bus_id = self.buscomboBox.currentText()
        driver_id = self.drivercomboBox.currentText()

        if not bus_id or not driver_id:
            self.show_error_message("Please select a Bus ID and Driver ID.")
            return

        connection = database_connection()
        cursor = connection.cursor()

        try:
            query = "SELECT COUNT(*) FROM Bus_Driver WHERE Bus_ID = ? AND Driver_ID = ?"
            cursor.execute(query, (bus_id, driver_id))
            exists = cursor.fetchone()[0] > 0

            if exists:
                self.show_error_message(f"Bus ID {bus_id} is already assigned to Driver ID {driver_id}.")
                return

            query_insert = "INSERT INTO Bus_Driver (Bus_ID, Driver_ID) VALUES (?, ?)"
            cursor.execute(query_insert, (bus_id, driver_id))

            connection.commit()
            self.show_info_message(f"Bus ID {bus_id} and Driver ID {driver_id} assigned successfully.")
            self.load_bus_driver_table()  
            self.load_assignments() 
        except Exception as e:
            connection.rollback()
            self.show_error_message(f"Error assigning bus to driver: {e}")
        finally:
            connection.close()

    def delete_bus_route(self):
        """ Delete the selected Bus-Route assignment """
        selected_row = self.busroutetable.currentRow()
        if selected_row == -1:
            self.show_error_message("Please select a bus-route combination to delete.")
            return

        bus_id = self.busroutetable.item(selected_row, 0).text()
        route_id = self.busroutetable.item(selected_row, 1).text()

        connection = database_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("DELETE FROM Bus_Route WHERE Bus_ID = ? AND Route_ID = ?", (bus_id, route_id))
            connection.commit()
            self.show_info_message(f"Bus ID {bus_id} and Route ID {route_id} deleted successfully.")
            self.load_bus_route_table() 
            self.load_assignments()  

        except Exception as e:
            connection.rollback()
            self.show_error_message(f"Error deleting bus-route assignment: {e}")
        finally:
            connection.close()

    def delete_bus_driver(self):
        """ Delete the selected Bus-Driver assignment """
        selected_row = self.busdrivertable.currentRow()
        if selected_row == -1:
            self.show_error_message("Please select a bus-driver combination to delete.")
            return

        bus_id = self.busdrivertable.item(selected_row, 0).text()
        driver_id = self.busdrivertable.item(selected_row, 1).text()

        connection = database_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("DELETE FROM Bus_Driver WHERE Bus_ID = ? AND Driver_ID = ?", (bus_id, driver_id))
            connection.commit()
            self.show_info_message(f"Bus ID {bus_id} and Driver ID {driver_id} deleted successfully.")
            self.load_bus_driver_table() 
            self.load_assignments()  

        except Exception as e:
            connection.rollback()
            self.show_error_message(f"Error deleting bus-driver assignment: {e}")
        finally:
            connection.close()

    def go_to_dashboard(self):
        from Admin import AdminDashboard
        """ Navigate back to the Admin Dashboard """
        self.dashboard_window = AdminDashboard(admin_id=self.admin_id)
        self.dashboard_window.show()
        self.close()

    def show_error_message(self, message):
        """ Show an error message box """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.exec()

    def show_info_message(self, message):
        """ Show an info message box """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(message)
        msg.setWindowTitle("Info")
        msg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BusRouteDriverPage(admin_id=12345) 
    window.show()
    sys.exit(app.exec())
