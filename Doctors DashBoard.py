import os
import sys
import PyQt5
import random
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import paho.mqtt.client as mqtt
import time
import json
import datetime
from mqtt_init import *

# Creating Client name - should be unique
global clientname
r = random.randrange(1, 10000000)
clientname = "doctor-"+str(r)
dashboard_topic = 'Hospital/Department/Room/patient'
global ON
ON = False

colors = {
    'yellow': '#ffff00',
    'red': '#ff0000',
    'green': '#00ff00'
}


class Mqtt_client():

    def __init__(self):
        # broker IP adress:
        self.broker = ''
        self.topic = ''
        self.port = ''
        self.clientname = ''
        self.username = ''
        self.password = ''
        self.subscribeTopic = ''
        self.publishTopic = ''
        self.publishMessage = ''
        self.on_connected_to_form = ''

        self.numberOfBadBloodPreasureDiastolic = 0
        self.numberOfBadBloodPreasureSystolic = 0
        self.numberOfBadHeartBeat = 0
        self.numberOfBadOxigen = 0
        self.numberOfBadBodyTemp = 0

    # Setters and getters
    def set_on_connected_to_form(self, on_connected_to_form):
        self.on_connected_to_form = on_connected_to_form

    def get_broker(self):
        return self.broker

    def set_broker(self, value):
        self.broker = value

    def get_port(self):
        return self.port

    def set_port(self, value):
        self.port = value

    def get_clientName(self):
        return self.clientName

    def set_clientName(self, value):
        self.clientName = value

    def get_username(self):
        return self.username

    def set_username(self, value):
        self.username = value

    def get_password(self):
        return self.password

    def set_password(self, value):
        self.password = value

    def get_subscribeTopic(self):
        return self.subscribeTopic

    def set_subscribeTopic(self, value):
        self.subscribeTopic = value

    def get_publishTopic(self):
        return self.publishTopic

    def set_publishTopic(self, value):
        self.publishTopic = value

    def get_publishMessage(self):
        return self.publishMessage

    def set_publishMessage(self, value):
        self.publishMessage = value

    def on_log(self, client, userdata, level, buf):
        print("log: "+buf)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("connected OK")
            self.on_connected_to_form()
        else:
            print("Bad connection Returned code=", rc)

    def on_disconnect(self, client, userdata, flags, rc=0):
        print("DisConnected result code "+str(rc))

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        print("message from:"+topic, m_decode)
        try:
            data = json.loads(m_decode)
            self.process_data(data)
        except:
            print("not paying attentiion to Warning messages")

    def process_data(self, data):
        self.handleBloodPreasure(data)
        self.handleHeartBeat(data)
        self.handleBodyTemp(data)
        self.handleOxygen(data)

    def handleBloodPreasure(self, data):
        # split into 2 parts the systolic and distolic
        blood_preasure = data['blood_preasure'].split("/")

        # check if higher than noraml and if the button is not red to indicate that
        # there is an unusual measurement

        if (int(blood_preasure[0]) >= 120 and mainwin.connectionDock.blood_pressure.styleSheet() != colors['red']):
            self.publish_to(dashboard_topic, "High systolic blood preasure")
            mainwin.connectionDock.update_btn_state(
                mainwin.connectionDock.blood_pressure, 'yellow')
            self.numberOfBadBloodPreasureSystolic += 1

        if (int(blood_preasure[1]) >= 80):
            self.publish_to(dashboard_topic, "High diastolic blood preasure")
            mainwin.connectionDock.update_btn_state(
                mainwin.connectionDock.blood_pressure, 'yellow')
            self.numberOfBadBloodPreasureDiastolic += 1

        # good measurement resets the indicator to green and resets the count

        if not (int(blood_preasure[1]) <= 80 or int(blood_preasure[0]) <= 120):
            mainwin.connectionDock.update_btn_state(
                mainwin.connectionDock.blood_pressure, 'green')
            self.numberOfBadBloodPreasureSystolic = 0
            self.numberOfBadBloodPreasureDiastolic = 0

        # 5 bad measurements turn the button to red because for an half a minute there were
        # only bad measurements

        if self.numberOfBadBloodPreasureSystolic > 5 and self.numberOfBadBloodPreasureDistolic > 5:
            mainwin.connectionDock.update_btn_state(
                mainwin.connectionDock.blood_pressure, 'red')

    def handleHeartBeat(self, data):

        # check if higher than noraml and if the button is not red to indicate that
        # there is an unusual measurement

        if int(data['heart_beat']) >= 120 and mainwin.connectionDock.heartbeat.styleSheet() != colors['red']:
            self.publish_to(dashboard_topic, "High heart beat")
            mainwin.connectionDock.update_btn_state(
                mainwin.connectionDock.heartbeat, 'yellow')
            self.numberOfBadHeartBeat += 1

        # good measurement resets the indicator to green and resets the count

        else:
            mainwin.connectionDock.update_btn_state(
                mainwin.connectionDock.heartbeat, 'green')
            self.numberOfBadHeartBeat = 0

        # 5 bad measurements turn the button to red because for an half a minute there were
        # only bad measurements

        if self.numberOfBadHeartBeat > 5:
            mainwin.connectionDock.update_btn_state(
                mainwin.connectionDock.heartbeat, 'red')

    def handleBodyTemp(self, data):

        # check if higher than noraml and if the button is not red to indicate that
        # there is an unusual measurement

        if float(data['body_temp']) >= 38.5 and mainwin.connectionDock.bodytemp.styleSheet() != colors['red']:
            self.publish_to(dashboard_topic, "High body temperature")
            mainwin.connectionDock.update_btn_state(
                mainwin.connectionDock.bodytemp, 'yellow')
            self.numberOfBadBodyTemp += 1

        # good measurement resets the indicator to green and resets the count

        else:
            mainwin.connectionDock.update_btn_state(
                mainwin.connectionDock.bodytemp, 'green')
            self.numberOfBadBodyTemp = 0

        # 5 bad measurements turn the button to red because for an half a minute there were
        # only bad measurements

        if self.numberOfBadBodyTemp > 5:
            mainwin.connectionDock.update_btn_state(
                mainwin.connectionDock.bodytemp, 'red')

    def handleOxygen(self, data):

        # check if higher than noraml and if the button is not red to indicate that
        # there is an unusual measurement

        if int(data['oxygen_precentage']) < 90 and mainwin.connectionDock.oxygen.styleSheet() != colors['red']:
            self.publish_to(dashboard_topic, "Low Oxygen precentage")
            mainwin.connectionDock.update_btn_state(
                mainwin.connectionDock.oxygen, 'yellow')
            self.numberOfBadOxigen += 1

        # good measurement resets the indicator to green and resets the count

        else:
            mainwin.connectionDock.update_btn_state(
                mainwin.connectionDock.oxigen, 'green')
            self.numberOfBadOxigen = 0

        # 5 bad measurements turn the button to red because for an half a minute there were
        # only bad measurements

        if (self.numberOfBadOxigen > 5):
            mainwin.connectionDock.update_btn_state(
                mainwin.connectionDock.oxygen, 'red')

    def connect_to(self):
        # Init paho mqtt client class
        # create new client instance
        self.client = mqtt.Client(self.clientname, clean_session=True)
        self.client.on_connect = self.on_connect  # bind call back function
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log
        self.client.on_message = self.on_message
        self.client.username_pw_set(self.username, self.password)
        print("Connecting to broker ", self.broker)
        self.client.connect(self.broker, self.port)  # connect to broker

    def disconnect_from(self):
        self.client.disconnect()

    def start_listening(self):
        self.client.loop_start()

    def stop_listening(self):
        self.client.loop_stop()

    def subscribe_to(self, topic):
        self.client.subscribe(topic)

    def publish_to(self, topic, message):
        self.client.publish(topic, message)


class ConnectionDock(QDockWidget):
    """Main """

    def __init__(self, mc):
        QDockWidget.__init__(self)

        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)
        self.eHostInput = QLineEdit()
        self.eHostInput.setInputMask('999.999.999.999')
        self.eHostInput.setText(broker_ip)

        self.ePort = QLineEdit()
        self.ePort.setValidator(QIntValidator())
        self.ePort.setMaxLength(4)
        self.ePort.setText(broker_port)

        self.eClientID = QLineEdit()
        global clientname
        self.eClientID.setText(clientname)

        self.eUserName = QLineEdit()
        self.eUserName.setText(username)

        self.ePassword = QLineEdit()
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.ePassword.setText(password)

        self.eKeepAlive = QLineEdit()
        self.eKeepAlive.setValidator(QIntValidator())
        self.eKeepAlive.setText("60")

        self.eSSL = QCheckBox()

        self.eCleanSession = QCheckBox()
        self.eCleanSession.setChecked(True)

        self.eConnectbtn = QPushButton("Enable/Connect", self)
        self.eConnectbtn.setToolTip("click me to connect")
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)
        self.eConnectbtn.setStyleSheet("background-color: gray")

        self.eSubscribeTopic = QLineEdit()
        self.eSubscribeTopic.setText(dashboard_topic)

        self.bodytemp = QPushButton("Body Temperature", self)
        self.bodytemp.setToolTip("red = bad")
        self.bodytemp.setStyleSheet("background-color: green")

        self.heartbeat = QPushButton("Heart Beat", self)
        self.heartbeat.setToolTip("red = bad")
        self.heartbeat.setStyleSheet("background-color: green")

        self.oxygen = QPushButton("Oxygen Precentage", self)
        self.oxygen.setToolTip("red = bad")
        self.oxygen.setStyleSheet("background-color: green")

        self.blood_pressure = QPushButton("Blood Preassure", self)
        self.blood_pressure.setToolTip("red = bad")
        self.blood_pressure.setStyleSheet("background-color: green")

        formLayot = QFormLayout()
        formLayot.addRow("Turn On/Off", self.eConnectbtn)
        formLayot.addRow("Sub topic", self.eSubscribeTopic)
        formLayot.addRow("", self.bodytemp)
        formLayot.addRow("", self.heartbeat)
        formLayot.addRow("", self.oxygen)
        formLayot.addRow("", self.blood_pressure)

        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)
        self.setWindowTitle("Connect")

    def on_connected(self):
        self.eConnectbtn.setStyleSheet("background-color: green")

    def on_button_connect_click(self):
        self.mc.set_broker(self.eHostInput.text())
        self.mc.set_port(int(self.ePort.text()))
        self.mc.set_clientName(self.eClientID.text())
        self.mc.set_username(self.eUserName.text())
        self.mc.set_password(self.ePassword.text())
        self.mc.connect_to()
        self.mc.start_listening()
        self.mc.subscribe_to(self.eSubscribeTopic.text())

    def update_btn_state(self, button, color):
        button.setStyleSheet(f"background-color: {color}")


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        # Init of Mqtt_client class
        self.mc = Mqtt_client()

        # general GUI settings
        self.setUnifiedTitleAndToolBarOnMac(True)

        # set up main window
        self.setGeometry(30, 300, 400, 150)
        self.setWindowTitle('DashBoard')

        # Init QDockWidget objects
        self.connectionDock = ConnectionDock(self.mc)
        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)


app = QApplication(sys.argv)
mainwin = MainWindow()
mainwin.show()
app.exec_()
