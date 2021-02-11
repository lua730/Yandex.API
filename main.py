import math


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from main_ui_file import Ui_MainWindow
from help_ui_file import Ui_Dialog
import requests
import sys

import traceback
def log_uncaught_exceptions(type, value, tb):
    text = '{}: {}:\n'.format(type.name, value)
    text += ''.join(traceback.format_tb(tb))
    print(text)
    sys.exit()
sys.excepthook = log_uncaught_exceptions

class SearchResult(object):
    def __init__(self, point, address, postal_code=None):
        self.point = point
        self.address = address
        self.postal_code = postal_code

class MapParams(object):
    # Параметры по умолчанию.
    def __init__(self):
        self.lat = 55.729738  # Координаты центра карты на старте.
        self.lon = 37.664777
        self.zoom = 15  # Масштаб карты на старте.
        self.type = "map"  # Тип карты на старте.

        self.search_result = None  # Найденный объект для отображения на карте.
        self.use_postal_code = False

    # Преобразование координат в параметр ll
    def ll(self):
        return ll(self.lon, self.lat)

def ll(x, y):
    return "{0},{1}".format(x, y)

def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"

class MyHelpDialog(QMainWindow, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.label_secret.hide()
        self.label_secret.setGeometry(10, 60, 301, 141)

        # Присвоение стилей и шрифтов
        QtGui.QFontDatabase.addApplicationFont('sources/fonts/Proxima Nova.otf')
        self.label_name.setFont(QtGui.QFont("Proxima Nova", 12))
        self.pushButton_page3.setFont(QtGui.QFont("Proxima Nova", 12))
        self.textEdit.setReadOnly(True)
        self.textEdit.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        #   Безрамочное окно + кнопки в заголовке
        self.SizeWidht = 339
        self.SizeHeight = 300
        self.setFixedSize(self.SizeWidht, self.SizeHeight)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setMouseTracking(True)
        self.grapping = False
        self.label_name.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)  # Сделать название программы невидимым для мыши

        # Подлключение функций у виджетам
        self.pushButton_page3.clicked.connect(self.close)

    def close(self):
        ex.setEnabled(True)
        help_dialog.hide()

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.oldPos = event.globalPos()

        if self.label_secret.underMouse():
            self.label_secret.hide()

    def mouseMoveEvent(self, event):
        # Движение мыши
        if event.buttons() == QtCore.Qt.LeftButton:
            # Определение перетаскивания окна
            if self.groupBox_title.underMouse() and not self.grapping:
                self.grapping = True
                QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.ClosedHandCursor)

            delta = QtCore.QPoint(event.globalPos() - self.oldPos)  # Дельта движения мыши
            # Перетаскивание окна
            if self.grapping and self.groupBox_title.underMouse():
                self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

    def mouseDoubleClickEvent(self, event):
        if (app.keyboardModifiers() == QtCore.Qt.ControlModifier and event.button() ==
                QtCore.Qt.LeftButton):
            self.label_secret.show()

    def mouseReleaseEvent(self, event):
        # Отмена всех действий при отпускании мыши
        self.grapping = False
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)

class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.mp = MapParams()
        self.map_file = self.load_map()

        # Подобранные константы для поведения карты.
        self.LAT_STEP = 0.008  # Шаги при движении карты по широте и долготе
        self.LON_STEP = 0.02
        self.coord_to_geo_x = 0.0000428  # Пропорции пиксельных и географических координат.
        self.coord_to_geo_y = 0.0000428

        # Присвоение стилей и шрифтов
        QtGui.QFontDatabase.addApplicationFont('sources/fonts/Proxima Nova.otf')
        QtGui.QFontDatabase.addApplicationFont('sources/fonts/VK Sans Display.otf')
        self.label_name.setFont(QtGui.QFont("Proxima Nova", 12))
        self.label_2.setFont(QtGui.QFont("Proxima Nova", 12))
        self.label_4.setFont(QtGui.QFont("Proxima Nova", 12))
        self.label_buisness.setFont(QtGui.QFont("Proxima Nova", 12))
        self.pushButton_find.setFont(QtGui.QFont("Proxima Nova", 12))
        self.pushButton_delete.setFont(QtGui.QFont("Proxima Nova", 12))
        self.pushButton_page1.setFont(QtGui.QFont("Proxima Nova", 12))
        self.pushButton_page2.setFont(QtGui.QFont("Proxima Nova", 12))
        self.pushButton_page3.setFont(QtGui.QFont("Proxima Nova", 12))
        self.pushButton_help.setFont(QtGui.QFont("Proxima Nova", 11))
        self.label_error.setFont(QtGui.QFont("Proxima Nova", 12))
        self.label_error.setStyleSheet("color: red;")
        self.textEdit_business.setReadOnly(True)
        self.textEdit_business.setFont(QtGui.QFont("VK Sans Display", 11))




        #   Безрамочное окно + кнопки в заголовке
        self.SizeWidht = 1157
        self.SizeHeight = 602
        self.setFixedSize(self.SizeWidht, self.SizeHeight)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.exitAppButton.clicked.connect(sys.exit)
        self.exitAppButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.minimizeButton.clicked.connect(self.showMinimized)
        self.minimizeButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setMouseTracking(True)
        self.grapping = False
        self.label_name.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)  # Сделать название программы невидимым для мыши




        # Подлключение функций у виджетам
        self.horizontalSlider_size.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_page1.clicked.connect(self.update_map_type)
        self.pushButton_page1.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_page2.clicked.connect(self.update_map_type)
        self.pushButton_page2.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_page3.clicked.connect(self.update_map_type)
        self.pushButton_page3.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_find.clicked.connect(self.find_by_address)
        self.pushButton_find.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_delete.clicked.connect(self.delete_result)
        self.pushButton_delete.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_help.clicked.connect(self.open_help)
        self.pushButton_help.setFocusPolicy(QtCore.Qt.NoFocus)
        self.checkBox.clicked.connect(self.toogle_index)

    def open_help(self):
        self.setEnabled(False)
        help_dialog.show()

    def find_business(self, ll):
        search_api_server = "https://search-maps.yandex.ru/v1/?apikey=66bae606-0a57-4142-a52a-a165be12ec8e"
        search_params = {
            "lang": "ru_RU",
            "text": self.mp.search_result.address,
            "ll": ll,
             "spn": "0.001,0.001",
            "type": "biz"
        }
        response = requests.get(search_api_server, params=search_params)
        json_response = response.json()
        features = json_response["features"]
        business = ""
        for i in range(len(features)):
            try:
                business += str(features[i]["properties"]["name"]) + "\n"
            except Exception:
                pass
            try:

                business += str(features[i]["properties"]["CompanyMetaData"]["url"]) + "\n"
            except Exception:
                pass
            try:
                business += str(features[i]["properties"]["CompanyMetaData"]["Phones"][0]["formatted"]) + "\n"
            except Exception:
                pass
            business += "\n"

        self.textEdit_business.setText(business)

    # Преобразование экранных координат в географические.
    def screen_to_geo(self, pos):
        dy = 225 - pos[1]
        dx = pos[0] - 300
        lx = self.mp.lon + dx * self.coord_to_geo_x * math.pow(2, 15 - self.mp.zoom)
        ly = self.mp.lat + dy * self.coord_to_geo_y * math.cos(math.radians(self.mp.lat)) * math.pow(2,
                                                                                          15 - self.mp.zoom)
        return lx, ly

    def toogle_index(self):
        try:
            if self.checkBox.checkState():
                self.lineEdit_index.setText(str(self.mp.search_result.postal_code))
            else:
                self.lineEdit_index.setText("")
        except Exception:
            pass

    def delete_result(self):
        self.mp.search_result = None
        self.lineEdit_fullAddress.setText("")
        self.lineEdit_index.setText("")
        self.load_map()
        self.textEdit_business.setText("")
        self.label_error.setText("")

    def reverse_toponym_search(self, pos):
        self.delete_result()
        geo_cords = self.screen_to_geo(pos)
        point = "{0},{1}".format(geo_cords[0], geo_cords[1])


        geocoder_request_template = "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=" + point + "&format=json"
        response = requests.get(geocoder_request_template)
        response_json = response.json()
        if int(response_json["response"]["GeoObjectCollection"]["metaDataProperty"]["GeocoderResponseMetaData"][
                   "found"]):
            self.label_error.setText("")
            Full_address = \
            response_json["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"][
                "GeocoderMetaData"]["text"]
            cords = response_json["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"][
                "pos"]
            index = None
            try:
                index = \
                response_json["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"][
                    "GeocoderMetaData"]["AddressDetails"]["Country"]["AdministrativeArea"]["SubAdministrativeArea"][
                    "Locality"][
                    "Thoroughfare"][
                    "Premise"]["PostalCode"]["PostalCodeNumber"]
            except Exception:
                pass
            self.mp.search_result = SearchResult("{} {}".format(geo_cords[0], geo_cords[1]), Full_address, index)

            self.lineEdit_fullAddress.setText(Full_address)
            if self.checkBox.checkState():
                self.lineEdit_index.setText(str(index))
            self.load_map()
            self.find_business(point)
        else:
            self.delete_result()
            self.label_error.setText("Не найдено")
            self.load_map()

    def find_by_address(self):
        self.delete_result()
        address = self.lineEdit_findName.text()
        if address != "":
            response = requests.get(
                "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={" + address + "}&format=json")
            response_json = response.json()
            if int(response_json["response"]["GeoObjectCollection"]["metaDataProperty"]["GeocoderResponseMetaData"][
                       "found"]):
                self.label_error.setText("")
                Full_address = response_json["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"][
                          "GeocoderMetaData"]["text"]
                cords = response_json["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"][
                    "pos"]
                index = None
                try:
                    index = response_json["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"][
                              "GeocoderMetaData"]["AddressDetails"]["Country"]["AdministrativeArea"]["SubAdministrativeArea"]["Locality"][
                              "Thoroughfare"][
                              "Premise"]["PostalCode"]["PostalCodeNumber"]
                except Exception:
                    pass
                self.mp.search_result = SearchResult(cords, Full_address, index)

                self.mp.lat = float(cords.split()[1])
                self.mp.lon = float(cords.split()[0])
                self.lineEdit_fullAddress.setText(Full_address)
                if self.checkBox.checkState():
                    self.lineEdit_index.setText(str(index))
                self.load_map()
                point = "{0},{1}".format(cords[0], cords[1])
                self.lineEdit_findName.clearFocus()
                self.find_business(point)
            else:
                self.delete_result()
                self.label_error.setText("Не найдено")
                self.load_map()

    def update_map_type(self):
        s = int(self.sender().objectName()[-1])
        if s == 1:
            self.mp.type = "map"
        elif s == 2:  # 2
            self.mp.type = "sat"
        elif s == 3:  # 3
            self.mp.type = "sat,skl"
        self.load_map()

    # Создание карты с соответствующими параметрами.
    def load_map(self):
        map_request = "http://static-maps.yandex.ru/1.x/?ll={ll}&z={z}&l={type}".format(ll=self.mp.ll(),
                                                                                        z=self.mp.zoom,
                                                                                        type=self.mp.type)
        if self.mp.search_result:
            map_request += "&pt={0},{1},pm2grm".format(self.mp.search_result.point.split()[0],
                                                       self.mp.search_result.point.split()[1])
        response = requests.get(map_request)
        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        # Запишем полученное изображение в файл.
        map_file = "sources\map.png"
        try:
            with open(map_file, "wb") as file:
                file.write(response.content)
        except IOError as ex:
            print("Ошибка записи временного файла:", ex)
            sys.exit(2)
        self.label.setPixmap(QtGui.QPixmap(map_file))


    # объявление функций через functions.py
    def mousePressEvent(self, event):
        if not self.lineEdit_findName.underMouse():
            self.lineEdit_findName.clearFocus()
        if not self.lineEdit_fullAddress.underMouse():
            self.lineEdit_fullAddress.clearFocus()
        if not self.lineEdit_index.underMouse():
            self.lineEdit_index.clearFocus()

        if event.pos().x() > 11 and event.pos().y() > 89 and event.pos().x() < 611 and event.pos().y() < 538:
            self.reverse_toponym_search([event.pos().x()-11, event.pos().y()-89])

        if event.buttons() == QtCore.Qt.LeftButton:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        # Движение мыши
        if event.buttons() == QtCore.Qt.LeftButton:
            # Определение перетаскивания окна
            if self.groupBox_title.underMouse() and not self.grapping:
                self.grapping = True
                QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.ClosedHandCursor)

            delta = QtCore.QPoint(event.globalPos() - self.oldPos)  # Дельта движения мыши
            # Перетаскивание окна
            if self.grapping and self.groupBox_title.underMouse():
                self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        # Отмена всех действий при отпускании мыши
        self.grapping = False
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_PageUp:
            if self.horizontalSlider_size.value() < self.horizontalSlider_size.maximum():
                self.horizontalSlider_size.setValue(self.horizontalSlider_size.value() + 1)
                self.mp.zoom = self.horizontalSlider_size.value()
        elif event.key() == QtCore.Qt.Key_PageDown:
            if self.horizontalSlider_size.value() > self.horizontalSlider_size.minimum():
                self.horizontalSlider_size.setValue(self.horizontalSlider_size.value() - 1)
                self.mp.zoom = self.horizontalSlider_size.value()
        elif event.key() == QtCore.Qt.Key_Left:                         # LEFT_ARROW
            self.mp.lon -= self.LON_STEP * math.pow(2, 15 - int(self.mp.zoom))
        elif event.key() == QtCore.Qt.Key_Right:                        # RIGHT_ARROW
            self.mp.lon += self.LON_STEP * math.pow(2, 15 - int(self.mp.zoom))
        elif event.key() == QtCore.Qt.Key_Up and self.mp.lat < 85:      # UP_ARROW
            self.mp.lat += self.LAT_STEP * math.pow(2, 15 - int(self.mp.zoom))
        elif event.key() == QtCore.Qt.Key_Down and self.mp.lat > -85:  # DOWN_ARROW
            self.mp.lat -= self.LAT_STEP * math.pow(2, 15 - int(self.mp.zoom))

        while self.mp.lon > 180:
            self.mp.lon -= 360
        while self.mp.lon < -180:
            self.mp.lon += 360
        while self.mp.lat > 90:
            self.mp.lat -= 180
        while self.mp.lat < -90:
            self.mp.lat += 180
        self.load_map()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    help_dialog = MyHelpDialog()
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
