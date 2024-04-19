import base64
import json
import math
import os
import re
import sys
import threading
import time
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
import webbrowser
import requests
from datetime import datetime
from PyQt5.QtWidgets import QApplication,QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTabWidget,QComboBox  
from PyQt5.QtCore import Qt
import logging  
  
# 配置日志记录器  
logging.basicConfig(filename='xigua.log', level=logging.INFO, encoding='UTF-8', 
                    format='%(asctime)s:%(levelname)s:%(message)s')
 
# 全局唯一
the_one_dict = {}
download_ids = []

NEW_APP_VERSION = None
THIS_APP_VERSION = 'v1.4.3' 

class MyGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
            # 加载版本信息
        util =  Util()
        NEW_APP_VERSION = util.new_version()

        self.setWindowTitle(f'西瓜视频下载@tt@{THIS_APP_VERSION}        qq:232400689')
        self.resize(1400, 600)

        main_layout = QVBoxLayout(self)
 
        input_layout = QHBoxLayout()

        self.url_input = QLineEdit(self)
        search_button = QPushButton('查找', self)
        search_button.clicked.connect(self.searchButtonClicked)
        self.url_input_value = ''
                        # 创建一个 QComboBox 并添加选项  
        combo_box = QComboBox()  
        combo_box.addItem('视频')  
        # combo_box.addItem('小视频')  

        input_layout.addWidget(self.url_input)
        input_layout.addWidget(combo_box)
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
            horizontalHeaderLabels = ['ID', '标题', '发布时间','清晰度', '状态']
        else:            
            horizontalHeaderLabels = ['复选框', 'ID', '标题', '发布时间','清晰度', '状态']

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
            logging.info('错误的url')
            return
        
        self.simulated_data = []
        for index,data in enumerate(item_list) :
            index_str = str(index + 1).zfill(4)
            id = f"{data['id'].zfill(5)}_{index_str}"[-10:]
            self.simulated_data.append((id, data['title'], data['publish_time'],data['definition_list'], '查看'))
            the_one_dict[id] = data

        self.updateTable(self.view_table)

    def updateTable(self, table,selected_rows=[]):
        ids = []
        if len(selected_rows) > 0:
            table_count = table.rowCount()
            ids = list(set( [ item['id']  for item in  selected_rows]) - set(download_ids))
            video_array = []
            if len(ids) == 0:
                logging.info('没有新增的数据')
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

                    p = next(obj['p'] for obj in selected_rows if obj['id'] == id)
                    table.insertRow(table_index)
                    table.setItem(table_index, 0, QTableWidgetItem(id))
                    table.setItem(table_index, 1, QTableWidgetItem(title))
                    table.setItem(table_index, 2, QTableWidgetItem(publish_time))
                    table.setItem(table_index, 3, QTableWidgetItem(p))
                    table.setItem(table_index, 4, QTableWidgetItem(status))
                    download_ids.append(id)
                    video_array.append({'id':id,'title':title,'url':the_one_dict[id]['url'],'p':p})
                if len(video_array) > 0:
                    threading.Thread(target=self.xigua_download_list, args=(video_array,)).start()
        else:
            for row, (id, title, publish_time,definition_list, status) in enumerate(self.simulated_data):
                table.setRowCount(len(self.simulated_data))
                checkbox = QCheckBox()
                table.setCellWidget(row, 0, checkbox)
                table.setItem(row, 1, QTableWidgetItem(id))
                table.setItem(row, 2, QTableWidgetItem(title))
                table.setItem(row, 3, QTableWidgetItem(publish_time))
                sorted_videos = sorted(definition_list, key=lambda item: int(item.rstrip('p')), reverse=True)  

                # 创建一个 QComboBox 并添加选项  
                combo_box = QComboBox()  
                for definition in sorted_videos:
                 combo_box.addItem(definition)  
                 
                
                # 将自定义的 QWidget 设置为特定单元格的内容  
                table.setCellWidget(row, 4, combo_box)  # 在第一行第五列设置自定义内容  
                table.setItem(row, 5, QTableWidgetItem(status))     

        # 修改行号的显示文本，可以设置为您需要的任何文本
        for i in range(table.rowCount()):
            item = QTableWidgetItem(str(((self.current_page-1) * self.page_size) + i + 1))
            table.setVerticalHeaderItem(i, item)   



    def xigua_download_list(self,video_array):
        util = Util()
        base_path = 'download'
        for video_data in video_array:
            id = video_data['id']
            video_data_target =  util.xigua_download(video_data)
            url = video_data_target['main_url']
            filename =  f"{video_data['title']}.{video_data['p']}.mp4"
            source_path = os.path.join(base_path,id)
            target_path = os.path.join(base_path,filename)

            if os.path.exists(target_path):
                logging.info(f"{target_path}已下载，不重复下载")
                self.updateStatus(id,f"已下载，不重复下载")
                continue


            os.makedirs(base_path, exist_ok=True)
            # response = requests.get(url, stream=True, timeout=500,headers=headers)
            total_size = video_data_target['size']
            logging.info('调用下载')
            flag =  self.download_video(url,target_path,total_size,id)
            if flag:
                self.updateStatus(id,f"下载完成")
            else:
                self.updateStatus(id,f"下载异常")

            logging.info('任务完成')

            # os.rename(source_path,target_path)


    def download_video_part(self,url, start_byte, end_byte, part_filename,total_size,output_filename):  
        headers = {
            'authority': 'v9-p-xg-web-pc.ixigua.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98"',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.139 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
            'accept': '*/*',
            'origin': 'https://www.ixigua.com',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.ixigua.com/',
            'accept-language': 'zh-CN,zh;q=0.9',
            'range': f'bytes={start_byte}-{end_byte}'
            } 
        
        response = self.send_request_with_retry(url,headers)  

        if response == None:
            logging.info(f"多次重试下载失败")  
            return False
        
        if response.status_code == 206:  
            with open(part_filename, 'wb') as f:  
                for chunk in response.iter_content(1024):  
                    if chunk:  
                        f.write(chunk)  
            logging.info(f"视频 {output_filename} {round((end_byte/total_size) * 100, 2)}%")  
            return True
        else:  
            logging.info(f"下载部分失败，状态码: {response.status_code}")  
            return False
  

    def send_request_with_retry(self,url,headers, retries=10, backoff_factor=0.3):  
        for attempt in range(retries):  
            try:  
                response = requests.get(url, headers=headers, stream=True)  
                response.raise_for_status()  # 如果响应状态码不是 200，则抛出 HTTPError 异常  
                return response  
            except (requests.RequestException, requests.HTTPError) as e:  
                logging.info(f"Request failed: {e}, retrying... ({attempt + 1}/{retries})")  
                time.sleep(backoff_factor * (2 ** attempt))  # 指数退避策略  
        logging.info("Max retries exceeded with url: %s" % url)  
        return None  

    def download_video(self,url, output_filename,total_size,id):  
        # 记录开始时间  
        start_time = time.time()  
        # 
        logging.info('发起一个HEAD请求来获取视频的总大小')
        head_response = requests.head(url)  
        logging.info(f'HEAD请求 head_response.status_code = {head_response.status_code}')
        if head_response.status_code != 200:  
            part_size = 1024 * 1024 # 1MB per part  
            
            # 计算需要下载的部分数量  
            num_parts = (total_size + part_size - 1) // part_size  
            
            # 创建临时目录来保存部分文件  
            temp_dir = f'/download/{id}'  
            if not os.path.exists(temp_dir):  
                os.makedirs(temp_dir)  
            
            # 下载视频的每个部分  
            for part_num in range(num_parts):  
                start_byte = part_num * part_size  
                end_byte = min(start_byte + part_size - 1, total_size - 1)  
                part_filename = os.path.join(temp_dir, f"video_part_{part_num}.mp4")  
                percentage = round((end_byte/total_size) * 100, 2)
                self.download_video_part(url, start_byte, end_byte, part_filename,total_size,output_filename)  
                self.updateStatus(id,f"已下载 {percentage}%")

            
            # 合并所有部分文件为一个完整的视频文件  
            with open(output_filename, 'wb') as outfile:  
                for part_num in range(num_parts):  
                    part_filename = os.path.join(temp_dir, f"video_part_{part_num}.mp4")  
                    with open(part_filename, 'rb') as partfile:  
                        outfile.write(partfile.read())  
                    # 删除已合并的部分文件以释放空间  
                    os.remove(part_filename)  
            
            # 删除临时目录（如果它是空的）  
            try:  
                os.rmdir(temp_dir)  
            except OSError:  
                pass  # 目录可能不空，忽略错误  
            # 记录结束时间  
            end_time = time.time()  
            
            # 计算并打印耗时  
            elapsed_time = end_time - start_time  

            logging.info(f"视频下载完成: {output_filename} 耗时约 {elapsed_time:.2f} 秒")  
            return True
        else:
            logging.info(f"请求视频size异常 url={url}")  
            return False



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
                selected_p_data = self.view_table.cellWidget(row, 4).currentText()
                selected_rows.append({'id':selected_data[0],'p':selected_p_data})

        logging.info("选中行的数据：", selected_rows)

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
                self.download_table.setItem(row, 4, QTableWidgetItem(new_status))
                break

# 工具类
class Util:
    def __init__(self):
        logging.info("Initializing...")


    # 存在两种情况，分别是有多P电视剧 和 没有多P
    # url = "https://www.ixigua.com/6719270659400155659?wid_try=1"
    # url = "https://www.ixigua.com/7322803456891486730?wid_try=1"
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
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        html_content = response.content.decode('utf-8')
        # 使用正则表达式匹配 <script[^>]*>(.*?)<\/script>
        pattern = re.compile(r'<script\s+id=".*?"\s*nonce=".*?">\s*window\._SSR_HYDRATED_DATA=(.*?)</script>', re.DOTALL)
        match = pattern.search(html_content)



        if match:
            json_content_str = match.group(1)
            # logging.info(json_content_str)
            output_string = json_content_str.replace('undefined', '{}')

            json_content = json.loads(output_string)
            video_list =  self.search_key_in_json(json_content,'video_list')
            definition_list = [x.get('definition', 'No definition provided') for x in video_list.values()]
            packerData = json_content['anyVideo']['gidInformation']['packerData']
            res = []
            # 判断键是否存在
            if 'episodeInfo' in packerData:
                episodeId = packerData['episodeInfo']['episodeId']
                url = f"https://www.ixigua.com/api/albumv2/details?albumId={id}&episodeId={episodeId}"

                payload = {}
                headers = {
                'authority': 'www.ixigua.com',
                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98"',
                'accept': 'application/json, text/plain, */*',
                'x-secsdk-csrf-token': '00010000000144d196a4207c356efe00325751746b756de113d5a8c47b39f9a5ac3dd3e2d9ff17aa79f74140abee',
                'sec-ch-ua-mobile': '?0',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.139 Safari/537.36',
                'tt-anti-token': 'NBZOII0rrA-b6c8c769ecfc773ae57f8403048234c51a5a9224a4d7e3bc08a983736da330ac',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': f'https://www.ixigua.com/{id}?id={episodeId}',
                'accept-language': 'zh-CN,zh;q=0.9',
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                json_data = json.loads(response.text)
                playlist = json_data['data']['playlist']

                for playItem in playlist:
                    target_url = f"https://www.ixigua.com/{id}?id={episodeId}"
                    res.append({'id':id,
                                'title':playItem['title'],
                                'publish_time':json_data['data']['albumInfo']['year'],
                                'url':target_url,
                                'video_list':video_list,
                                'definition_list':definition_list})
                
            else:
                    target_url = f"https://www.ixigua.com/{id}"
                    publish_time = self.search_key_in_json(packerData,'video_publish_time')
                    formatted_time = datetime.fromtimestamp(int(publish_time)).strftime('%Y-%m-%d %H:%M:%S')
                    title = self.search_key_in_json(packerData,'title')
               
                    res.append({'id':id,
                                'title':title,
                                'publish_time':formatted_time,
                                'url':target_url,
                                'video_list':video_list,
                                'definition_list':definition_list
                                })
            return res    
        else:
            logging.info("未找到匹配的部分")
            return []



    def xigua_download(self,video_data_):
        # 解析URL
        parsed_url = urlparse(video_data_['url'])

        # 解析查询参数
        query_params = parse_qs(parsed_url.query)

        # 添加或更新 wid_try 参数
        query_params['wid_try'] = ['1']

        # 重新构建URL
        url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path,
                                parsed_url.params, urlencode(query_params, doseq=True),
                                parsed_url.fragment))

        payload = {}
        headers = {
        'authority': 'www.ixigua.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'referer': f'{url}',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        html_content = response.content.decode('utf-8')
        # 使用正则表达式匹配 <script[^>]*>(.*?)<\/script>
        pattern = re.compile(r'<script\s+id=".*?"\s*nonce=".*?">\s*window\._SSR_HYDRATED_DATA=(.*?)</script>', re.DOTALL)
        match = pattern.search(html_content)


        video_data = None
        if match:
            json_content_str = match.group(1)
            output_string = json_content_str.replace('undefined', '{}')

            json_content = json.loads(output_string)
            # 当前路径：anyVideo.gidInformation.packerData.videoResource.normal.video_list.video_3.main_url

            video_list = self.search_key_in_json(json_content,'video_list')
            video_data =next((obj for obj in video_list.values() if obj['definition'] == video_data_['p']), list(video_list.values())[len(video_list.values() )- 1])
            main_url  = video_data['main_url']
            decoded_url = base64.b64decode(main_url).decode('utf-8')
            video_data['main_url'] = decoded_url

        return video_data


 
    def search_key_in_json(self,data, search_key):
        if isinstance(data, dict):
            if search_key in data:
                return data[search_key]
            for key, value in data.items():
                result = self.search_key_in_json(value, search_key)
                if result is not None:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = self.search_key_in_json(item, search_key)
                if result is not None:
                    return result
        return None

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
        item_list = [{'id':x['gid'],
                      'title':x['title'],
                      'publish_time': datetime.utcfromtimestamp( x['publish_time']).strftime("%Y-%m-%d %H:%M:%S"),
                      'url':f"https://www.ixigua.com/{x['gid']}",
                       'definition_list':['360p','480p','720p','1080p']
                    #   ,'videolist':definition_list
                      } 
                      for x in videoList]
        return item_list   


    def new_version(self):
        url = "https://gitee.com/mijin/xigua_down/releases"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 200:
            input_data = response.text
            regex = "data-tag-name='(.*?)'"
            pattern = re.compile(regex)
            matcher = pattern.finditer(input_data)

            version_list = []
            # 寻找匹配项
            for match in matcher:
                # 提取匹配的组（即括号内的内容）
                version_code = match.group(1)
                version_list.append(version_code)

            if version_list:
                NEW_APP_VERSION = max(version_list)

        return NEW_APP_VERSION


                



if __name__ == '__main__':


    app = QApplication(sys.argv)
    my_gui = MyGUI()
    my_gui.show()
    sys.exit(app.exec_())
