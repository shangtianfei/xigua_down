import base64
import json
import os
import re
import sys
# from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox
from PyQt5.QtCore import Qt
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from PyQt5.QtWidgets import QApplication,QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTabWidget
 
class MyGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('简单GUI示例')
        self.resize(1200, 600)

        main_layout = QVBoxLayout(self)
        input_layout = QHBoxLayout()

        self.url_input = QLineEdit(self)
        search_button = QPushButton('查找', self)
        search_button.clicked.connect(self.searchButtonClicked)
        self.url_input_value = ''

        input_layout.addWidget(self.url_input)
        input_layout.addWidget(search_button)

        # 创建QTabWidget作为主布局
        self.tab_widget = QTabWidget(self)

        # 创建查看和下载列表两个页签
        self.view_tab = QWidget(self)
        self.download_tab = QWidget(self)

        # 在页签上添加布局
        self.view_tab_layout = QVBoxLayout(self.view_tab)
        self.download_tab_layout = QVBoxLayout(self.download_tab)

        # 创建查看和下载列表两个表格
        self.view_table = QTableWidget(self)
        self.download_table = QTableWidget(self)

        # 初始化两个表格
        self.initTable(self.view_table)
        self.initTable(self.download_table,True)

        # 将表格添加到对应的页签布局中
        self.view_tab_layout.addWidget(self.view_table)
        self.download_tab_layout.addWidget(self.download_table)

        # 将页签添加到QTabWidget中
        self.tab_widget.addTab(self.view_tab, "查看")
        self.tab_widget.addTab(self.download_tab, "下载列表")

        page_layout = QHBoxLayout()
        prev_button = QPushButton('上一页', self)
        next_button = QPushButton('下一页', self)
        all_selected_button = QPushButton('全选/反选', self)
        download_button = QPushButton('下载选中', self)

        prev_button.clicked.connect(self.prevButtonClicked)
        next_button.clicked.connect(self.nextButtonClicked)
        all_selected_button.clicked.connect(self.headerCheckboxStateChanged)
        download_button.clicked.connect(self.downloadButtonClicked)

        page_layout.addWidget(prev_button)
        page_layout.addWidget(next_button)
        page_layout.addWidget(all_selected_button)
        page_layout.addWidget(download_button)

        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.tab_widget)  # 将QTabWidget添加到主布局中
        main_layout.addLayout(page_layout)

        self.simulated_data = []
        self.current_page = 1
        self.page_size = 30

    def initTable(self, table,download_table_flag=False):
        horizontalHeaderLabels = []
        if download_table_flag:
            horizontalHeaderLabels = ['ID', '标题', '发布时间', '状态']
        else:            
            horizontalHeaderLabels = ['复选框', 'ID', '标题', '发布时间', '状态']

        table.setColumnCount(len(horizontalHeaderLabels))
        table.setHorizontalHeaderLabels(horizontalHeaderLabels)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def generateSimulatedData(self):
        self.url_input_value = self.url_input.text()
        url = self.url_input_value
        if len(url) == 0:
            return

        util = Util()
        xigua_url = 'https://www.ixigua.com/'
        item_list = []
        if xigua_url in url:
            text = url.replace(xigua_url, '')
            if 'home' in text:
                item_list = util.item_list_page(text[5:21], (self.current_page-1) * self.page_size, self.page_size)
            else:
                item_list = util.xigua_title_by_id(text[:19])
        else:
            print('错误的url')
            return

        self.simulated_data = []
        for data in item_list:
            self.simulated_data.append((data['id'], data['title'], data['publish_time'], '查看'))

        self.updateTable(self.view_table)

    def updateTable(self, table,selected_rows=[]):
        for row, (id, title, publish_time, status) in enumerate(self.simulated_data):
            if len(selected_rows) > 0:
                table.setRowCount(len(selected_rows))
                if id in selected_rows:
                    table_index = row
                    table.setItem(table_index, 0, QTableWidgetItem(id))
                    table.setItem(table_index, 1, QTableWidgetItem(title))
                    table.setItem(table_index, 2, QTableWidgetItem(publish_time))
                    table.setItem(table_index, 3, QTableWidgetItem(status))
            else:
                table.setRowCount(len(self.simulated_data))
                checkbox = QCheckBox()
                table.setCellWidget(row, 0, checkbox)
                table.setItem(row, 1, QTableWidgetItem(id))
                table.setItem(row, 2, QTableWidgetItem(title))
                table.setItem(row, 3, QTableWidgetItem(publish_time))
                table.setItem(row, 4, QTableWidgetItem(status))     
        # 修改行号的显示文本，可以设置为您需要的任何文本
        for i in range(table.rowCount()):
            item = QTableWidgetItem(str(((self.current_page-1) * self.page_size) + i + 1))
            table.setVerticalHeaderItem(i, item)        

             

    def searchButtonClicked(self):
        self.current_page = 1
        self.generateSimulatedData()

    def prevButtonClicked(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.generateSimulatedData()

    def nextButtonClicked(self):
        self.current_page += 1
        self.generateSimulatedData()

    def downloadButtonClicked(self):
        selected_rows = []
        for row in range(self.view_table.rowCount()):
            checkbox = self.view_table.cellWidget(row, 0)
            if checkbox.isChecked():
                selected_data = [self.view_table.item(row, col).text() for col in range(1, 4)]
                selected_rows.append(selected_data[0])

        print("选中行的数据：", selected_rows)

        # 将选中的数据添加到下载列表表格中
        self.updateTable(self.download_table,selected_rows)

    def headerCheckboxStateChanged(self):
        for row in range(self.view_table.rowCount()):
            checkbox = self.view_table.cellWidget(row, 0)
            checkbox.setChecked(not checkbox.isChecked())

# 工具类
class Util:
    def __init__(self):
        print("Initializing...")


    def xigua_title_by_id(self,id):
        url = f"https://www.ixigua.com/{id}?wid_try=1"

        payload = {}
        headers = {
        'authority': 'www.ixigua.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'referer': f'https://www.ixigua.com/{id}',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Cookie': 'ixigua-a-s=0; support_avif=true; support_webp=true; xiguavideopcwebid=7320170644196492809; xiguavideopcwebid.sig=Hc-t8VdBrG3Na9D9VN55QRtiqTI'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        html_content = response.content.decode('utf-8')
        # 使用正则表达式匹配 <script[^>]*>(.*?)<\/script>
        pattern = re.compile(r'<script\s+data-react-helmet="true"[^>]*>(.*?)<\/script>', re.DOTALL)
        match = pattern.search(html_content)

        if match:
            json_content_str = match.group(1)
            json_content = json.loads(json_content_str)
            return [{'id':id,'title':json_content['name'],'publish_time':json_content['uploadDate']}]
        else:
            print("未找到匹配的部分")
            return []

    def xigua_download_list(ids):
        for id in ids:
            Util.xigua_download(id)

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
                                                        Util.file_download(filename,decoded_url)
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
                                            Util.file_download(filename,decoded_url)
                                            flag = 1
                                            break
                                    else:
                                        print("No main_url found.")
                                except json.JSONDecodeError as e:
                                    print("Error decoding JSON:", e)          




    def item_list_page(self,home_id,offset=0,limit=30):
        url = f"https://www.ixigua.com/api/videov2/author/new_video_list?to_user_id={home_id}&offset={offset}&limit={limit}"

        payload = {}
        headers = {
        'authority': 'www.ixigua.com',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98"',
        'accept': 'application/json, text/plain, */*',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.139 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': f'https://www.ixigua.com/user_playlist/{home_id}',
        'accept-language': 'zh-CN,zh;q=0.9',
        'Cookie': 'ixigua-a-s=0'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        json_data = json.loads(response.text)
        videoList = json_data['data']['videoList']
        item_list = [{'id':x['gid'],'title':x['title'],'publish_time': datetime.utcfromtimestamp( x['publish_time']).strftime("%Y-%m-%d %H:%M:%S")} for x in videoList]
        return item_list                    

    def file_download(filename,url):
        os.makedirs('download', exist_ok=True)
        response = requests.get(url, stream=True, timeout=30)

        with open(os.path.join('download',filename), 'wb') as file:
            for chunk in response.iter_content(chunk_size=1*1024*1024):
                file.write(chunk)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_gui = MyGUI()
    my_gui.show()
    sys.exit(app.exec_())
