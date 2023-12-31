import sys 
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import datetime


import class_hogaData as StockClass
import f_getls as getls


class MyWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("주식호가잔량")
        # self.setGeometry(300, 300, 300, 400)
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.ocx.OnEventConnect.connect(self.connect)
        self.ocx.OnReceiveRealData.connect(self._handler_real_data)
        # 2초 후에 로그인 진행
        QTimer.singleShot(1000 * 2, self.CommmConnect)
        self.code = "005930"
        self.codels = getls.getList()#코스피200중 가격 낮은 종목 리스트 가져오기
        print(self.codels)
        self.stockls = []


    def connect(self):
        self.SetRealReg("1000", self.codels, "41", 0)

    def CommmConnect(self):
        self.ocx.dynamicCall("CommConnect()")
        self.statusBar().showMessage("login 중 ...")



    def _handler_real_data(self, codels, real_type, data):
        # for i in range(10):
        #     self.buyamount.append(self.GetCommRealData(code,61+i))
        # print(self.buyamount)


        self.stockls.clear()


        for i in codels:
            print("code1",i)
            # temp = StockClass.StockData(i,[],[],[],[])
            # for a in range(10):
            #     temp.sellamount.append(self.GetCommRealData(i,41+a))
            #     temp.sellprice.append( self.GetCommRealData(i, 61+a))
            #     temp.buyamount.append(self.GetCommRealData(i,51+a))
            #     temp.buyprice.append(self.GetCommRealData(i, 71+a))
            # self.stockls.append(temp)
        print(self.stockls)
        print("\n\n")







    def SetRealReg(self, screen_no, code_list, fid_list, real_type):
        self.ocx.dynamicCall("SetRealReg(QString, QString, QString, QString)", 
                              screen_no, code_list, fid_list, real_type)
        self.statusBar().showMessage("구독 신청 완료")

    def DisConnectRealData(self, screen_no):
        self.ocx.dynamicCall("DisConnectRealData(QString)", screen_no)
        self.statusBar().showMessage("구독 해지 완료")

    def GetCommRealData(self, code, fid):
        data = self.ocx.dynamicCall("GetCommRealData(QString, int)", code, fid) 
        return data

    def __del__(self):
        self.DisConnectRealData("1000")     

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()