import base64
import json
import os
import re
import requests
from bs4 import BeautifulSoup



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

def file_download(filename,url):
    os.makedirs('download', exist_ok=True)
    response = requests.get(url, stream=True, timeout=30)

    with open(os.path.join('download',filename), 'wb') as file:
        for chunk in response.iter_content(chunk_size=128):
            file.write(chunk)

def all_item_list(home_id):
    url = f"https://www.ixigua.com/api/videov2/author/new_video_list?to_user_id={home_id}&offset=0&limit=30"

    payload = {}
    headers = {
    'authority': 'www.ixigua.com',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98"',
    'accept': 'application/json, text/plain, */*',
    'x-secsdk-csrf-token': '0001000000012d8c8e7b0d26fba2cfc3268638a09cde9aaa2547df73756304a88ba8fc8a33ba17a70903d2d357bc',
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

    return response



if __name__ == '__main__':

    url = "https://www.ixigua.com/7319841194182672936?wid_try=1"

    payload = {}
    headers = {
    'authority': 'www.ixigua.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'max-age=0',
    'referer': 'https://www.ixigua.com/7319841194182672936',
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
    # 使用正则表达式匹配
    pattern = re.compile(r'<title[^>]*>(.*?)<\/title>', re.DOTALL)
    match = pattern.search(html_content)

    if match:
        title_content = match.group(1)
        print("找到匹配的部分:", title_content)
    else:
        print("未找到匹配的部分")

