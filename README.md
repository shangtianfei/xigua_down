
# xigua_down
西瓜视频免登录下载,提供单个视频的url即可下载


# 使用方法
## 下载单个视频

1. 将西瓜URL复制下来

    e.g.
![1](https://gitee.com/mijin/xigua_down/raw/main/imgs/1.png)

2. 双击 app.xigua.qt.exe

    e.g.
![2](https://gitee.com/mijin/xigua_down/raw/main/imgs/2.png)


3. 在窗口输入 复制的链接，点击查找，等待

    e.g.
![3](https://gitee.com/mijin/xigua_down/raw/main/imgs/3.png)


4. 下载完成后 app.xigua.qt.exe 所在目录会自动生成download文件夹，文件夹里面会有链接对应的视频

    e.g.
![4](https://gitee.com/mijin/xigua_down/raw/main/imgs/4.png)


    e.g.
![5](https://gitee.com/mijin/xigua_down/raw/main/imgs/5.png)




## 下载多个视频

1. 将西瓜博主的URL复制下来

    e.g.
![1](https://gitee.com/mijin/xigua_down/raw/main/imgs/11.png)

2. 双击 app.xigua.qt.exe

    e.g.
![2](https://gitee.com/mijin/xigua_down/raw/main/imgs/2.png)


3. 在窗口输入 复制的链接，点击查找，等待

    e.g.
![3](https://gitee.com/mijin/xigua_down/raw/main/imgs/13.png)


4. 下载完成后 app.xigua.qt.exe 所在目录会自动生成download文件夹，文件夹里面会有链接对应的视频

    e.g.
![4](https://gitee.com/mijin/xigua_down/raw/main/imgs/4.png)


    e.g.
![5](https://gitee.com/mijin/xigua_down/raw/main/imgs/5.png)



## 桌面

使用默认python版本创建虚拟环境
```
virtualenv venv

.\venv\Scripts\activate

依赖处理

pip install -r requirements.txt
pip freeze > requirements.txt

打包处理

pyinstaller --noconsole --onefile  app.xigua.qt.py

退出虚拟环境
deactivate
```
感谢 https://github.com/wangjunji0920/xigua_downloader 开源的代码