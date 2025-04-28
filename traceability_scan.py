from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout
from ui import Ui_Dialog
import re
import datetime
import comtypes.client as ct
import mysql.connector
# from sqlalchemy import create_engine, text

class MyDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        with mysql.connector.connect(
            host= '', #host name/ip address
            user= '', #user name
            password= '', #password
            database= '' #database name
        ) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT prefix FROM partdetails WHERE station_name = 'V248FCSP' AND sequence = 1")
            self.prefix1 = cursor.fetchone()[0]

            cursor.execute("SELECT prefix FROM partdetails WHERE station_name = 'V248FCSP' AND sequence = 2")
            self.prefix2 = cursor.fetchone()[0]

        self.counter = 0
        self.ui.Input.returnPressed.connect(self.print1)
        self.ui.errorLabel = QLabel(self)  # Create an error label
        self.ui.errorLabel.setGeometry(10, 200, 400, 30)  # Adjust the geometry as needed

    def print1(self):
        if self.counter == 0:
            self.ui.label_3.clear()
            self.ui.label_5.clear()
            self.ui.p_part_3.clear()
            self.ui.label_6.clear()
            self.ui.label_6.setStyleSheet('background-color: none')

            self.wip = self.ui.Input.text()
            self.ui.label_3.setText(self.wip)
            self.ui.Input.clear()
            self.duplicatecheck(self.wip)

        elif self.counter == 1:
            self.part1 = self.ui.Input.text()
            self.ui.label_5.setText(self.part1)
            self.duplicatecheck(self.part1)
            self.prefixcheck(self.part1)

        elif self.counter == 2:
            self.part2 = self.ui.Input.text()
            self.ui.p_part_3.setText(self.part2)
            self.duplicatecheck(self.part2)
            self.prefixcheck(self.part2)

    def prefixcheck(self, item):
        if self.counter == 1:
            if self.ui.label_3.text()[0:7] == item[0:7] and re.search(self.prefix1,item):
                self.ui.Input.clear()
                self.counter += 1
            else:
                self.ui.label_6.setText('Prefix Error')
                self.ui.label_6.setStyleSheet('background-color: orange')
                self.ui.Input.clear()
                self.counter = 0

        elif self.counter == 2:
            if self.ui.label_3.text()[8:15] == item[0:7] and re.search(self.prefix2,item):
                self.ui.Input.clear()
                self.counter = 0
                self.insert_cfsp()
            else:
                self.ui.label_6.setText('Prefix Error')
                self.ui.label_6.setStyleSheet('background-color: orange')
                self.ui.Input.clear()
                self.counter = 0
        
    def duplicatecheck(self, item):
        try:
            with mysql.connector.connect(
                    host= '', #host name/ip address
                    user= '', #user name
                    password= '', #password
                    database= '' #database name
                ) as conn:
                cursor = conn.cursor()
                if self.counter == 0:
                    cursor.execute(f"SELECT serial_number FROM station WHERE serial_number = '{item}'")
                    result = cursor.fetchone()
                    if result == None:
                        self.counter += 1
                    else:
                        self.ui.label_6.setText('WIP already paired')
                        self.ui.label_6.setStyleSheet('background-color: orange')
                        self.ui.Input.clear()
                        self.counter = 0
                elif self.counter == 1:
                    cursor.execute(f"SELECT part1 FROM station WHERE part1 = '{item}'")
                    result = cursor.fetchone()
                    if result == None:
                        pass
                    else:
                        self.ui.label_6.setText('Part Used')
                        self.ui.label_6.setStyleSheet('background-color: orange')
                        self.ui.Input.clear()
                        self.counter = 0

                elif self.counter == 2:
                    cursor.execute(f"SELECT part2 FROM station WHERE part2 = '{item}'")
                    result = cursor.fetchone()
                    if result == None:
                        pass
                    else:
                        self.ui.label_6.setText('Part Used')
                        self.ui.label_6.setStyleSheet('background-color: orange')
                        self.ui.Input.clear()
                        self.counter = 0
        except Exception as e:
            print(e)

    def insert_cfsp(self):
        try:
            with mysql.connector.connect(
                host= '', #host name/ip address
                user= '', #user name
                password= '', #password
                database= '' #database name
            ) as conn:
                cursor = conn.cursor()

                query = f"""INSERT INTO `mes_x248f`.`menu_e_fcsp` 
                (`serial_number`, `part1`, `part2`, `timestamp`, `status`, `station_code`, `station_name`, `attempt_no`) VALUES 
                ('{self.wip}', '{self.part1}', '{self.part2}', '{datetime.datetime.now()}', '0', '0001', 'scan1', '1')"""

                cursor.execute(query)
                self.ui.label_6.setStyleSheet('background-color: rgb(69,255,0)')
                self.ui.label_6.setText('PASS')
                cursor.close()
                conn.commit()

        except mysql.connector.Error as err:
            self.ui.label_6.setText(err)

    def show_message(self, sku, wo):
        self.ui.label_3.setText(sku)
        self.ui.label_5.setText(wo)
        self.ui.Input.clear()
        self.ui.errorLabel.clear()  # Clear the error message label

def main():
    app = QApplication([])
    
    dialog = MyDialog()
    dialog.show()
    app.exec_()

if __name__ == "__main__":
    main()
