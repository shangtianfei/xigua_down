
# xigua_down
西瓜视频免登录下载,提供单个视频的url即可下载


# 使用方法
## 下载单个视频

1. 将西瓜URL复制下来

    e.g.
![1](https://github.com/shangtianfei/xigua_down/assets/24507317/b515f189-845e-41a4-9dae-2d98f23531a8)

2. 双击 西瓜视频.exe

    e.g.
![2](https://github.com/shangtianfei/xigua_down/assets/24507317/b054c898-05dc-40e1-8d87-e0bfacb47fc8)


3. 在窗口输入 复制的链接，点击下载按钮，等待

    e.g.
![3](https://github.com/shangtianfei/xigua_down/assets/24507317/37abec21-ab57-4e28-9389-16641cd3845d)


4. 下载完成后 西瓜视频.exe 所在目录会自动生成download文件夹，文件夹里面会有链接对应的视频

    e.g.
![4](https://github.com/shangtianfei/xigua_down/assets/24507317/7fcee0b1-4297-4e64-91f9-3439d598144b)


    e.g.
![5](https://github.com/shangtianfei/xigua_down/assets/24507317/5122ed18-011a-47d6-8fba-15b33c497b01)


## 下载多个视频
todo。。。


感谢 https://github.com/wangjunji0920/xigua_downloader 开源的代码


批量下载
```
async function getVideoUrl(url) {
    let iframe = document.createElement('iframe')

    document.body.appendChild(iframe)

    try {
        await new Promise((resolve, reject) => Object.assign(iframe, { onload: resolve, onerror: reject, src: url }))

        //anyVideo.gidInformation.packerData.videoResource.normal.video_list
        let videoRes;
        if (iframe.contentWindow._SSR_HYDRATED_DATA.anyVideo.gidInformation.packerData.video) {
            videoRes = iframe.contentWindow._SSR_HYDRATED_DATA.anyVideo.gidInformation.packerData.video.videoResource;
        }
        else{
            videoRes = iframe.contentWindow._SSR_HYDRATED_DATA.anyVideo.gidInformation.packerData.videoResource;
        }

        let { video_list: videoList } = videoRes.normal
        let key = Object.keys(videoList).sort().pop()
        let { main_url: videoUrl } = videoList[key]

        return videoUrl
    } finally {
        document.body.removeChild(iframe)
    }
}

async function download(title, url) {
    let board = document.createElement('div')
    board.style = `
        position: fixed; left: 0; top: 0; z-index: 10000; background: lightgray;
        font-size: 20px; line-height: 40px; padding: 18px 2em; box-shadow: #b6b6b6 0 0 20px 14px;
        white-space: pre; text-align: center;
    `
    document.body.appendChild(board)

    try {
        let xhr = new XMLHttpRequest()
        xhr.open('GET', url)
        xhr.responseType = 'arraybuffer'
        xhr.onprogress = ({ loaded, total }) => board.textContent = `当前任务：${title}\n进行中：${(loaded / total * 100).toFixed(1)}%`
        await new Promise((resolve, reject) => (Object.assign(xhr, { onload: resolve, onerror: reject }), xhr.send()))

        const { response } = xhr
        return new Blob([response], {type: 'arraybuffer'})
    } finally {
        document.body.removeChild(board)
    }
}

function retryWrapper(fn, times = 3) {
    return async function() {
        for (let i = 0; i < times; i++) {
            try {
                return await fn.apply(this, arguments)
            } catch (e) {
                await new Promise(resolve => setTimeout(resolve, 500 * Math.pow(2, i)))
            }
        }
    }
}

(async function main() {
    let nodeList = document.querySelectorAll('div.HorizontalFeedCard a.HorizontalFeedCard__coverWrapper')

    for (let element of nodeList) {
        let title = element.getAttribute('title')
        let url = location.origin + element.getAttribute('href')

        let videoUrl = await retryWrapper(getVideoUrl, 5)(url)

        let blob = await retryWrapper(download, 10)(title, videoUrl)
        let link = URL.createObjectURL(blob)
        Object.assign(document.createElement('a'), { href: link, download: `${title}.mp4` }).click()
    }
})()
```