# coding:utf-8
import os
import re
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QCompleter
import json
import base64
import requests
from bs4 import BeautifulSoup
from qfluentwidgets import  PushButton, SearchLineEdit
from PyQt5.QtGui import QIcon



class Demo(QWidget):

    def __init__(self):
        super().__init__()
        # self.setStyleSheet("Demo {background: rgb(32, 32, 32)}")
        # setTheme(Theme.DARK)
        self.setWindowTitle("西瓜down@shangtianfei")  # 将窗口标题更改为 "666"

        # 设置窗口图标
        # icon = QIcon('icon.png')
        # self.setWindowIcon(icon)


        self.hBoxLayout = QHBoxLayout(self)
        self.lineEdit = SearchLineEdit(self)
        self.button = PushButton('下载', self)

        # add completer
        stands = [
            "Star Platinum", "Hierophant Green",
            "Made in Haven", "King Crimson",
            "Silver Chariot", "Crazy diamond",
            "Metallica", "Another One Bites The Dust",
            "Heaven's Door", "Killer Queen",
            "The Grateful Dead", "Stone Free",
            "The World", "Sticky Fingers",
            "Ozone Baby", "Love Love Deluxe",
            "Hermit Purple", "Gold Experience",
            "King Nothing", "Paper Moon King",
            "Scary Monster", "Mandom",
            "20th Century Boy", "Tusk Act 4",
            "Ball Breaker", "Sex Pistols",
            "D4C • Love Train", "Born This Way",
            "SOFT & WET", "Paisley Park",
            "Wonder of U", "Walking Heart",
            "Cream Starter", "November Rain",
            "Smooth Operators", "The Matte Kudasai"
        ]
        self.completer = QCompleter(stands, self.lineEdit)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setMaxVisibleItems(10)
        self.lineEdit.setCompleter(self.completer)

        self.resize(800, 300)
        self.hBoxLayout.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.lineEdit, 0, Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.button, 0, Qt.AlignCenter)

        self.lineEdit.setFixedSize(600, 33)
        self.lineEdit.setClearButtonEnabled(True)
        self.lineEdit.setPlaceholderText('输入西瓜链接')
        self.button.pressed.connect(self._textChanged)

    def _textChanged(self):
        text = self.lineEdit.text()
        if len(self.lineEdit.text()) > 0:
            match = re.search(r'\d+', text)
            if match:
                video_id = match.group()
                self.xigua_download(video_id)

    

    def xigua_download(self,id):
        # 指定目标URL
        url = "https://www.ixigua.com/" + id +'?wid_try=1'  #这里可以自行添加User-Agent和cookie

        # 发送HTTP请求获取URL内容
        flag = 0
        is_hevc = 0 
        out_q = 0
        while flag == 0 :
                while 1 :
                    try:
                        response = requests.get(url)
                        break
                    except ConnectionError as e:
                        continue

                content = response.content.decode('utf-8')
                if content.find("video_5") != -1:
                    if out_q == 0 :
                        out_q = 1   
                        print("4K")
                    video_parts = content.split("video_5")
                else :
                    if content.find("video_4") != -1 :
                        if out_q == 0 :
                            out_q = 1 
                            print("1080P")
                        video_parts = content.split("video_4")
                    else :
                        if content.find("video_3") != -1 :
                            if out_q == 0 :
                                out_q = 1 
                                print("720P")
                            video_parts = content.split("video_3")
                        else :
                            if content.find("video_2") != -1 :
                                if out_q == 0 :
                                    out_q = 1 
                                    print("480P")
                                video_parts = content.split("video_2")
                            else :
                                if out_q == 0 :
                                    out_q = 1 
                                    print("360P")
                                video_parts = content.split("video_1")

                
                for part in video_parts[1:]:
                    brace_count = 0
                    json_content = ""
                    
                    for char in part:
                        if char == "{":
                            brace_count += 1
                        elif char == "}":
                            brace_count -= 1
                            if brace_count == 0:
                                json_content =  json_content + char
                                break
                        if brace_count > 0:
                            json_content += char

                    if json_content:
                        try:
                            data = json.loads(json_content)
                            # 检查是否有 "codec_type" 为 "bytevc1" 的对象
                            if "codec_type" in data and data["codec_type"] == "bytevc1":
                                    main_url = data.get("main_url")
                                    if main_url:
                                            # 解码 main_url 的值并输出
                                            decoded_url = base64.b64decode(main_url).decode('utf-8')
                                            test = requests.head(decoded_url)
                                            is_hevc = 1
                                            if test.status_code == 200:
                                                    soup = BeautifulSoup(content, 'html.parser')
                                                    title = soup.title.string.strip()
                                                    filename = f'{title}.mp4'
                                                    self.file_download(filename,decoded_url)
                                                    flag = 1
                                                    break
                                    else:
                                        print("No main_url found.")
                        except json.JSONDecodeError as e:
                            print("Error decoding JSON:", e)              
                if is_hevc == 0 :
                    for part in video_parts[1:]:
                        brace_count = 0
                        json_content = ""
                    
                        for char in part:
                            if char == "{":
                                brace_count += 1
                            elif char == "}":
                                brace_count -= 1
                                if brace_count == 0:
                                    json_content =  json_content + char
                                    break
                            if brace_count > 0:
                                json_content += char
                        if json_content:
                            try:
                                data = json.loads(json_content)
                                main_url = data.get("main_url")
                                if main_url:     
                                    # 解码 main_url 的值并输出
                                    decoded_url = base64.b64decode(main_url).decode('utf-8')
                                    test = requests.head(decoded_url)
                                    if test.status_code == 200:
                                        soup = BeautifulSoup(content, 'html.parser')
                                        title = soup.title.string.strip()
                                        filename = f"{title}.mp4"
                                        self.file_download(filename,decoded_url)
                                        flag = 1
                                        break
                                else:
                                    print("No main_url found.")
                            except json.JSONDecodeError as e:
                                print("Error decoding JSON:", e)          

    def file_download(self,filename,url):
        response = requests.get(url)
        response.raise_for_status()
        os.makedirs('download', exist_ok=True)
        with open(os.path.join('download',filename), 'wb') as file:
            file.write(response.content)
        print(f"{filename}下载成功")


        


if __name__ == '__main__':
    # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = Demo()
    w.show()
    app.exec_()