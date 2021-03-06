
import sys,os,time,copy,json,requests
import queue, threading
sys.path.append(os.getcwd())
from PyQt5.QtWidgets import QMainWindow, QPushButton,QMessageBox,QListView
from PyQt5 import QtWidgets, Qt, QtCore
from PyQt5.uic import loadUi

class SuccessException(Exception):
    def __init__(self, msg):
        self.msgs = msg

class MainWindow(QMainWindow):
    def __init__(self, *args):
        super(MainWindow, self).__init__(*args)
        loadUi('config.ui', self)
        self.startCalcBut.clicked.connect(self.startCalc)
        self.addSeedBut.clicked.connect(self.addSeed)
        self.threads = 8
        self.minSeedsGroup = 1
        self.maxSeedsGroup = 5
        self.queene = queue.Queue()
        self.bitcoin_url = ""
        self.bitcoin_rpcuser = ""
        self.bitcoin_rpcpassword = ""
        self.mainThread = None
        self.seedsJson = {}
        self.load()
        self.password = None
        self.hasErrors = False
        self.seedEdit.installEventFilter(self)
                
    def eventFilter(self, obj, event):
        if obj == self.seedEdit:
            if event.type() == QtCore.QEvent.KeyPress:
                if event.key() == QtCore.Qt.Key_Return:
                    self.addSeed()
        return super(MainWindow, self).eventFilter(obj, event)
    
    def addSeed(self):
        if self.seedEdit.text() is not None and self.seedEdit.text() not in self.getSeedListData():
            self.seedlist.addItem(self.seedEdit.text().lower())
            self.keysJson['seedlist'].append(self.seedEdit.text().lower())
            self.seedEdit.clear()
            self.save()
            
    def load(self):
        f = open("keys.txt", "r")
        keys = f.read()
        if len(keys) < 3:
            keys = '{"seedlist":[]}'
        self.keysJson = json.loads(keys)
        self.seedlist.clear()
        for l in range(len(self.keysJson['seedlist'] )):
            self.seedlist.addItem(self.keysJson['seedlist'][l])
        f.close()

        f = open("seeds.txt", "r")
        seeds = f.read()
        if len(seeds) == 0:
            seeds = "{}"
        self.seedsJson = json.loads(seeds)
        try:
            t = self.seedsJson['seeds']
        except:
            self.seedsJson['seeds'] = []
        f.close()

        f = open("config.txt", "r")
        cf = f.read()
        jsonStr = json.loads(cf)
        self.bitcoin_url = jsonStr['bitcoin_url']
        self.bitcoin_rpcuser = jsonStr['bitcoin_rpcuser']
        self.bitcoin_rpcpassword = jsonStr['bitcoin_rpcpassword']
        self.minSeedsGroup = jsonStr['minSeedsGroup']
        self.maxSeedsGroup = jsonStr['maxSeedsGroup']
        f.close()
        
    
    def save(self):
        f = open("seeds.txt", "r+")
        str1 = json.dumps(self.seedsJson)
        f.write(str1)
        f.close()
        f = open("keys.txt", "r+")
        str1 = json.dumps(self.keysJson)
        f.write(str1)
        f.close()
        

    def startCalc(self):
        self.password = None
        self.passwordLabel.setText("")
        s1 = "????????????"
        s2 = "???   ???"
        
        if self.startCalcBut.text() == s1:
            self.startCalcBut.setText(s2)
#            self.startCalcBut.setEnabled(False)

            if self.mainThread is None or not self.mainThread.is_alive():
                self.hasErrors = False
                seeds = self.getSeedListData()
                self.mainThread = threading.Thread(target=self.mainCalc, args=(seeds,))
                self.mainThread.setDaemon(True)
                self.mainThread.start()
        elif self.startCalcBut.text() == s2:
            self.hasErrors = True
            th = threading.Thread(target=self.cleanQueue)
            th.setDaemon(True)
            th.start()

    def cleanQueue(self):
        s3 = "?????????"
        self.startCalcBut.setEnabled(False)
        while True:
            time.sleep(0.03)
            if not self.queene.empty():
                self.queene.get()
                self.info.setText("????????????...... ??????:{0}".format(self.queene.qsize()))
            else:
                break

        self.startCalcBut.setText("????????????")
        self.startCalcBut.setEnabled(True)
        
    def closeEvent(self, event):
        quitMsgBox = QMessageBox()
        quitMsgBox.setWindowTitle('????????????')
        quitMsgBox.setText('?????????????????????')
        quitMsgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        buttonY = quitMsgBox.button(QMessageBox.Yes)
        buttonY.setText('??????')
        buttonN = quitMsgBox.button(QMessageBox.No)
        buttonN.setText('??????')
        quitMsgBox.exec_()
        if quitMsgBox.clickedButton() == buttonY:
            event.accept()
        else:
            event.ignore()
    
    def callBitcoinByRpc(self, method, params=[]):
        payload = json.dumps({
            "jsonrpc": "2.0",
            "id": "minebet-{0}".format(time.time()),
            "method": method,
            "params": params
        })
        return requests.post(self.bitcoin_url, auth=(self.bitcoin_rpcuser, self.bitcoin_rpcpassword), data=payload, timeout=30).json()

    def getSeedListData(self):
        items = []
        for index in range(self.seedlist.count()):
            try:
                items.append(self.seedlist.item(index).text())
            except:
                pass
#                print(bs)
        return items

    def genMainSeeds(self, seeds, positions):

        if self.hasErrors:
            return

        while True:
            for index in range(len(seeds)):
                positions[0] = index
                seed = []
                for ii in range(len(positions)):
                    seed.append(seeds[positions[ii]])
                self.parseSeed(seed)
#                print("-----Seed: {0}".format("".join(seed)))

            ret = True
            for i in range(1, len(positions)):
                if positions[i] < len(seeds) - 1:
                    positions[i] = positions[i] + 1
                    for ii in range(0, i):
                        positions[ii] = 0
                    ret = False
                    break;
                
            if ret:
                return
                
    def parseSeed(self, seed):
        try:
            if self.hasErrors:
                return
            
            s = "".join(seed).lower()
            if s in self.seedsJson['seeds']:
#                print( "????????????[{0}]?????????????????? ?????????????????????{1} ".format(s))
#                time.sleep(0.1)
                try:
                    self.info.setText("????????????[{0}]??????????????????{1}".format(s))
                except:
                    pass
            else:
                self.mainSeeds(s)
                while True:
                    time.sleep(0.1)
                    if self.password is not None or self.hasErrors:
                        return
                    if self.queene.empty():
                        try:
                            self.callBitcoinByRpc('walletpassphrase', ['1234', 10])
                        except:
                            self.hasErrors = True
                        if not self.hasErrors and s not in self.seedsJson['seeds']:
                            self.seedsJson['seeds'].append(s)
                            self.save()
                        break;
        except:
            pass
        
        
    def mainCalc(self, seeds):
        
        while True:
            time.sleep(0.02)
            if not self.queene.empty():
                self.queene.get()
                self.info.setText("????????????...... ??????{0}".format(self.queene.qsize()))
            else:
                break
        
        for i in range(self.threads):
            thread = threading.Thread(target=self.subCalc)
            thread.setDaemon(True)
            thread.start()
        
#        seeds = self.getSeedListData()
        if seeds is not None and len(seeds) > 0:
            for group in range(self.minSeedsGroup, self.maxSeedsGroup + 1):
                posit = []
                for i in range(0,group):
                    posit.append(0)
                self.genMainSeeds(seeds, posit)
        
#        while True:
#            time.sleep(2)
#            if self.hasErrors:
#                return
#            if self.queene.empty() or self.password is not None:
#                self.startCalcBut.setText("????????????")
#                break
    
    def addToQueue(self, seed):
        self.queene.put(seed)
        if self.queene.qsize() >= 1000:
            time.sleep(5)
        
    
    def mainSeeds(self, seeds):
#        self.queene.put("".join(seeds))
        self.addToQueue("".join(seeds))
        for i in range(len(seeds)):
            if not self.isChar(seeds[i]):
                continue;
            if self.hasErrors:
                return
            seedsTmp = list("".join(seeds).lower())
            seedsTmp[i] = seedsTmp[i].upper()
#            self.queene.put("".join(seedsTmp))
            self.addToQueue("".join(seedsTmp))

            self.subSeeds(seedsTmp, i)
    
    """
         abcd abcD abCd abCD aBcd aBcD aBCd aBCD
         Abcd AbcD AbCd AbCD ABcd ABcD ABCd ABCD
    """
    def subSeeds(self, seeds, index):
        
        if self.hasErrors:
            return
        
        for i in range(0,index):
            if not self.isChar(seeds[i]):
                continue;
            s = list("".join(seeds[0:index]).lower() + "".join(seeds[index:]))
            s[i] = s[i].upper()
#            self.queene.put("".join(s))
            self.addToQueue("".join(s))
            self.subSeeds(s, i)

    def isChar(self, c):
        return c.isupper() or c.islower()
        
    def subCalc(self):
        while(True):
            
            if self.hasErrors:
                return
            
            if self.password is not None:
                raise SuccessException("Sucess")
#            print ("Queue Length: {0}" . format(self.queene.qsize()))

            passwd = self.queene.get()
            result = None
            try:
                result = self.callBitcoinByRpc('walletpassphrase', [passwd, 10])['error']
            except BaseException as be:
                self.hasErrors = True
                self.info.setText("??????????????????????????????")
                raise be
            if result is None:
                self.password = passwd
                self.passwordLabel.setText("??????: {0}".format(self.password))
                raise SuccessException("Sucess")
                #abCdefG_hijkl
            else:
                if self.password is None:
                    self.info.setText("????????????: {0} ????????????: {1}".format(passwd, self.queene.qsize()))
#            time.sleep(0.01)
#            print("---{0}---".format(passwd))
            
    def printInfo(self, info):
        self.info.setText(info)

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QMainWindow()
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec_()
    sys.exit(0)
