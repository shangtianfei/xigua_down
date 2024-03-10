
import re
import requests


class Util():

    # 获取json对象
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
    

    # 获取版本信息
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