from wsgiref.simple_server import make_server
from urllib import parse
import json,base64,requests

class Pympq(object):
    def __init__(self):
        self.Mpq_index=0
        self.Port = ""       #监听的服务端口，范围为 8010-8020
        self.Pid=""          #进程ID
        self.Ver = ""        #框架版本
        self.MsgID = ""      #信息序号
        self.Robot = ""      #机器人QQ
        self.MsgType = ""    #信息类型
        self.MsgSubType = "" #信息子类型，默认 0
        self.Source = ""     #信息来源
        self.Sender = ""     #主动触发对象
        self.Receiver = ""   #被动接收对象
        self.Content = ""    #正文内容，需要 base64解码
        self.OrigMsg = ""    #原始数据，需要 base64解码
        '''{
            "Port":"8010",                    //监听的服务端口，范围为 8010-8020
            "Pid":"14880",                    //进程ID
            "Ver":"MyPCQQ Ver20170721",       //框架版本
            "MsgID":"40",                     //信息序号
            "Robot":"3509945636",             //机器人QQ
            "MsgType":"1",                    //信息类型
            "MsgSubType":"0",                 //信息子类型，默认 0
            "Source":"445491251",             //信息来源
            "Sender":"445491251",             //主动触发对象
            "Receiver":"3509945636",          //被动接收对象
            "Content":"5ZWq5ZWq5ZWq",         //正文内容，需要 base64解码
            "OrigMsg":""                      //原始数据，需要 base64解码
        ｝'''
    def Error(self,json_str):
        json_content = json.loads(json_str)  # 字典格式化
        code = json_content["Code"]
        if (code == "0"):
            return True
        elif (code == "-1"):
            print("调度过程中发生了读写异常")
            return False
        elif (code == "-2"):
            print("找不到响应的机器人QQ")
            return False
        elif (code == "-3"):
            print("POST的API参数为空或解析失败")
            return False
        elif (code == "-4"):
            print("API不存在")
            return False
        elif (code == "-5"):
            print("API参数格式错误")
            return False
        elif (code == "-6"):
            print("API最多支持15个参数")
            return False
        else:
            print("unknow err")
            return False
        return False
    def index(self,environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        if(environ.get("REQUEST_METHOD")=="GET"):
            return [b"<h1>It's GET</h1>"]
        elif(environ.get("REQUEST_METHOD")=="POST"):
            request_body = environ["wsgi.input"].read(int(environ.get("CONTENT_LENGTH", 0)))#获取聊天信息
            html=str(request_body,'utf-8') #将以字节为单位的bytes转化为python unicode编码
            m_info = self.Mpq_main(html)
        return [b"<h1>It's POST</h1>"]
    def Mpq_main(self,environ):
        json_content = json.loads(environ)  # 字典格式化
        if (self.Mpq_index == 0):
            self.Port = json_content['Port']            # 监听的服务端口，范围为 8010-8020
            self.Pid = json_content['Pid']              # 进程ID
            self.Ver = json_content['Ver']              # 框架版本
            self.MsgID = json_content['MsgID']          # 信息序号
            self.Robot = json_content['Robot']          # 机器人QQ
            self.MsgType = json_content['MsgType']      # 信息类型
            self.MsgSubType = json_content['MsgSubType']# 信息子类型，默认 0
            self.Source = json_content['Source']        # 信息来源
            self.Sender = json_content['Sender']        # 主动触发对象
            self.Receiver = json_content['Receiver']    # 被动接收对象
            self.Content = self.Mpq_base64_decode(json_content['Content'])      # 正文内容，需要 base64解码
            self.OrigMsg = json_content['OrigMsg']      # 原始内容，需要 base64解码
            self.Mpq_index = 1
        else:
            self.Robot = json_content['Robot']          # 机器人QQ
            self.MsgType = json_content['MsgType']      # 信息类型
            self.Source = json_content['Source']        # 信息来源
            self.Sender = json_content['Sender']        # 主动触发对象
            self.Receiver = json_content['Receiver']    # 被动接收对象
            self.Content = self.Mpq_base64_decode(json_content['Content'])      # 正文内容，需要 base64解码

        if (self.MsgType == "1"):
            print('Robot：', self.Robot)  # 调试输出 机器人QQ
            print('MsgType：', self.MsgType)  # 调试输出 信息类型
            print('Source：', self.Source)  # 调试输出 信息来源
            print("Sender：", self.Sender)  # 调试输出 主动触发对象
            print("Receiver：", self.Receiver)  # 调试输出 被动接收对象
            print("来自好友的消息：", self.Content)  # 调试输出 解码后的信息正文

        elif (self.MsgType == "2" and self.Source == "564"):
            print('Robot：', self.Robot)  # 调试输出 机器人QQ
            print('MsgType：', self.MsgType)  # 调试输出 信息类型
            print('Source：', self.Source)  # 调试输出 信息来源
            print("Sender：", self.Sender)  # 调试输出 主动触发对象
            print("Receiver：", self.Receiver)  # 调试输出 被动接收对象
            print("来自群友的消息：", self.Content)  # 调试输出 解码后的信息正文
            if (self.Content == "测试回复"):
                self.Mpq_Sendmsg(self.Robot, self.Source, self.Sender, "测试信息666")
        else:
            self.Mpq_msgtype(self.MsgType)
        self.Mpq_ret("0")
    def Mpq_base64_decode(self,str):
        return base64.b64decode(str).decode()
    def Mpq_ret(self,ret,msg=None):
        """{
            "Ret": "10", // 返回值，10 = 默认确定\同意，20 = 默认取消\拒绝
            "Msg": "" // 返回信息，用于处理拒绝加群拒绝加好友的理由回传
            }"""
        txt = {'Ret': '{}', 'Msg': '{}'}
        txt['Ret'] = ret
        txt['Msg'] = msg
        return (txt)
    def Mpq_msgtype(self,Msgtype):
        if (Msgtype == "2009" and self.Source == "564"):
            print('Robot：', self.Robot)  # 调试输出 机器人QQ
            print('MsgType：', self.MsgType)  # 调试输出 信息类型
            print('Source：', self.Source)  # 调试输出 信息来源
            print("Sender：", self.Sender)  # 调试输出 主动触发对象
            print("Receiver：", self.Receiver)  # 调试输出 被动接收对象
            print(self.Sender," 成为管理员~")  # 调试输出
            self.Mpq_Sendmsg(self.Robot, self.Source, self.Sender, "[name]和群主达成了不可告人的交易成为了本群管理员~~")
        elif(Msgtype == "2010" and self.Source == "564"):
            print('Robot：', self.Robot)  # 调试输出 机器人QQ
            print('MsgType：', self.MsgType)  # 调试输出 信息类型
            print('Source：', self.Source)  # 调试输出 信息来源
            print("Sender：", self.Sender)  # 调试输出 主动触发对象
            print("Receiver：", self.Receiver)  # 调试输出 被动接收对象
            print(self.Sender," 取消管理员权限~")  # 调试输出
            self.Mpq_Sendmsg(self.Robot, self.Source, self.Sender, "[name]和群主交易达成失败，被取消管理员权限~")
        else:
            print()
    def Mpq_Sendmsg(self,Robotqq,Source,Sender,text):
        get_text = "/?QQ=" + Robotqq + "&API="
        api_text = parse.quote("Api_SendMsg({},2,0,{},{},{})".format("'" + Robotqq + "'",
                                                                 "'" + Source + "'",
                                                                 "'" + Sender + "'",
                                                                 "'"+text+"'"))
        tt = requests.get("http://127.0.0.1:8010" + get_text + api_text)
        return self.Error(tt.text)
    def start(self):
        port=900
        httpd = make_server('', port, self.index)
        httpd.serve_forever()


if __name__ == '__main__':
 MPQ=  Pympq()
 MPQ.start()
