import base64
from datetime import datetime
from enum import Enum  
from abc import ABC, abstractmethod
import json
import re
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import requests

from util import Util  




class FactoryBean():

    def factory_bean(self,url):
        for s in  NetType:
            parts = s.value.split(",")  # 使用逗号和空格作为切割点  
            for part in parts:
                if part in url:
                    return factory_dict[s] 
        
        return   None 


  
class NetType(Enum):  
   IXIGUA = "ixigua.com"  
   BiliBili = "bilibili.com"  


        
# 抽象工厂接口  
class AbstractFactory(ABC):  
    def __init__(self):
        self.callbacks = []

    def subscribe(self, callback):
        self.callbacks.append(callback)

    def trigger(self, *args, **kwargs):
        for callback in self.callbacks:
            callback(*args, **kwargs)

    @abstractmethod  
    def handler(self,url,offset=0,limit=30):  
        pass      

    @abstractmethod  
    def netType(self):  
        pass    

    @abstractmethod  
    def download_url(self,url):  
        pass   

    @abstractmethod  
    def download(self,download_url,heard_dict,out_file):
        pass          

 
        

# 具体工厂 西瓜 
class IXIGUAConcreteFactory(AbstractFactory):  
    def __init__(self):
        self.util = Util()
        self.observers = []

    def register(self, observer):
        self.observers.append(observer)


    def download(self, download_url, heard_dict, out_file):

        return super().download(download_url, heard_dict, out_file)

    def download_url(self, url):
        # 解析URL
        parsed_url = urlparse(url)

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


        decoded_url = None
        if match:
            json_content_str = match.group(1)
            output_string = json_content_str.replace('undefined', '{}')

            json_content = json.loads(output_string)
            # 当前路径：anyVideo.gidInformation.packerData.videoResource.normal.video_list.video_3.main_url
            for i in range(3,0,-1):
                video_data = self.util.search_key_in_json(json_content,f'video_{i}')
                if video_data != None:
                    main_url  = video_data['main_url']
                    decoded_url = base64.b64decode(main_url).decode('utf-8')
                    break

        return decoded_url


    def netType(self):
        return NetType.IXIGUA

    def handler(self,url,offset=0,limit=30):
        xigua_url = 'https://www.ixigua.com/'
        if xigua_url in url:
            text = url.replace(xigua_url, '')
        if 'home' in text:
            item_list = self.item_list_page(text[5:21],offset,limit)
        else:
            item_list = self.xigua_title_by_id(text[:19])
        return item_list


        
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
            # print(json_content_str)
            output_string = json_content_str.replace('undefined', '{}')

            json_content = json.loads(output_string)
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
                    res.append({'id':id,'title':playItem['title'],'publish_time':json_data['data']['albumInfo']['year'],'url':target_url,'status':'查看'})
                
            else:
                    target_url = f"https://www.ixigua.com/{id}"
                    publish_time = self.util.search_key_in_json(packerData,'video_publish_time')
                    formatted_time = datetime.fromtimestamp(int(publish_time)).strftime('%Y-%m-%d %H:%M:%S')
                    title = self.util.search_key_in_json(packerData,'title')
               
                    res.append({'id':id,'title':title,'publish_time':formatted_time,'url':target_url,'status':'查看'})
            return res    
        else:
            print("未找到匹配的部分")
            return []
        

    def item_list_page(self,home_id,offset=0,limit=30):
        offset += 1
        print(f"home_id={home_id},offset={offset},limit={limit}")
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
        item_list = [{'id':x['gid'],'title':x['title'],'publish_time': datetime.utcfromtimestamp( x['publish_time']).strftime("%Y-%m-%d %H:%M:%S"),'url':f"https://www.ixigua.com/{x['gid']}",'status':'查看'} for x in videoList]
        return item_list   



class BiliBiliConcreteFactory(AbstractFactory):
    
    def handler(self, url, offset=0, limit=30):
        return super().handler(url, offset, limit)
    
    def netType(self):
        return NetType.BiliBili
    
    def download_url(self, url):
        return super().download_url(url)

# 创建一个字典，使用NetType作为键，工厂对象作为值  
factory_dict = {  
    NetType.IXIGUA: IXIGUAConcreteFactory()  
}  