import sys 
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import datetime



import f_getls as getls
import f_logic_fin as logic


from pykiwoom.kiwoom import *






class Hoga(QMainWindow):
     #생성자()-----------------------
    def __init__(self):
        super().__init__()
        self.setWindowTitle("주식호가잔량")
        # self.setGeometry(300, 300, 300, 400)
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.ocx.OnEventConnect.connect(self.connect)
        self.ocx.OnReceiveRealData.connect(self._handler_real_data)
        QTimer.singleShot(1000 * 2, self.CommmConnect)



        #거래용 인스턴스 생성
        #연결
        self.kiwoom=Kiwoom()
        self.kiwoom.CommConnect(block=True)
        self.state = self.kiwoom.GetConnectState()
        self.account = self.kiwoom.GetLoginInfo("ACCNO")[0]#내 계좌 중 2번째 계좌  불러오기
        if(self.state==0):
            print("연결안됨")
        elif self.state==1:
            print("연결완료")



         #변수선언
        self.stocks=[]#  [   [종목코드, [호가잔량],[호가] ]    ,
        self.tradingstocks = [] #[[종목명,기대주가,당시시가(중간가격)]]
        


        #거래할 종목들 코드리스트 받아오기
        #zero
        self.codes = getls.getList2()       
        

    #실시간 실행 함수-------------------
    def _handler_real_data(self,code,real_type,data):
        print("handler")

        if self.real_type == "주식우선호가":
            while(True):
                self.first_get_hoga()#self.stocks 초기화
                if(self.stocks[0][1][0] != ''):
                    self.second_get_future_price()
                    #third#------


                else:
                    print("market not opened yet")







#순서도 대로 기능 정리한 함수들-------------------------------------------------------------------------------------
    def first_get_hoga(self):
        self.stocks.clear()
        for each in self.codes:
            self.stocks.append(self.get_each_stock_data(each))
        print(self.stocks)

    def second_get_future_price(self):
        self.tradingstocks.clear()
        for each_stock in self.stocks: #[   [종목코드, [호가잔량],[호가] ]    ,[종목코드, [호가잔량],[호가]].. ]
            temp = []
            expec_price_index = logic.calc_assumePriceIndex(each_stock[1])
            if expec_price_index == 0 : continue#수익 리턴이 0이 나오면 제끼기
            middle_price = each_stock[2][int(len(each_stock[2])/2)]
            expec_price = each_stock[2][expec_price_index]
            temp.append(each_stock[0])
            temp.append(expec_price)
            temp.append(middle_price)
            self.tradingstocks.append(temp)
        #print(self.tradingstocks)


    def third_order(self): 
        #self.stocks[   [종목코드, [호가잔량],[호가] ]    ,
        #self.tradingstocks#[[종목명,기대주가,당시시가(중간가격)]]

        pass


    #기능함수 1 : 입력 코드에 해당하는 종목의 호가 데이터 가져오기-----------
    def get_each_stock_data(self,code):
        rsult = []
        temp_amount = []
        temp_price=[]
        for i in reversed(range(10)):
            temp_amount.append(self.GetCommRealData(code,71+i))
            temp_price.append(self.GetCommRealData(code,51+i))
        for i in range(10):
            temp_amount.append(self.GetCommRealData(code,61+i))
            temp_price.append(self.GetCommRealData(code,41+i))
        rsult.append(code)
        rsult.append(temp_amount)
        rsult.append(temp_price)
        return rsult
        #[종목명, [호가잔량리스트], [호가리스트]]




    def get_currPrice(self,code):#현재가 가져오기
        return  self.GetCommRealData(code, 10)


    #매수
    def buy(self,StockCode, Qty, Price):
        self.kiwoom.SendOrder("","0000",self.account, 1,StockCode,Qty,Price,'00',"")#주문이름,화면명,계좌번호,주문유형(1매수2매도3매수취소4매도취소5매수정정6매도정정),주식종목코드,주문수량,주문단가,'00':지정가'03':시장가,원주문번호로 주문 정정시 사용. 디폴트 : ""   
    #매도
    def sell(self,StockCode, Qty, Price):
        self.kiwoom.SendOrder("","0000",self.account, 2,StockCode,Qty,Price,'00',"")








#기타 필요한 함수들------------------------------------
    def connect(self):
        strarr = ""
        for each in self.codes:
            strarr += each+";"
        strarr = strarr[:-1]
        self.SetRealReg("1000",strarr, "41", 0)

    def CommmConnect(self):
        self.ocx.dynamicCall("CommConnect()")
        self.statusBar().showMessage("login 중 ...")

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
    window = Hoga()
    window.show()
    app.exec_()


