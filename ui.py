import sys
import os
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QMessageBox, QTableWidget, QTableWidgetItem, QScrollArea, QApplication, QWidget, QDialog, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QFormLayout, QDateEdit
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
import json
import billGenerator
from PIL.ImageQt import ImageQt


cwd = os.getcwd()
TEMPLATES = os.path.join(cwd, 'Templates')
# Get the templates
invoice_dir = os.path.join(TEMPLATES, 'TAX INVOICE.png')
duplicate_dir = os.path.join(TEMPLATES, 'DUPLICATE TAX INVOICE.png')
triplicate_dir = os.path.join(TEMPLATES, 'TRIPLICATE TAX INVOICE.png')


label_style = "QLabel { font-weight: bold; color: #06124c; }"
button_style = '''
            QPushButton {
                background-color: #06124c;
                border-style: none;
                border-radius: 20px;
                padding: 10px;
                color: white;
                font: bold 14px;
            }
            QPushButton:hover {
                background-color: #c20101;
                color: white;
            }
            QPushButton:pressed {
                background-color: #e6ecf0;
                color: #06124c;
            }
        '''
calendar_style = """
            QDateEdit {
                border: 1px solid #06124c;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
                color: #06124c;
                font-weight: bold;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: 1px solid #06124c;
            }
            QDateEdit::down-arrow {
                image: url(Static/Logo/calendar.png);
                width: 30px;
                height: 15px;
            }
        """

class BillViewWindow(QDialog):
    def __init__(self, data):
        super().__init__()
        self.bill_data = data
        self.initUI()
    
    def initUI(self):
        self.invoice = billGenerator.generate_bill(self.bill_data, invoice_dir)
        # Convert the PIL Image to QImage
        qim = ImageQt(self.invoice)
        pix = QPixmap.fromImage(qim)
        pix = pix.scaled(600, 600, Qt.KeepAspectRatio)
        # Create a QLabel to display the QPixmap
        label = QLabel(self)
        label.setPixmap(pix)

        # Create a vertical layout and add the QLabel to it
        layout = QVBoxLayout()
        layout.addWidget(label)

        cancel_btn = QPushButton('Cancel')
        save_btn = QPushButton('Save')

        hor_layout = QHBoxLayout()

        hor_layout.addWidget(cancel_btn)
        hor_layout.addStretch(1)  # Add stretchable space
        hor_layout.addWidget(save_btn)

        layout.addLayout(hor_layout)

        cancel_btn.clicked.connect(self.close)
        save_btn.clicked.connect(self.save)

        # Set the layout for the window
        self.setLayout(layout)

        # Set window properties
        self.setWindowTitle('Invoice')
        self.setGeometry(10, 10, 400, 400)  # Set window size (x, y, width, height)
        self.exec_()

    def save(self):
        # Save the invoice
        if not self.bill_data.get('flag',None):
            query = QSqlQuery()
            query.prepare(''' INSERT INTO Bill 
                        (invoice_no, date, e_way_no, party_name, address, 
                        state, gst_no, hsn_code, particulars, oth_amt, 
                        taxable_value, cgst, sgst, igst, grand_total) 
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''')
            query.bindValue(0, self.bill_data['invoice_no'])
            query.bindValue(1, self.bill_data['date'])
            query.bindValue(2, self.bill_data['e_way_no'])
            query.bindValue(3, self.bill_data['party_details']['name'])
            query.bindValue(4, self.bill_data['party_details']['street_address'])
            query.bindValue(5, self.bill_data['party_details']['state'])
            query.bindValue(6, self.bill_data['party_details']['gst_no'])
            query.bindValue(7, self.bill_data['hsn_code'])
            query.bindValue(8, json.dumps(self.bill_data['items']))
            query.bindValue(9, self.bill_data['others_amt'])
            query.bindValue(10, self.bill_data['taxable_value'])
            query.bindValue(11, self.bill_data['cgst'])
            query.bindValue(12, self.bill_data['sgst'])
            query.bindValue(13, self.bill_data['igst'])
            query.bindValue(14, self.bill_data['grand_total'])
            if not query.exec_():
                print(query.lastError().text())
                QMessageBox.warning(self, "Database Error", "Failed to insert bill data into the database!")
                return
        else:
            query = QSqlQuery()
            query.prepare('''   UPDATE Bill
                                SET date = ?, e_way_no = ?, party_name = ?, address = ?,
                                state = ?, gst_no = ?, hsn_code = ?, particulars = ?, oth_amt = ?,
                                taxable_value = ?, cgst = ?, sgst = ?, igst = ?, grand_total = ?
                                WHERE invoice_no = ?; ''')
            
            query.bindValue(0, self.bill_data['date'])
            query.bindValue(1, self.bill_data['e_way_no'])
            query.bindValue(2, self.bill_data['party_details']['name'])
            query.bindValue(3, self.bill_data['party_details']['street_address'])
            query.bindValue(4, self.bill_data['party_details']['state'])
            query.bindValue(5, self.bill_data['party_details']['gst_no'])
            query.bindValue(6, self.bill_data['hsn_code'])
            query.bindValue(7, json.dumps(self.bill_data['items']))
            query.bindValue(8, self.bill_data['others_amt'])
            query.bindValue(9, self.bill_data['taxable_value'])
            query.bindValue(10, self.bill_data['cgst'])
            query.bindValue(11, self.bill_data['sgst'])
            query.bindValue(12, self.bill_data['igst'])
            query.bindValue(13, self.bill_data['grand_total'])
            query.bindValue(14, self.bill_data['invoice_no'])

            if not query.exec_():
                print(query.lastError().text())
                QMessageBox.warning(self, "Database Error", "Failed to update bill data into the database!")
                return
            
            # Delete current bills in the directory
            for file in os.listdir('Bills/' + self.bill_data['invoice_no']):
                os.remove(os.path.join('Bills/' + self.bill_data['invoice_no'], file))
            
            os.rmdir('Bills/' + self.bill_data['invoice_no'])

        self.dup_invoice = billGenerator.generate_bill(self.bill_data, duplicate_dir)
        self.tri_invoice = billGenerator.generate_bill(self.bill_data, triplicate_dir)

        os.mkdir('Bills/' + self.bill_data['invoice_no'])
        path = 'Bills/' + self.bill_data['invoice_no'] + '/'
        self.invoice.save(os.path.join(path,'invoice.png'))
        self.dup_invoice.save(os.path.join(path,'duplicate.png'))
        self.tri_invoice.save(os.path.join(path,'triplicate.png'))
        self.close()

class BillConfirmationWindow(QDialog):
    def __init__(self, bill_data):
        super().__init__()

        self.initUI(bill_data)

    def initUI(self, bill_data):
        self.bill_data = bill_data
        layout = QVBoxLayout()

        table_widget = QTableWidget()
        table_widget.setColumnCount(4)
        table_widget.setHorizontalHeaderLabels(['Particulars', 'Quantity', 'Rate', 'Amount'])

        for row, item in enumerate(bill_data['items']):
            table_widget.insertRow(row)
            table_widget.setItem(row, 0, QTableWidgetItem(item[0]))
            table_widget.setItem(row, 1, QTableWidgetItem(item[1]))
            table_widget.setItem(row, 2, QTableWidgetItem(item[2]))
            table_widget.setItem(row, 3, QTableWidgetItem(item[3]))

            for col in range(table_widget.columnCount()):
                table_widget.item(row, col).setTextAlignment(Qt.AlignCenter)

        table_widget.setFixedWidth(652)

        # Set the width of each column
        table_widget.setColumnWidth(0, 400)  # Particulars column width
        table_widget.setColumnWidth(1, 150)  # Quantity column width
        table_widget.setColumnWidth(2, 100)  # Rate column width

        table_widget.resizeRowsToContents()

        layout.addWidget(table_widget)

        oth_amt_label = QLabel("Other Amount: " + bill_data['others_amt'])
        layout.addWidget(oth_amt_label)
        taxable_amt_label = QLabel("Taxable Amount: " + bill_data['taxable_value'])
        layout.addWidget(taxable_amt_label)
        cgst_label = QLabel("CGST: " + bill_data['cgst'])
        layout.addWidget(cgst_label)
        sgst_label = QLabel("SGST: " + bill_data['sgst'])
        layout.addWidget(sgst_label)
        igst_label = QLabel("IGST: " + bill_data['igst'])
        layout.addWidget(igst_label)
        total_label = QLabel("Total: " + bill_data['grand_total'])
        layout.addWidget(total_label)

        hor_layout = QHBoxLayout()

        cancel_btn = QPushButton('Cancel')
        submit_btn = QPushButton('Confirm')

        hor_layout.addWidget(cancel_btn)
        hor_layout.addStretch(1)  # Add stretchable space
        hor_layout.addWidget(submit_btn)

        layout.addLayout(hor_layout)

        cancel_btn.clicked.connect(self.close)
        submit_btn.clicked.connect(self.submit)

        self.setLayout(layout)

        self.setWindowTitle('Invoice Confirmation')
        self.setGeometry(10, 10, 500, 500)
        self.exec_()

    def submit(self):
        # Create a connection to the SQLite database
        if not create_connection():
            QMessageBox.warning(self, "Database Error", "Database connection failed!")
            return
        if not self.bill_data.get('flag',None):
            query = QSqlQuery()
            query.prepare('''SELECT invoice_no FROM Bill
                                ORDER BY invoice_no DESC
                                LIMIT 1; ''')
            if not query.exec_():
                print(query.lastError().text())
                QMessageBox.warning(self, "Database Error", "Failed to fetch invoice number from the database!")
                return

            if query.next():
                self.bill_data['invoice_no'] = str(int(query.value(0)) + 1)
            else:
                self.bill_data['invoice_no'] = '1'
        

        billview = BillViewWindow(self.bill_data)
        billview.setStyleSheet(self.styleSheet())
        self.close()

class BillEditWindow(QDialog):
    def __init__(self, bill_data):
        super().__init__()
        self.bill_data = bill_data
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        hor_layout = QHBoxLayout()
        hor_layout.setAlignment(Qt.AlignLeft)
        # Create form fields
        self.fields = {
            "Date:": [QDateEdit(),self.bill_data['date']],
            "E-Way No:": [QLineEdit(),self.bill_data['e_way_no']],
            "Name:": [QLineEdit(),self.bill_data['party_details']['name']],
            "Address:": [QTextEdit(),self.bill_data['party_details']['street_address']],
            "State:": [QLineEdit(),self.bill_data['party_details']['state']],
            "GST No:": [QLineEdit(),self.bill_data['party_details']['gst_no']],
            "HSN / SAC Code:": [QLineEdit(),self.bill_data['hsn_code']],
            "Particulars:": [QTableWidget(),self.bill_data['items']],
            "Plus Button": QPushButton("+"),
            "Minus Button": QPushButton("-"),
            "Other Amount:": [QLineEdit(),self.bill_data['others_amt']],
            "CGST:": [QLineEdit(),str((float(self.bill_data['cgst'])/float(self.bill_data['taxable_value']))*100)],
            "SGST:": [QLineEdit(),str((float(self.bill_data['sgst'])/float(self.bill_data['taxable_value']))*100)],
            "IGST:": [QLineEdit(),str((float(self.bill_data['igst'])/float(self.bill_data['taxable_value']))*100)],
        }
        # Add QLabel and QLineEdit widgets to the layout
        for label, widget in self.fields.items():
            if label == "Plus Button" or label == "Minus Button":
                hor_layout.addWidget(widget)
                layout.addLayout(hor_layout)
                continue
            elif label == "Particulars:":
                self.fields['Particulars:'][0].setColumnCount(3)  # Set the number of columns
                self.fields['Particulars:'][0].setHorizontalHeaderLabels(["Particulars", "Quantity", "Rate"])  # Set column headers
                for row, item in enumerate(widget[1]):
                    widget[0].insertRow(row)
                    widget[0].setItem(row, 0, QTableWidgetItem(item[0]))
                    widget[0].setItem(row, 1, QTableWidgetItem(item[1]))
                    widget[0].setItem(row, 2, QTableWidgetItem(item[2]))

                widget[0].setFixedWidth(652)
                widget[0].setFixedHeight(200)
                # Set the width of each column
                widget[0].setColumnWidth(0, 300)
                widget[0].setColumnWidth(1, 150)
                widget[0].setColumnWidth(2, 100)
                widget[0].setColumnWidth(3, 100)
                widget[0].resizeRowsToContents()
                label_widget = QLabel(label)
                label_widget.setStyleSheet(label_style)
                layout.addWidget(label_widget)
                layout.addWidget(widget[0])
            elif label == "Date:":
                label_widget = QLabel(label)
                label_widget.setStyleSheet(label_style)
                layout.addWidget(label_widget)
                layout.addWidget(widget[0])
                widget[0].setCalendarPopup(True)
                widget[0].setDisplayFormat("dd-MM-yyyy")
                widget[0].setDate(QDate.fromString(widget[1], "dd-MM-yyyy"))
                widget[0].setStyleSheet(calendar_style)
            elif label == "Address:":
                label_widget = QLabel(label)
                label_widget.setStyleSheet(label_style)
                layout.addWidget(label_widget)
                layout.addWidget(widget[0])
                widget[0].setFixedHeight(100)
                widget[0].setFixedWidth(300)
                widget[0].setLineWrapMode(QTextEdit.WidgetWidth)
                widget[0].setText(widget[1])
            else:
                label_widget = QLabel(label)
                label_widget.setStyleSheet(label_style)
                layout.addWidget(label_widget)
                layout.addWidget(widget[0])
                widget[0].setFixedWidth(300)
                widget[0].setText(str(widget[1]))
                widget[0].setStyleSheet("QLineEdit { color: #06124c; }")
                widget[0].setAlignment(Qt.AlignCenter)
        
        # Plus Minus Button styling
        self.fields['Plus Button'].setStyleSheet(button_style)
        self.fields['Plus Button'].setFixedWidth(50)
        self.fields['Minus Button'].setStyleSheet(button_style)
        self.fields['Minus Button'].setFixedWidth(50)

        # Connect the plus button's and mins button's clicked signal to the custom function
        self.fields['Plus Button'].clicked.connect(self.addRow)
        self.fields['Minus Button'].clicked.connect(self.removeRow)

         # Create a submit button
        submit_button = QPushButton("Submit")
        submit_button.setStyleSheet(button_style)
        layout.addWidget(submit_button)
        submit_button.clicked.connect(self.submit)

        # Create a cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet(button_style)
        layout.addWidget(cancel_button)
        cancel_button.clicked.connect(self.close)

        content_widget = QWidget()
        content_widget.setLayout(layout)

        # Create a QScrollArea and set the content widget
        scroll_area = QScrollArea()
        scroll_area.setWidget(content_widget)

        # Set the fixed height for the scroll area
        scroll_area.setFixedHeight(400)
        scroll_area.setFixedWidth(750)
        scroll_area.setWidgetResizable(True)

        # Set the scroll area as the main layout of the window
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(scroll_area)     
        self.setWindowTitle('Edit Invoice')
        self.setGeometry(10, 10, 300, 100)  # Set window size (x, y, width, height)
        self.exec_()
    
    def addRow(self):
        row_count = self.fields['Particulars:'][0].rowCount()
        self.fields['Particulars:'][0].insertRow(row_count)
    
    def removeRow(self):
        row_count = self.fields['Particulars:'][0].rowCount()
        if row_count > 0:
            self.fields['Particulars:'][0].removeRow(row_count - 1)
    
    def submit(self):
        #Check if all the fields are filled
        for label, widget in self.fields.items():
            if label == "Plus Button" or label == "Minus Button":
                continue
            elif label == "Address:": 
                if widget[0].toPlainText() == "":
                    QMessageBox.warning(self, "Empty Field", "Please fill the Address")
                    return
            elif label == "Particulars:":
                row_count = self.fields['Particulars:'][0].rowCount()
                if row_count == 0:
                    QMessageBox.warning(self, "Empty Field", "Please fill the Particulars")
                    return
            elif label!="E-Way No:" and widget[0].text() == "":
                QMessageBox.warning(self, "Empty Field", f"Please fill the {label[:-1]}")
                return

        date = self.fields['Date:'][0].date().toString("dd-MM-yyyy")
        e_way_no = self.fields['E-Way No:'][0].text()
        name = self.fields['Name:'][0].text()
        address = self.fields['Address:'][0].toPlainText()
        state = self.fields['State:'][0].text()
        gst_no = self.fields['GST No:'][0].text()
        hsn_code = self.fields['HSN / SAC Code:'][0].text()
        oth_amt = self.fields['Other Amount:'][0].text()
        cgst = self.fields['CGST:'][0].text()
        sgst = self.fields['SGST:'][0].text()
        igst = self.fields['IGST:'][0].text()

        row_count = self.fields['Particulars:'][0].rowCount()
        column_count = self.fields['Particulars:'][0].columnCount()
        particulars = []
        total_amount = 0
        for row in range(row_count):
            row_data = []
            for column in range(column_count):
                item = self.fields['Particulars:'][0].item(row, column)
                if item is not None:
                    row_data.append(item.text())
                else:
                    QMessageBox.warning(self, "Empty Field", "Please fill all the details in Particulars")
                    return
            row_data.append(str(float(row_data[1]) * float(row_data[2])))
            total_amount += float(row_data[3])
            particulars.append(row_data)
        
        taxable_amt = total_amount + float(oth_amt)
        cgst = float(cgst)/100 * taxable_amt
        sgst = float(sgst)/100 * taxable_amt
        igst = float(igst)/100 * taxable_amt
        grand_total = taxable_amt + cgst + sgst + igst

        # Create a dictionary to store the data
        bill_data = {
            "invoice_no": self.bill_data['invoice_no'],
            "date": date,
            "e_way_no": e_way_no,
            "party_details": {
                "name": name,
                "street_address": address,
                "state": state,
                "state_code": stateCode(state),
                "gst_no": gst_no,
            },
            "items": particulars,
            "hsn_code": hsn_code,
            "others_amt": oth_amt,
            "taxable_value": str(taxable_amt),
            "cgst": str(cgst),
            "sgst": str(sgst),
            "igst": str(igst),
            "grand_total": str(grand_total),
            "flag": "EDIT"
        }
        bill_confirm = BillConfirmationWindow(bill_data)
        bill_confirm.setStyleSheet(self.styleSheet())
        self.close()


class BillEditFormWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.initUI()
    
    def initUI(self):
        layout =  QVBoxLayout()
        label_widget = QLabel("Invoice No:")
        label_widget.setStyleSheet(label_style)
        layout.addWidget(label_widget)
        invoice_no = QLineEdit()
        layout.addWidget(invoice_no)
        submit_button = QPushButton("Submit")
        submit_button.setStyleSheet(button_style)
        layout.addWidget(submit_button)
        submit_button.clicked.connect(lambda: self.submit(invoice_no.text()))
    
        self.setLayout(layout)
        self.setWindowTitle('Invoice Edit Form')
        self.setGeometry(10, 10, 300, 100)  # Set window size (x, y, width, height)
        self.exec_()
    
    def submit(self, invoice_no):
        # Create a connection to the SQLite database
        if not create_connection():
            QMessageBox.warning(self, "Database Error", "Database connection failed!")
            return
        query = QSqlQuery()
        query.prepare('''   SELECT * FROM Bill
                            WHERE invoice_no = ?; ''')
        query.bindValue(0, invoice_no)

        if not query.exec_():
            print(query.lastError().text())
            QMessageBox.warning(self, "Database Error", "Failed to fetch invoice number from the database!")
            return
        if not query.next():
            QMessageBox.warning(self, "Database Error", "Invoice number not found!")
            return
        
        self.bill_data = {
            "invoice_no": str(query.value(0)),
            "e_way_no": query.value(1),
            "party_details": {
                "name": query.value(2),
                "street_address": query.value(3),
                "state": query.value(4),
                "gst_no": query.value(5),
            },
            "items": json.loads(query.value(6)),
            "hsn_code": query.value(7),
            "others_amt": query.value(8),
            "taxable_value": query.value(9),
            "cgst": query.value(10),
            "sgst": query.value(11),
            "igst": query.value(12),
            "grand_total": query.value(13),
            "date": query.value(14),
        }
        bill_edit = BillEditWindow(self.bill_data)
        bill_edit.setStyleSheet(self.styleSheet())
        self.close()




class FormWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Create form fields
        self.fields = {
            "Date:": QDateEdit(),
            "E-Way No:": QLineEdit(),
            "Name:": QLineEdit(),
            "Address:": QTextEdit(),
            "State:": QLineEdit(),
            "GST No:": QLineEdit(),
            "HSN / SAC Code:": QLineEdit(),
            "Particulars:": QTableWidget(),
            "Plus Button": QPushButton("+"),
            "Minus Button": QPushButton("-"),
            "Other Amount:": QLineEdit(),
            "CGST:": QLineEdit(),
            "SGST:": QLineEdit(),
            "IGST:": QLineEdit(),
        }
        layout =  QVBoxLayout()
        hor_layout = QHBoxLayout()
        hor_layout.setAlignment(Qt.AlignLeft)
        # Add QLabel and QLineEdit widgets to the layout
        for label, widget in self.fields.items():
            if label == "Plus Button" or label == "Minus Button":
                hor_layout.addWidget(widget)
                layout.addLayout(hor_layout)
                continue
            label_widget = QLabel(label)
            label_widget.setStyleSheet(label_style)
            layout.addWidget(label_widget)
            layout.addWidget(widget)
            widget.setFixedWidth(300) 

        self.fields['Address:'].setFixedHeight(100)
        self.fields['Address:'].setFixedWidth(300)
        self.fields['Address:'].setLineWrapMode(QTextEdit.WidgetWidth)
        # Add table for particulars
        self.fields['Particulars:'].setColumnCount(3)  # Set the number of columns
        self.fields['Particulars:'].setHorizontalHeaderLabels(["Particulars", "Quantity", "Rate"])  # Set column headers
        self.fields['Particulars:'].setFixedWidth(652)
        self.fields['Particulars:'].setFixedHeight(200)

        # Set the width of each column
        self.fields['Particulars:'].setColumnWidth(0, 400)  # Particulars column width
        self.fields['Particulars:'].setColumnWidth(1, 150)  # Quantity column width
        self.fields['Particulars:'].setColumnWidth(2, 100)  # Rate column width

        # Plus Minus Button styling
        self.fields['Plus Button'].setStyleSheet(button_style)
        self.fields['Plus Button'].setFixedWidth(50)
        self.fields['Minus Button'].setStyleSheet(button_style)
        self.fields['Minus Button'].setFixedWidth(50)

        # Connect the plus button's and mins button's clicked signal to the custom function
        self.fields['Plus Button'].clicked.connect(self.addRow)
        self.fields['Minus Button'].clicked.connect(self.removeRow)


        # Create a QDateEdit widget for the calendar field
        self.fields['Date:'].setCalendarPopup(True)
        self.fields['Date:'].setDisplayFormat("dd-MM-yyyy")  # Set the display format
        self.fields['Date:'].setDate(QDate.currentDate())  # Set the minimum date as today

        # Apply custom styles to the calendar field
        self.fields['Date:'].setStyleSheet(calendar_style)


        # Create a submit button
        submit_button = QPushButton("Submit")
        submit_button.setStyleSheet(button_style)
        layout.addWidget(submit_button)
        submit_button.clicked.connect(self.submit)

        # Create a QWidget to hold the layout
        content_widget = QWidget()
        content_widget.setLayout(layout)

        # Create a QScrollArea and set the content widget
        scroll_area = QScrollArea()
        scroll_area.setWidget(content_widget)

        # Set the fixed height for the scroll area
        scroll_area.setFixedHeight(400)
        scroll_area.setFixedWidth(750)
        scroll_area.setWidgetResizable(True)

        # Set the scroll area as the main layout of the window
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(scroll_area)     
        
        # Set window properties
        self.setGeometry(10, 10, 300, 200)  # Set window size (x, y, width, height)
        self.setWindowTitle('Invoice Form')
        self.exec_()

    def submit(self):
        #Check if all the fields are filled
        for label, widget in self.fields.items():
            if label == "Plus Button" or label == "Minus Button":
                continue
            elif label == "Address:": 
                if widget.toPlainText() == "":
                    QMessageBox.warning(self, "Empty Field", "Please fill the Address")
                    return
            elif label == "Particulars:":
                row_count = self.fields['Particulars:'].rowCount()
                if row_count == 0:
                    QMessageBox.warning(self, "Empty Field", "Please fill the Particulars")
                    return
            elif label!="E-Way No:" and widget.text() == "":
                QMessageBox.warning(self, "Empty Field", f"Please fill the {label[:-1]}")
                return

        date = self.fields['Date:'].date().toString("dd-MM-yyyy")
        e_way_no = self.fields['E-Way No:'].text()
        name = self.fields['Name:'].text()
        address = self.fields['Address:'].toPlainText()
        state = self.fields['State:'].text()
        gst_no = self.fields['GST No:'].text()
        hsn_code = self.fields['HSN / SAC Code:'].text()
        oth_amt = self.fields['Other Amount:'].text()
        cgst = self.fields['CGST:'].text()
        sgst = self.fields['SGST:'].text()
        igst = self.fields['IGST:'].text()

        row_count = self.fields['Particulars:'].rowCount()
        column_count = self.fields['Particulars:'].columnCount()
        particulars = []
        total_amount = 0
        for row in range(row_count):
            row_data = []
            for column in range(column_count):
                item = self.fields['Particulars:'].item(row, column)
                if item is not None:
                    row_data.append(item.text())
                else:
                    QMessageBox.warning(self, "Empty Field", "Please fill all the details in Particulars")
                    return
            row_data.append(str(float(row_data[1]) * float(row_data[2])))
            total_amount += float(row_data[3])
            particulars.append(row_data)
        
        taxable_amt = total_amount + float(oth_amt)
        cgst = float(cgst)/100 * taxable_amt
        sgst = float(sgst)/100 * taxable_amt
        igst = float(igst)/100 * taxable_amt
        grand_total = taxable_amt + cgst + sgst + igst

        # Create a dictionary to store the data
        self.bill_data = {
            "date": date,
            "e_way_no": e_way_no,
            "party_details": {
                "name": name,
                "street_address": address,
                "state": state,
                "state_code": stateCode(state),
                "gst_no": gst_no,
            },
            "items": particulars,
            "hsn_code": hsn_code,
            "others_amt": oth_amt,
            "taxable_value": str(taxable_amt),
            "cgst": str(cgst),
            "sgst": str(sgst),
            "igst": str(igst),
            "grand_total": str(grand_total),
        }
        bill_confirm = BillConfirmationWindow(self.bill_data)
        bill_confirm.setStyleSheet(self.styleSheet())
        self.close()

    def addRow(self):
        row_count = self.fields['Particulars:'].rowCount()
        self.fields['Particulars:'].insertRow(row_count)
    
    def removeRow(self):
        row_count = self.fields['Particulars:'].rowCount()
        if row_count > 0:
            self.fields['Particulars:'].removeRow(row_count - 1)
    
    



class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Create three buttons
        self.button1 = QPushButton('Generate New Bill', self)
        self.button2 = QPushButton('Edit Bill', self)

        # Apply custom style to the buttons
        self.button1.setStyleSheet(button_style)
        self.button2.setStyleSheet(button_style)

        # Create a vertical layout for buttons
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.button1)
        button_layout.addWidget(self.button2)

        # Create a label for the image
        loc = 'Static/Logo/dp_full.jpeg'  # Specify the path to the image
        image_label = QLabel(self)
        image_label.setPixmap(QPixmap(loc))
        image_label.setAlignment(Qt.AlignCenter)  # Align the image to the center

        # Create a form layout for the form
        self.form_layout = QFormLayout()

        # Create a horizontal layout and add buttons and the image label to it
        layout = QHBoxLayout()
        layout.addLayout(button_layout)
        layout.addWidget(image_label)

        # Set the layout for the window
        self.setLayout(layout)

        # Set window properties
        self.setWindowTitle('Diapro Impex Billing Software')
        self.setGeometry(10, 10, 700, 200)  # Set window size (x, y, width, height)
        self.show()

        # Connect button1's clicked signal to show the form
        self.button1.clicked.connect(self.openFormWindow)
        self.button2.clicked.connect(self.openBillEditFormWindow)
    
    def openFormWindow(self):
        form_window = FormWindow()
        form_window.setStyleSheet(self.styleSheet())
    
    def openBillEditFormWindow(self):
        bill_edit_form_window = BillEditFormWindow()
        bill_edit_form_window.setStyleSheet(self.styleSheet())
    
def create_connection():
    # Create a connection to the SQLite database
    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('db.sqlite3')  # Replace with the actual path to your SQLite database file

    if not db.open():
        return False
    
    return True

def stateCode(state):
    stateToCode = {
        "andhra pradesh": "AP",
        "arunachal pradesh": "AR",
        "assam": "AS",
        "bihar": "BR",
        "chhattisgarh": "CT",
        "goa": "GA",
        "gujarat": "GJ",
        "haryana": "HR",
        "himachal pradesh": "HP",
        "jammu and kashmir": "JK",
        "jharkhand": "JH",
        "karnataka": "KA",
        "kerala": "KL",
        "madhya pradesh": "MP",
        "maharashtra": "MH",
        "manipur": "MN",
        "meghalaya": "ML",
        "mizoram": "MZ",
        "nagaland": "NL",
        "odisha": "OR",
        "punjab": "PB",
        "rajasthan": "RJ",
        "sikkim": "SK",
        "tamil nadu": "TN",
        "telangana": "TG",
        "tripura": "TR",
        "uttarakhand": "UT",
        "uttar pradesh": "UP",
        "west bengal": "WB",
        "andaman and nicobar islands": "AN",
        "chandigarh": "CH",
        "dadra and nagar haveli": "DN",
        "daman and diu": "DD",
        "delhi": "DL",
        "lakshadweep": "LD",
        "puducherry": "PY",
    }
    return stateToCode[state.lower()]

if __name__ == '__main__':
    app = QApplication(sys.argv)
    icon = QIcon('Static/Logo/dp.jpeg')  # Replace 'path_to_icon_file.png' with the actual path to your icon file
    app.setWindowIcon(icon)
    window = Window()
    window.setStyleSheet('background-color: #F7F7F7;')  # Set the background color to #F7F7F7
    sys.exit(app.exec_())



