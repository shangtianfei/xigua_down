from asyncio import Event
import base64
import json
import os
import re
import sys
import threading
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
import webbrowser
import requests
from datetime import datetime
from PyQt5.QtWidgets import QApplication,QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTabWidget
from PyQt5.QtCore import Qt
from network import FactoryBean

from util import Util

# 全局唯一
the_one_dict = {}

NEW_APP_VERSION = None
THIS_APP_VERSION = 'v1.3.0' 

class MyGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
            # 加载版本信息
        util =  Util()
        NEW_APP_VERSION = util.new_version()

        self.setWindowTitle('西瓜视频下载@tt')
        self.resize(1400, 600)

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
        about_button = QPushButton(('关于' if THIS_APP_VERSION==NEW_APP_VERSION else '点击更新'), self)
        prev_button = QPushButton('上一页', self)
        next_button = QPushButton('下一页', self)
        all_selected_button = QPushButton('全选/反选', self)
        download_button = QPushButton('下载选中', self)

        about_button.clicked.connect(self.openGit)
        prev_button.clicked.connect(self.prevButtonClicked)
        next_button.clicked.connect(self.nextButtonClicked)
        all_selected_button.clicked.connect(self.headerCheckboxStateChanged)
        download_button.clicked.connect(self.downloadButtonClicked)

        page_layout.addWidget(about_button)
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
    
    def openGit(self):
            # 在点击按钮时，打开默认浏览器并跳转到百度
            webbrowser.open('https://gitee.com/mijin/xigua_down/releases')

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

        factory = FactoryBean().factory_bean(self.url_input_value)
        if factory == None:
            print("无法解析的url")
            return

        item_list = factory.handler(url,(self.current_page-1) * self.page_size, self.page_size)
        if len(item_list) == 0:
            print("没有获取到具体信息")
            return
        
        # 获取字典中最大的键，如果字典为空则默认为1
        max_key =  max(the_one_dict.keys(), default='1')

        self.simulated_data = []
        for index,data in enumerate(item_list) :
            id = int(max_key) + index 
            self.simulated_data.append(( str(id).zfill(5), data['title'], data['publish_time'], '查看'))
            the_one_dict[str(id).zfill(5)] = data

        self.updateTable(self.view_table)

    def updateTable(self, table,selected_rows=[]):
        ids = []
        if len(selected_rows) > 0:
            table_count = table.rowCount()
            local_ids = [table.item(index, 0).text() for index in range(table_count) if table.item(index, 0).text() in selected_rows]
            ids = list(set(selected_rows) - set(local_ids))
            video_array = []
            if len(ids) == 0:
                print('没有新增的数据')
                return
            else:
                for index,id in enumerate(ids):
                    table.setRowCount(len(ids) + table_count -1)
                    table_index = index  + table_count
                    desired_object = next(obj for obj in self.simulated_data if obj[0] == id)
                    id = desired_object[0]
                    title  = desired_object[1]
                    publish_time = desired_object[2]
                    status = '等待中'

                    table.insertRow(table_index)
                    table.setItem(table_index, 0, QTableWidgetItem(id))
                    table.setItem(table_index, 1, QTableWidgetItem(title))
                    table.setItem(table_index, 2, QTableWidgetItem(publish_time))
                    table.setItem(table_index, 3, QTableWidgetItem(status))
                    video_array.append({'id':id,'title':title,'url':the_one_dict[id]['url']})
                if len(video_array) > 0:
                    threading.Thread(target=self.xigua_download_list, args=(video_array,)).start()
        else:
            for row, (id, title, publish_time, status) in enumerate(self.simulated_data):
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



    def xigua_download_list(self,video_array):
        base_path = 'download'
        for video_data in video_array:
            id = video_data['id']

            factoryBean =  FactoryBean()
            factory = factoryBean.factory_bean(self.url_input_value)
            url =  factory.download_url(video_data['url'])

            filename =  f"{video_data['title']}.mp4"
            source_path = os.path.join(base_path,id)
            target_path = os.path.join(base_path,filename)

            if os.path.exists(target_path):
                print(f"{target_path}已下载，不重复下载")
                self.updateStatus(id,f"已下载，不重复下载")
                break

            factory = FactoryBean().factory_bean(self.url_input_value)
            # 使用
 
            def listener(arg):
                print(f"监听到事件，参数是 {arg}")

            factory.subscribe(listener)
            factory.trigger("测试")

            os.makedirs(base_path, exist_ok=True)
            response = requests.get(url, stream=True, timeout=500)

            to_do_count = 0
            with open(source_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=2*1024*1024):
                    file.write(chunk)
                    to_do_count = to_do_count + len(chunk)
                    self.updateStatus(id,f"已下载{to_do_count/1024/1024}MB")
                    print(f"已下载{to_do_count/1024/1024}MB")
            os.rename(source_path,target_path)
            self.updateStatus(id,f"下载完成")




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

    def updateStatus(self, id_to_update, new_status):
        # 根据ID修改相应行的状态列文字
        # 遍历表格，查找匹配的ID并更新状态列
        for row in range(self.download_table.rowCount()):
            current_id = (self.download_table.item(row, 0).text())
            if current_id == id_to_update:
                self.download_table.setItem(row, 3, QTableWidgetItem(new_status))
                break


                



if __name__ == '__main__':


    app = QApplication(sys.argv)
    my_gui = MyGUI()
    my_gui.show()
    sys.exit(app.exec_())
