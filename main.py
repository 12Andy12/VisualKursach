import sqlite3
import sys
import time
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.openTrainsForm()
        self.currentTrain = "";
        self.currentWagon = "";
        self.absolutSeatNumber = 54;

    def setCurentWagon(self):
        row = self.tableWidget.currentRow()
        if row > -1:  # Если есть выделенная строка/элемент
            self.currentWagon = self.tableWidget.item(row, 0).text()
            self.tableWidget.selectionModel().clearCurrentIndex()
        self.openPassengersForm()

    def openPassengersForm(self):
        uic.loadUi('ThirdForm.ui', self)
        self.btnBack.clicked.connect(self.openWagonsForm)
        self.info.setText("Train № " + self.currentTrain + " Wagon № " + self.currentWagon)
        self.tableWidget.setColumnCount(3)  # Set three columns
        self.tableWidget.setRowCount(0)  # and zero row
        self.tableWidget.setColumnWidth(2, 1)  # Для удаления узкая колонка
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger(0))
        self.tableWidget.setHorizontalHeaderLabels(['Пассажир', 'Номер места', ''])
        self.loadPassengersTable()
        self.btnAdd.clicked.connect(self.openAddPassengerForm)

    def placeIsAccept(self, testPlace):
        connection = sqlite3.connect("train.db")
        cur = connection.cursor()
        cur.execute("SELECT * FROM Passengers WHERE train = ? AND wagon = ?;", (self.currentTrain, self.currentWagon))
        allTable = cur.fetchall()
        isAccept = True
        for i in allTable:
            if(i[1] == str(testPlace)):
                isAccept = False
        return isAccept

    def openAddTrainForm(self):
        uic.loadUi('AddForm.ui', self)
        self.btnCancel.clicked.connect(self.openTrainsForm)
        self.btnAdd.clicked.connect(self.addTrain)

    def openTrainsForm(self):
        uic.loadUi('firstForm.ui', self)

        self.btnAdd.clicked.connect(self.openAddTrainForm)
        self.btnSort.clicked.connect(self.sort)
        self.btnReset.clicked.connect(self.loadTrainsTable)
        self.tableWidget.setColumnCount(5)  # Set three columns
        self.tableWidget.setRowCount(0)  # and one row
        self.tableWidget.setColumnWidth(4, 1)  # Для удаления узкая колонка
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger(0))

        self.loadTrainsTable()

        # Set the table headers
        self.tableWidget.setHorizontalHeaderLabels(['Номер поезда', 'Дата прибытия', 'Дата отбытия', 'Открыть', ''])

    def sort(self):
        self.tableWidget.setRowCount(0)
        connection = sqlite3.connect("train.db")
        cur = connection.cursor()
        curentRow = 0
        for row in cur.execute("SELECT * FROM Trains WHERE dataIn = ? AND dataOut = ?;", (self.sortDateIn.text(), self.sortDateOut.text())):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for i in range(0, 3):
                self.tableWidget.setItem(curentRow, i, QtWidgets.QTableWidgetItem(row[i]))
                btnOpen = QPushButton("open")

                btnClose = QPushButton("X")
                btnClose.setStyleSheet("QPushButton{\n"
                                       "background-color: rgb(255, 0, 0);\n}")
                btnClose.clicked.connect(self.DelTrain)
                btnOpen.clicked.connect(self.setCurentTrain)
                self.tableWidget.setCellWidget(self.tableWidget.rowCount() - 1, 4, btnClose)
                self.tableWidget.setCellWidget(self.tableWidget.rowCount() - 1, 3, btnOpen)
            curentRow += 1

    def addTrain(self):
        ret = QMessageBox.question(self, 'Add', "Are u sure?",
                                   QMessageBox.No | QMessageBox.Yes)
        if ret == QMessageBox.Yes:
            connection = sqlite3.connect("train.db")
            cur = connection.cursor()
            row = [self.trainName.text(), self.dateIn.text(), self.dateOut.text()]
            cur.execute("INSERT INTO Trains VALUES(?, ?, ?);", row)
            connection.commit()
            self.openTrainsForm()

    def addPassenger(self):
        thisSeatNumber = -1;
        for i in range(1, self.absolutSeatNumber):
            if(self.placeIsAccept(i) == True):
                thisSeatNumber = i
                break
        if(thisSeatNumber == -1):
            QMessageBox.about(self, 'Error', "No place")
            return
        ret = QMessageBox.question(self, 'Add', "Are u sure?",
                                   QMessageBox.No | QMessageBox.Yes)
        if ret == QMessageBox.Yes:
            connection = sqlite3.connect("train.db")
            cur = connection.cursor()
            row = [self.passengerName.text(), thisSeatNumber, self.currentWagon, self.currentTrain]
            cur.execute("INSERT INTO Passengers VALUES(?, ?, ?, ?);", row)
            connection.commit()
            self.openPassengersForm()

    def openAddWagonForm(self):
        uic.loadUi('AddWagonForm.ui', self)
        self.trainName.setText("Train - " + self.currentTrain)
        self.wagonName.setText("Wagon - " + self.currentWagon)
        self.btnCancel.clicked.connect(self.openPassengerForm)
        self.btnAdd.clicked.connect(self.addPassenger)

    def openAddPassengerForm(self):
        uic.loadUi('AddPassengerForm.ui', self)
        self.trainName.setText("Train - " + self.currentTrain)
        self.wagonName.setText("Wagon - " + self.currentWagon)
        self.btnCancel.clicked.connect(self.openPassengersForm)
        self.btnAdd.clicked.connect(self.addPassenger)

    def addWagon(self):
        ret = QMessageBox.question(self, 'Add', "Are u sure?",
                                   QMessageBox.No | QMessageBox.Yes)
        if ret == QMessageBox.Yes:
            connection = sqlite3.connect("train.db")
            cur = connection.cursor()
            newRow = [self.currentTrain, self.wagonName.text()]
            cur.execute("INSERT INTO Wagons VALUES(?, ?);", newRow)
            connection.commit()
            self.openWagonsForm()

    def setCurentTrain(self):
        row = self.tableWidget.currentRow()
        if row > -1:  # Если есть выделенная строка/элемент
            self.currentTrain = self.tableWidget.item(row, 0).text()
            self.tableWidget.selectionModel().clearCurrentIndex()
        self.openWagonsForm()

    def openWagonsForm(self):
        uic.loadUi('secondForm.ui', self)
        self.info.setText("Train № " + self.currentTrain)
        self.btnBack.clicked.connect(self.openTrainsForm)
        self.tableWidget.setColumnCount(3)  # Set three columns
        self.tableWidget.setRowCount(0)  # and zero row
        self.tableWidget.setColumnWidth(2, 1)  # Для удаления узкая колонка
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger(0))
        self.tableWidget.setHorizontalHeaderLabels(['Номер вагона', 'Открыть', ''])
        self.loadWagonsTable()
        self.btnAdd.clicked.connect(self.openAddWagonForm)



    def loadTrainsTable(self):
        self.tableWidget.setRowCount(0)
        connection = sqlite3.connect("train.db")
        cur = connection.cursor()
        curentRow = 0
        for row in cur.execute("SELECT * FROM Trains"):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for i in range(0, 3):
                self.tableWidget.setItem(curentRow, i, QtWidgets.QTableWidgetItem(row[i]))
                btnOpen = QPushButton("open")

                btnClose = QPushButton("X")
                btnClose.setStyleSheet("QPushButton{\n"
                                       "background-color: rgb(255, 0, 0);\n}")
                btnClose.clicked.connect(self.DelTrain)
                btnOpen.clicked.connect(self.setCurentTrain)
                self.tableWidget.setCellWidget(self.tableWidget.rowCount() - 1, 4, btnClose)
                self.tableWidget.setCellWidget(self.tableWidget.rowCount() - 1, 3, btnOpen)
            curentRow+=1

    def loadWagonsTable(self):
        self.tableWidget.setRowCount(0)
        connection = sqlite3.connect("train.db")
        cur = connection.cursor()
        curentRow = 0
        for row in cur.execute("SELECT * FROM Wagons WHERE train = ?;", (self.currentTrain, )):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            self.tableWidget.setItem(curentRow, 0, QtWidgets.QTableWidgetItem(row[1]))
            btnOpen = QPushButton("open")
            btnClose = QPushButton("X")
            btnClose.setStyleSheet("QPushButton{\nbackground-color: rgb(255, 0, 0);\n}")
            btnClose.clicked.connect(self.DelWagon)
            btnOpen.clicked.connect(self.setCurentWagon)
            self.tableWidget.setCellWidget(self.tableWidget.rowCount() - 1, 2, btnClose)
            self.tableWidget.setCellWidget(self.tableWidget.rowCount() - 1, 1, btnOpen)
            curentRow += 1

    def loadPassengersTable(self):
        self.tableWidget.setRowCount(0)
        connection = sqlite3.connect("train.db")
        cur = connection.cursor()
        curentRow = 0
        for row in cur.execute("SELECT * FROM Passengers WHERE wagon = ? AND train = ? ", (self.currentWagon, self.currentTrain)):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for i in range(0, 3):
                self.tableWidget.setItem(curentRow, i, QtWidgets.QTableWidgetItem(row[i]))

                btnClose = QPushButton("X")
                btnClose.setStyleSheet("QPushButton{\n"
                                       "background-color: rgb(255, 0, 0);\n}")
                btnClose.clicked.connect(self.DelPassenger)
                self.tableWidget.setCellWidget(self.tableWidget.rowCount() - 1, 2, btnClose)
            curentRow += 1

    def DelTrain(self):
        button = QMessageBox.question(self, "Удаление строки", "Вы уверены?")
        connection = sqlite3.connect("train.db")
        cur = connection.cursor()
        cur.execute("SELECT * FROM Trains;")
        allMain = cur.fetchall()
        if button == QMessageBox.StandardButton.Yes:
            row = self.tableWidget.currentRow()
            delIndex = self.tableWidget.currentRow()
            print(1)
            cur.execute("DELETE FROM Passengers WHERE train = ?",
                        (allMain[delIndex][0], ))
            print(2)
            cur.execute("DELETE FROM Wagons WHERE train = ?",
                        (allMain[delIndex][0], ))
            print(3)
            cur.execute("DELETE FROM Trains WHERE train = ? AND dataIn = ? AND dataOut = ?",
                        (allMain[delIndex][0], allMain[delIndex][1], allMain[delIndex][2]))
            print(4)

            connection.commit()
            print(5)
            if row > -1:  # Если есть выделенная строка/элемент
                self.tableWidget.removeRow(row)
                self.tableWidget.selectionModel().clearCurrentIndex()

    def DelWagon(self):
        button = QMessageBox.question(self, "Удаление строки", "Вы уверены?")
        connection = sqlite3.connect("train.db")
        cur = connection.cursor()
        cur.execute("SELECT * FROM Wagons;")
        allMain = cur.fetchall()
        if button == QMessageBox.StandardButton.Yes:
            row = self.tableWidget.currentRow()
            delIndex = self.tableWidget.currentRow()
            cur.execute("DELETE FROM Wagons WHERE wagon = ? AND train = ?",
                        (allMain[delIndex][0], self.currentTrain))
            cur.execute("DELETE FROM Passengers WHERE wagon = ? AND train = ?",
                        (allMain[delIndex][0], self.currentTrain))
            connection.commit()
            if row > -1:  # Если есть выделенная строка/элемент
                self.tableWidget.removeRow(row)
                self.tableWidget.selectionModel().clearCurrentIndex()

    def DelPassenger(self):
        button = QMessageBox.question(self, "Удаление строки", "Вы уверены?")
        connection = sqlite3.connect("train.db")
        cur = connection.cursor()
        cur.execute("SELECT * FROM Passengers;")
        allMain = cur.fetchall()
        if button == QMessageBox.StandardButton.Yes:
            row = self.tableWidget.currentRow()
            delIndex = self.tableWidget.currentRow()
            cur.execute("DELETE FROM Passengers WHERE passenger = ? AND seatingPosition = ?",
                        (allMain[delIndex][0], allMain[delIndex][1]))
            connection.commit()
            if row > -1:  # Если есть выделенная строка/элемент
                self.tableWidget.removeRow(row)
                self.tableWidget.selectionModel().clearCurrentIndex()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    splash = QtWidgets.QSplashScreen(QPixmap('startIcon.jpg'))  # Загружаем изображение;
    splash.setFixedWidth(1000)
    splash.setFixedHeight(800)
    splash.show()  # Отображаем заставку;
    for i in range(0,100):
        splash.showMessage('Загрузка данных...{'+ str(i) +'}%',
                       Qt.AlignHCenter | Qt.AlignBottom, Qt.white)
        time.sleep(0.001)

    QtWidgets.qApp.processEvents()  # Оборот цикла;
    ex = App()
    ex.show()
    splash.finish(ex)
    sys.exit(app.exec())


