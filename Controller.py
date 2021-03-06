import json
import os
import socket
import sys
import threading
import time

import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

import startroom
from Connector import Connector
from views import login, instruction, home, chatOpt, chatRoom, FullTodo, reserveShow, reserveForm, assignment, profile,allEmployee,createport,selectroom
from models import user, TodoList, Reservation
#placeholder for user data
globalUserData=None
authority=None
global nameData
connector=Connector()
# login page
class loginWindow(QtWidgets.QWidget, login.Ui_Form):

    def __init__(self, parent=None):
        self.invalidCount=0
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.login.clicked.connect(self.doLogin)
        self.window2 = None
        self.setWindowOpacity(0.98)
        self.setStyleSheet("background-color:#121317;")
        self.user_entry.returnPressed.connect(self.doLogin)
        self.pass_entry.returnPressed.connect(self.doLogin)

    def doLogin(self):

        username = self.user_entry.text()
        psw = self.pass_entry.text()
        # authenticate
        data = {'username': username, 'password': psw}
        url = "Somchai/login"

        # post and return user
        result, cookies = connector.postWithData(url, data)

        if not self.isDict(result.text):  # check if result.text can change back to dict, if not then its not a json
            self.dialog(result.text)
        else:
            userData = json.loads(result.text)

            fullname = userData.get("name")
            firstName = fullname.split(" ")[0]
            lastName = fullname.split(" ")[1]
            email = userData.get("email")
            phone = userData.get("phone")
            department = userData.get("department")
            position = userData.get("position")
            p = user.User()
            p.setUser(firstName=firstName, lastName=lastName, email=email, phone=phone, department=department, privillege=position)
            global globalUserData
            globalUserData = p
            print(globalUserData)
            # setup home
            if self.window2 is None:
                self.window2 = homeWindow(cookie=cookies)
                self.window2.show()
                self.close()
            else:
                print("....")

    # create dialog box
    def dialog(self, mes):
        self.invalidCount+=1
        if self.invalidCount==3:
            mes="Too many retrials, please retry later"
            self.setDisabled(True)
        # initial dialog box
        self.w = QtWidgets.QDialog(self)
        layout = QtWidgets.QVBoxLayout()

        # massage and button
        massage = QtWidgets.QLabel("Caution : " + mes)

        massage.setStyleSheet("color:red;font-size:18px;")
        bt = QtWidgets.QPushButton("OK")
        bt.clicked.connect(self.closeCaution)
        bt.setStyleSheet("font-size:18px;color:white;")
        # add massage to layout
        layout.addWidget(massage)
        layout.addWidget(bt)

        # set layout to widget
        self.w.setLayout(layout)
        self.w.show()
    def closeCaution(self):
        self.w.close()
    def isDict(self, mes):
        try:
            dic = json.loads(mes)
        except ValueError as e:
            return False
        return True

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter:
            print("in")
            self.login.clicked()

class allEmployeeForm(QtWidgets.QWidget,allEmployee.Ui_Form):
     def __init__(self, cookie, parent=None):
         self.cookie=cookie
         QtWidgets.QWidget.__init__(self, parent)
         self.setupUi(self)
# home page
class homeWindow(QtWidgets.QWidget, home.Ui_Form):
    def __init__(self, cookie, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.setWindowOpacity(0.98)
        self.setStyleSheet("background-color:#121317;")
        self.help_button.clicked.connect(self.doHelp)
        self.chat_button.clicked.connect(self.doChat)
        self.todo_button.mousePressEvent=self.doTodo
        self.todo_label.mousePressEvent=self.doTodo
        self.list_widget.mousePressEvent=self.doTodo
        self.reserve_button.clicked.connect(self.doReserveShow)
        self.profile_button.clicked.connect(self.doProfile)
        self.helpWindow=None
        self.chatopWindow=None
        self.todoWindow=None
        self.reserveShow=None
        self.profileWindow=None
        self.employeeWindow=None
        self.cookie = cookie
        self.queryTodo()
        global authority
        global globalUserData
        print(globalUserData)
        authority = globalUserData.get_privillege().lower()
        print(authority)
    def doProfile(self):
        if self.profileWindow is None:
            r,cookie=connector.get("Somchai/Profile/getProfile",cookie=self.cookie)
            if not self.isDict(r.text):  # check if result.text can change back to dict, if not then its not a json
                print("no yet")
            else:
                profileData = json.loads(r.text)
                print(profileData)
                self.profileWindow = profileForm(self.cookie)
                self.profileWindow.header_label.setText(profileData['fullName'].partition(' ')[0])
                self.profileWindow.nametag.setText(profileData['fullName'])
                nameData=profileData['fullName']
                self.profileWindow.emailtag.setText(profileData['email'])
                self.profileWindow.phonetag.setText(profileData['phone'])
                self.profileWindow.postag.setText(profileData['position'])
                self.profileWindow.deptag.setText(profileData['department'])
                self.profileWindow.show()
        if self.employeeWindow is None:
            temp=""
            self.employeeWindow=allEmployeeForm(self.cookie)
            self.employeeWindow.setStyleSheet("background-color:white;")
            if authority!=None and (authority=="manager" or authority=="ceo"):
                r,cookie=connector.get("Somchai/get_allUserData",cookie=self.cookie)
                if not self.isDict(r.text):  # check if result.text can change back to dict, if not then its not a json
                    print("no yet")
                else:
                    allData = json.loads(r.text)
                    print(allData)
                    for pack in allData:
                        temp+=allData[pack]['Name']+" "
                        temp+=": "+allData[pack]['position']+" "
                        temp+=allData[pack]['department']+" "
                        temp+=allData[pack]['email']
                        temp+=allData[pack]['phone']
                        self.employeeWindow.employeeList.addItem(temp)
                        temp=""

            self.employeeWindow.show()

    def doReserveShow(self):
        if self.reserveShow is None:
            self.reserveShow = ReserveShow(self.cookie)
        self.reserveShow.show()

    def doHelp(self):
        if self.helpWindow is None:
            self.helpWindow = HelpWindow()
        self.helpWindow.show()

    def doChat(self):
         if self.chatopWindow is None:
             self.chatopWindow = ChatOptionForm(self.cookie)
             if authority==None or (authority!="manager" and authority!="ceo"):
                 self.chatopWindow.createButton.setDisabled(True)
         self.chatopWindow.show()

    def doTodo(self,event):
        print("before todo " + str(self.cookie))
        if self.todoWindow is None:
             self.todoWindow = FullTodoForm(self.cookie,self)
        self.todoWindow.show()

    def closeEvent(self, *args, **kwargs):

        r, self.cookie = connector.post("Somchai/logout", cookie=self.cookie)
        print(r.text)
        os._exit()

    def isDict(self, mes):
        try:
            dic = json.loads(mes)
        except ValueError as e:
            return False
        return True


    def queryTodo(self):
        self.list_widget.clear()
        count=6
        #query todoList for that user
        r,cookie=connector.get("Somchai/Todo/getTodo",cookie=self.cookie)
        if not self.isDict(r.text):  # check if result.text can change back to dict, if not then its not a json
            print("no todo yet")
        else:
            todoData = json.loads(r.text)
            for todo in todoData:
                self.list_widget.addItem(todoData[todo])
                count-=1
                if(count<0):
                    break


# help page - finishes
class HelpWindow(QtWidgets.QWidget, instruction.Ui_Form):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.setWindowOpacity(0.9)
        self.setStyleSheet("background-color:#ffd200;")

#chat option
class ChatOptionForm(QtWidgets.QWidget, chatOpt.Ui_Form):
      def __init__(self,cookie, parent=None):
        QtWidgets.QWidget.__init__(self,parent)
        self.cookie = cookie
        self.setupUi(self)
        self.setWindowOpacity(0.98)
        self.setStyleSheet("background-color:#121317;")
        self.joinButton.clicked.connect(self.invokeChat)
        self.createButton.clicked.connect(self.invokePort)
        #self.chatRoomWindow=None
      def invokeChat(self):
          self.hide()
          #if self.chatRoomWindow is None:
          self.chatRoomWindow=ChatRoomSelect(self.cookie)
          self.chatRoomWindow.show()
      def invokePort(self):
          self.hide()
          #if self.chatRoomWindow is None:
          self.chatRoomWindow=CreatingRoom(self.cookie)
          self.chatRoomWindow.show()
#################################
# Open a Server class
class CreatingRoom(QtWidgets.QWidget, createport.create_server):
    def __init__(self, cookie, parent=None):
        self.cookie = cookie
        QtWidgets.QWidget.__init__(self, parent)
        self.setup(self)
        self.setWindowOpacity(0.98)
        self.setStyleSheet("background-color:#121317;color:pink;")
        self.accept_button.clicked.connect(self.create)

    def create(self):
        # ---- This is for Public IP address ---- #
        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # s.connect(("google.com", 80))
        # s.getsockname() ---- This return Public IPADDRESS + Public PORT (where is not require)
        self.form.hide()
        self.port = 8005
        self.mcli = self.input_box.text()
        self.rname = self.input2_box.text()
        self.startServer()

    def startServer(self):
        self.__iniserver = startroom.create_room(self.mcli, self.host, self.port)
        self.addroom()

        # ---- IP, Port, and Room Name is kept into database for later query ---- #
    def addroom(self):
        IP = self.host
        PORT = self.port
        NAME = self.rname
        data = {'roomIP': IP, 'roomPort': PORT, 'roomName': NAME}
        url = "Somchai/Chat/createChat"
        # post and return user
        result, cookies = connector.postWithData(url, data,cookie=self.cookie)
        # --------------------------------------- #

# Select avaliable Room when a Server is created
class ChatRoomSelect(QtWidgets.QWidget, selectroom.select_room):
    def __init__(self, cookie, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.cookie = cookie
        self.setup_ui(self)
        self.roomlist=[]
        # --- invoke method to get room --- #
        self.queryRoom()
        #if (self.listWidget.count() > 0):
        #    self.listWidget.setCurrentRow(0)
        # --- ------------------------- --- #
        self.chat_button.clicked.connect(self.getdata)

        self.setWindowOpacity(0.98)
        self.setStyleSheet("background-color:#121317;")

    def queryRoom(self):
        # query avaliable Room
        r, cookie = connector.get("Somchai/Chat/getChat", cookie=self.cookie)
        if(r.text == "no room"):
            self.listWidget.addItem("no room")
            return 0
        else:
            temp=""
            roomData = json.loads(r.text)
            for reserve in roomData:
                #for item in roomData[reserve]:
                    #temp+=roomData[reserve][item]+" "
                self.roomlist.append(roomData[reserve])
                temp+=roomData[reserve]['chatName']+" "
                temp+=roomData[reserve]['owner']+" "
                temp+=roomData[reserve]['chatIP']+" "
                temp+=roomData[reserve]['chatPort']
                self.listWidget.addItem(temp)
                temp=""

    def isDict(self, mes):
        try:
            dic = json.loads(mes)
        except ValueError as e:
            return False
        return True


    def getdata(self):
        if(self.listWidget.count() > 0):
            #serverdetail=self.listWidget.currentItem().text()
            content=self.roomlist[self.listWidget.currentRow()]
            self.cIP = content['chatIP']
            self.cPORT = content['chatPort']
            self.connection()

    def connection(self):
        # Receieve Clicked Widget Data (IP, Port, and Name)

        self.enter = enterChat( cookie=self.cookie, ip=self.cIP, port=int(self.cPORT)) # send(IP,PORT) to start chat
        self.enter.show()


class enterChat(QtWidgets.QWidget, chatRoom.Ui_Form):
    def __init__(self, cookie, ip, port, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setStyleSheet("background-color:#0cc7d6;")
        self.setWindowOpacity(0.94)
        self.cookie = cookie
        self.useIP = ip
        self.usePORT = port
        self.setupUi(self)
        self.messageEdit.returnPressed.connect(self.sendMsg)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        global globalUserData
        self.connection()

    def closeEvent(self, QCloseEvent):
        hehe = "out:" + globalUserData.get_firstName() + " " + globalUserData.get_lastName()
        hehe = hehe.encode("utf-8")
        self.sock.send(hehe)
        self.sock.close()

    def connection(self):

        self.sock.connect((self.useIP, int(self.usePORT)))
        data = self.sock.recv(1024)
        data = data.decode('utf-8')
        if data == "ready":
            hehe = globalUserData.get_firstName() + " " + globalUserData.get_lastName()
            hehe = hehe.encode("utf-8")
            self.sock.send(hehe)
        #except:
        #    warning = QtWidgets.QMessageBox.warning(self,"Error","Cannot connect to your host",QtWidgets.QMessageBox.Ok)
        #    #warning.show()
        #    self.close()
        threading.Thread(target=self.recvMsg).start()

    def sendMsg(self):
        self.msg = globalUserData.get_firstName() + " " + globalUserData.get_lastName()+":" + self.messageEdit.text()
        self.messageEdit.clear()
        #self.msg = self.encrypt(self.msg)
        self.msg = self.msg.encode("utf-8")
        self.sock.send(self.msg)

    def recvMsg(self):
        while True:
            time.sleep(0.050)
            try:
                self.rec = self.sock.recv(1024)
                self.rec = self.rec.decode("utf-8")
                if "pe_pp:" in self.rec:
                    self.onlineList.clear()
                    r = self.rec.split(":")
                    r.remove("pe_pp")
                    for i in r:
                        self.onlineList.addItem(i)
                else:
                    #self.rec = self.decrypt(self.rec)
                    # need to implement which user send msg
                    r = self.rec.split(":")
                    temp="<" + r[0] + ">" + r[1]
                    self.messageList.addItem(temp)
            except ConnectionError as e:
                print("connection reset")

    def encrypt(self, word):
        tempword = ""
        count = 3
        for i in word:
            if count == 6:
                count = 3
            tempword += chr(ord(i) - count)
            count += 1
        return tempword

    def decrypt(self, word):
        tempword = ""
        count = 3
        for i in word:
            if count == 6:
                count = 3
            tempword += chr(ord(i) + count)
            count += 1
        return tempword

    # for looking when new user enter
    def onlineuser(self):
        self.onlineList
#################################


class FullTodoForm(QtWidgets.QWidget,FullTodo.Ui_Form ):
    def __init__(self,cookie, mini,parent=None):
        QtWidgets.QWidget.__init__(self,parent)
        self.mini=mini
        self.setupUi(self)
        self.cookie=cookie
        print("todo "+ str(self.cookie))
        self.setWindowOpacity(0.98)
        self.setStyleSheet("background-color:#121317;")
        self.addButton.clicked.connect(self.invokeAssign)
        self.assignWindow=None
        self.finishButton.clicked.connect(self.delTodo)
        if(self.tasksList.count()>0):
            self.tasksList.setCurrentRow(0)
        self.queryTodo()
    def invokeAssign(self):
        if self.assignWindow is None:
             self.assignWindow=assignForm(self.cookie)
        self.assignWindow.show()
        self.assignWindow.assignButton.clicked.connect(self.queryTodo)
    def isDict(self, mes):
        try:
            dic = json.loads(mes)
        except ValueError as e:
            return False
        return True
    def queryTodo(self):
        self.mini.queryTodo()
        self.tasksList.clear()
        #query todoList for that user
        r,cookie=connector.get("Somchai/Todo/getTodo",cookie=self.cookie)
        if not self.isDict(r.text):  # check if result.text can change back to dict, if not then its not a json
            print("no todo yet")
        else:
            todoData = json.loads(r.text)
            print(todoData)
            for todo in todoData:
                self.tasksList.addItem(todoData[todo])
    def delTodo(self):
        if(self.tasksList.count()>0):
            detail=self.tasksList.currentItem().text()
            data = {'des':detail}
            url = "Somchai/Todo/deleteTodo"
            listItems=self.tasksList.selectedItems()
            for item in listItems:
                self.tasksList.takeItem(self.tasksList.row(item))
            result, cookies = connector.postWithData(url, data)

class ReserveShow(QtWidgets.QWidget,reserveShow.Ui_Form ):
      def __init__(self, cookie,parent=None):
        QtWidgets.QWidget.__init__(self,parent)
        self.cookie=cookie
        self.setupUi(self)
        self.list=[]
        self.reserved_list.setStyleSheet("color:white;font-size:15px;")
        self.cancelButton.clicked.connect(self.cancelMeeting)
        self.setWindowOpacity(0.98)
        self.reserveButton.clicked.connect(self.showForm)
        self.reserveForm=None
        self.setStyleSheet("background-color:#121317;")
        if authority==None or (authority!="manager" and authority!="ceo"):
            self.reserveButton.setDisabled(True)
        self.showReserved()
      def cancelMeeting(self):
        if(self.reserved_list.count()>0):
            detail=self.reserved_list.currentItem().text()
            data=self.list[self.reserved_list.currentRow()]
            print(data)
            url = "Somchai/Meeting/deleteReserve"
            listItems=self.reserved_list.selectedItems()
            for item in listItems:
                self.reserved_list.takeItem(self.reserved_list.row(item))
            result, cookies = connector.postWithData(url, data)
      def isDict(self, mes):
        try:
            dic = json.loads(mes)
        except ValueError as e:
            return False
        return True
      def showForm(self):
          if self.reserveForm is None:
             self.reserveForm=ReserveForm(self.cookie)
             self.reserveForm.reserveButton.clicked.connect(self.updateReserve)
          self.reserveForm.show()
      def updateReserve(self):
          self.reserved_list.clear()
          self.showReserved()
      def showReserved(self):
        temp=""
        r,cookie=connector.get("Somchai/Meeting/getReserve",cookie=self.cookie)
        reserveData = json.loads(r.text)
        print(reserveData)
        for reserve in reserveData:
            temp+=reserveData[reserve]['topic']+" "
            temp+=reserveData[reserve]['room']+" "
            temp+=reserveData[reserve]['time']+" "
            temp+=reserveData[reserve]['owner']+" "
            ##
            self.list.append(reserveData[reserve])
            ##
            self.reserved_list.addItem(temp)
            temp=""


class ReserveForm(QtWidgets.QWidget,reserveForm.Ui_Form ):
     def __init__(self,cookie, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        print(cookie)
        self.cookie=cookie
        self.setupUi(self)
        self.setWindowOpacity(0.98)
        self.setStyleSheet("background-color:#f8e71d;")
        self.reserveButton.clicked.connect(self.addReserve)
        self.fillRoom()
     def isDict(self, mes):
        try:
            dic = json.loads(mes)
        except ValueError as e:
            return False
        return True
     def fillRoom(self):
        r,cookie=connector.get("Somchai/Meeting/getRoom",cookie=self.cookie)
        if not self.isDict(r.text):  # check if result.text can change back to dict, if not then its not a json
            print("empty")
        else:
            reserveData = json.loads(r.text)
            for item in reserveData:
                self.roomList.addItem(reserveData[item])
     def addReserve(self):
         
         detail=str(self.topicEdit.text())
         start=self.dateTimeEdit.text()
         end=self.dateTimeEdit_2.text()
         room=self.roomList.currentItem().text()
         data={'topic':detail,'roomStart':start,'roomEnd':end,'room':room,}
         url="Somchai/Meeting/makeReserve"
        # post and return user
         result, cookies = connector.postWithData(url, data, self.cookie)

         if(result.text == "Overlapped"):
            self.w = QtWidgets.QDialog(self)
            layout = QtWidgets.QVBoxLayout()

            # massage and button
            massage = QtWidgets.QLabel("This room has been reserved at this time")

            massage.setStyleSheet("color:red;font-size:18px;")
            bt = QtWidgets.QPushButton("OK")
            #bt.clicked.connect(self.closeCaution)
            bt.setStyleSheet("font-size:18px;color:white;")
            # add massage to layout
            layout.addWidget(massage)
            layout.addWidget(bt)

            # set layout to widget
            self.w.setLayout(layout)
            self.w.show()


class assignForm(QtWidgets.QWidget,assignment.Ui_Form ):
    def __init__(self, cookie,parent=None):
        self.cookie=cookie
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.setWindowOpacity(0.98)
        self.setStyleSheet("background-color:#2283f6;")
        self.assignButton.clicked.connect(self.addTask)
        self.fillEmployee()
    def isDict(self, mes):
        try:
            dic = json.loads(mes)
        except ValueError as e:
            return False
        return True
    def fillEmployee(self):
        #non-authority is only allowed to assign work to themselves
        if authority==None or (authority!="manager" and authority!="ceo"):
            print(authority)
            print("kak")
            self.employeeBox.addItem(nameData)
            return
        r,cookie=connector.get("Somchai/get_allUser",cookie=self.cookie)
        if not self.isDict(r.text):  # check if result.text can change back to dict, if not then its not a json
            print("no employee yet")
        else:
            emploData = json.loads(r.text)
            print(emploData)
            for employee in emploData:
                self.employeeBox.addItem(emploData[employee])

    def addTask(self):
        usr = str(self.employeeBox.currentText())
        detail=str(self.descripEdit.toPlainText())
        start=self.dateTimeEdit.text()
        end=self.dateTimeEdit_2.text()
        detail=detail+" from "+start+" to "+end
        data = {'user': usr, 'taskDescription':detail,}
        url = "Somchai/Todo/addTodo"
        # post and return user
        result, cookies = connector.postWithData(url, data)



class profileForm(QtWidgets.QWidget,profile.Ui_Form):
     def __init__(self,cookie, parent=None):
        self.cookie=cookie
        QtWidgets.QWidget.__init__(self, parent)
        self.setStyleSheet("background-color:#01cc9f;")
        self.setupUi(self)
        self.setWindowOpacity(0.9)
        print(globalUserData)


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    window = loginWindow()
    window.show()
    sys.exit(app.exec_())