import json
import requests
import urllib.parse
import time
import datetime
import random
import os
import subprocess
from cache import cache
import ast

# 3 => (3.0, 1.5) => (1.5, 1)
max_api_wait_time = (1.5, 1)
# 10 => 10
max_time = 10

user_agents = [
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3864.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:62.0) Gecko/20100101 Firefox/62.0',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:67.0) Gecko/20100101 Firefox/67.0',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:68.0) Gecko/20100101 Firefox/68.0',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15',
  'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1'
]

def getRandomUserAgent():
  user_agent = user_agents[random.randint(0, len(user_agents) - 1)]
  print(user_agent)
  return {
    'User-Agent': user_agent
  }

class InvidiousAPI:
    def __init__(self):
        self.all = ast.literal_eval(requests.get('https://raw.githubusercontent.com/yuto1106110/invidious-instance-dieu-eviter/refs/heads/main/data/valid.json', headers=getRandomUserAgent(), timeout=(1.0, 0.5)).text)
        
        self.video = self.all['video']
        self.playlist = self.all['playlist']
        self.search = self.all['search']
        self.channel = self.all['channel']
        self.comments = self.all['comments']

        self.check_video = False

    def info(self):
        return {
            'API': self.all,
            'checkVideo': self.check_video
        }

        
invidious_api = InvidiousAPI()

url = requests.get('https://raw.githubusercontent.com/yuto1106110/invidious-instance-dieu-eviter/refs/heads/main/data/valid.json', headers=getRandomUserAgent()).text.rstrip()

version = "1.0"
new_instance_version = "1.3.2"


os.system("chmod 777 ./yukiverify")

class APITimeoutError(Exception):
    pass

class UnallowedBot(Exception):
    pass

def isJSON(json_str):
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError as jde:
        pass
    return False

def updateList(list, str):
    list.append(str)
    list.remove(str)
    return list

def requestAPI(path, api_urls):
    starttime = time.time()
    
    for api in api_urls:
        if  time.time() - starttime >= max_time - 1:
            break
            
        try:
            print(api + 'api/v1' + path)
            res = requests.get(api + 'api/v1' + path, headers=getRandomUserAgent(), timeout=max_api_wait_time)
            if res.status_code == requests.codes.ok and isJSON(res.text):
                
                if invidious_api.check_video and path.startswith('/video/'):
                    # 動画の有無をチェックする場合
                    video_res = requests.get(json.loads(res.text)['formatStreams'][0]['url'], headers=getRandomUserAgent(), timeout=(3.0, 0.5))
                    if not 'video' in video_res.headers['Content-Type']:
                        print(f"No Video(True)({video_res.headers['Content-Type']}): {api}")
                        updateList(api_urls, api)
                        continue

                if path.startswith('/channel/') and json.loads(res.text)["latestvideo"] == []:
                    print(f"No Channel: {api}")
                    updateList(api_urls, api)
                    continue

                print(f"Success({invidious_api.check_video})({path.split('/')[1].split('?')[0]}): {api}")
                return res.text

            elif isJSON(res.text):
                # ステータスコードが200ではないかつ内容がJSON形式の場合
                print(f"Returned Err0r(JSON): {api} ('{json.loads(res.text)['error'].replace('error', 'err0r')}')")
                updateList(api_urls, api)
            else:
                # ステータスコードが200ではないかつ内容がJSON形式ではない場合
                print(f"Returned Err0r: {api} ('{res.text[:100]}')")
                updateList(api_urls, api)
        except:
            # 例外等が発生した場合
            print(f"Err0r: {api}")
            updateList(api_urls, api)
    
    raise APITimeoutError("APIがタイムアウトしました")


def getInfo(request):
    return json.dumps([version, os.environ.get('RENDER_EXTERNAL_URL'), str(request.scope["headers"]), str(request.scope['router'])[39:-2]])

failed = "Load Failed"

def getVideoData(videoid):
    t = json.loads(requestAPI(f"/videos/{urllib.parse.quote(videoid)}?hl=ja&gl=JP", invidious_api.video))

    if 'recommendedvideo' in t:
        recommended_videos = t["recommendedvideo"]
    elif 'recommendedVideos' in t:
        recommended_videos = t["recommendedVideos"]
    else:
        recommended_videos = [{
            "videoId": failed, "title": failed,
            "authorId": failed, "author": failed,
            "lengthSeconds": 0, "viewCountText": "Load Failed"
        }]

    adaptiveFormats = t.get("adaptiveFormats", [])
    highstream_url = None
    audio_url = None
    quality_streams = []

    for stream in adaptiveFormats:
        if stream.get("container") == "webm" and stream.get("resolution"):
            quality_streams.append({
                "url": stream.get("url"),
                "resolution": stream.get("resolution"),
            })

    quality_streams.sort(
        key=lambda x: int(x["resolution"].replace("p", "")) if x["resolution"].replace("p", "").isdigit() else 0,
        reverse=True
    )
    highstream_url = quality_streams[0]["url"] if quality_streams else None

    streamUrls = [
        {"url": s["url"], "resolution": s["resolution"]}
        for s in adaptiveFormats
        if s.get("container") == "webm" and s.get("resolution")
    ]

    return [
        {
            "video_urls": list(reversed([i["url"] for i in t["formatStreams"]]))[:2],
            "highstream_url": highstream_url,
            "audio_url": audio_url,
            "quality_streams": quality_streams,
            "hlsUrl": t.get("hlsUrl"),
            "description_html": t["descriptionHtml"].replace("\n", "<br>"),
            "title": t["title"],
            "length_text": str(datetime.timedelta(seconds=t["lengthSeconds"])),
            "author_id": t["authorId"],
            "author": t["author"],
            "author_thumbnails_url": t["authorThumbnails"][-1]["url"],
            "view_count": t["viewCount"],
            "like_count": t["likeCount"],
            "subscribers_count": t["subCountText"],
            "streamUrls": streamUrls
        },
        [
            {
                "video_id": i["videoId"],
                "title": i["title"],
                "author_id": i["authorId"],
                "author": i["author"],
                "length_text": str(datetime.timedelta(seconds=i["lengthSeconds"])),
                "view_count_text": i["viewCountText"]
            } for i in recommended_videos
        ]
    ]

def getSearchData(q, page):

    def formatSearchData(data_dict):
        if data_dict["type"] == "video":
            return {
                "type": "video",
                "title": data_dict["title"] if 'title' in data_dict else failed,
                "id": data_dict["videoId"] if 'videoId' in data_dict else failed,
                "authorId": data_dict["authorId"] if 'authorId' in data_dict else failed,
                "author": data_dict["author"] if 'author' in data_dict else failed,
                "published": data_dict["publishedText"] if 'publishedText' in data_dict else failed,
                "length": str(datetime.timedelta(seconds=data_dict["lengthSeconds"])),
                "view_count_text": data_dict["viewCountText"]
            }
            
        elif data_dict["type"] == "playlist":
            return {
                    "type": "playlist",
                    "title": data_dict["title"] if 'title' in data_dict else failed,
                    "id": data_dict['playlistId'] if 'playlistId' in data_dict else failed,
                    "thumbnail": data_dict["playlistThumbnail"] if 'playlistThumbnail' in data_dict else failed,
                    "count": data_dict["videoCount"] if 'videoCount' in data_dict else failed
                }
            
        elif data_dict["authorThumbnails"][-1]["url"].startswith("https"):
            return {
                "type": "channel",
                "author": data_dict["author"] if 'author' in data_dict else failed,
                "id": data_dict["authorId"] if 'authorId' in data_dict else failed,
                "thumbnail": data_dict["authorThumbnails"][-1]["url"] if 'authorThumbnails' in data_dict and len(data_dict["authorThumbnails"]) and 'url' in data_dict["authorThumbnails"][-1] else failed
            }
        else:
            return {
                "type": "channel",
                "author": data_dict["author"] if 'author' in data_dict else failed,
                "id": data_dict["authorId"] if 'authorId' in data_dict else failed,
                "thumbnail": "https://" + data_dict['authorThumbnails'][-1]['url']
            }

    # "datas"というのは気持ち悪いかもしれないが、複数のデータが入っていると明示できるという
    # メリットの方がコードを書く上では大きい
    datas_dict = json.loads(requestAPI(f"/search?q={urllib.parse.quote(q)}&page={page}&hl=jp", invidious_api.search))
    return [formatSearchData(data_dict) for data_dict in datas_dict]


def getChannelData(channelid):
    t = json.loads(requestAPI(f"/channels/{urllib.parse.quote(channelid)}", invidious_api.channel))
    if 'latestvideo' in t:
        latest_videos = t['latestvideo']
    elif 'latestVideos' in t:
        latest_videos = t['latestVideos']
    else:
        latest_videos = {
            "title": failed,
            "videoId": failed,
            "authorId": failed,
            "author": failed,
            "publishedText": failed,
            "viewCountText": "0",
            "lengthSeconds": "0"
        }
    
    
    return [
        [
            {
                # 直近の動画
                "type":"video",
                "title": i["title"],
                "id": i["videoId"],
                "authorId": t["authorId"],
                "author": t["author"],
                "published": i["publishedText"],
                "view_count_text": i['viewCountText'],
                "length_str": str(datetime.timedelta(seconds=i["lengthSeconds"]))
            } for i in latest_videos
        ], {
            # チャンネル情報
            "channel_name": t["author"],
            "channel_icon": t["authorThumbnails"][-1]["url"],
            "channel_profile": t["descriptionHtml"],
            "author_banner": urllib.parse.quote(t["authorBanners"][0]["url"], safe="-_.~/:") if 'authorBanners' in t and len(t['authorBanners']) else '',
            "subscribers_count": t["subCount"],
            "tags": t["tags"]
        }
    ]

def getPlaylistData(listid, page):
    t = json.loads(requestAPI(f"/playlists/{urllib.parse.quote(listid)}?page={urllib.parse.quote(page)}", invidious_api.playlist))["videos"]
    return [{"title": i["title"], "id": i["videoId"], "authorId": i["authorId"], "author": i["author"], "type": "video"} for i in t]

def getCommentsData(videoid):
    t = json.loads(requestAPI(f"/comments/{urllib.parse.quote(videoid)}?hl=jp", invidious_api.comments))["comments"]
    return [{"author": i["author"], "authoricon": i["authorThumbnails"][-1]["url"], "authorid": i["authorId"], "body": i["contentHtml"].replace("\n", "<br>")} for i in t]

'''
使われていないし戻り値も設定されていないためコメントアウト
def get_replies(videoid, key):
    t = json.loads(requestAPI(f"/comments/{videoid}?hmac_key={key}&hl=jp&format=html", invidious_api.comments))["contentHtml"]
'''


def checkCookie(cookie):
    isTrue = True if cookie == "True" else False
    return isTrue

def getVerifyCode():
    try:
        result = subprocess.run(["./yukiverify"], encoding='utf-8', stdout=subprocess.PIPE)
        hashed_password = result.stdout.strip()
        return hashed_password
    except subprocess.CalledProcessError as e:
        print(f"getVerifyCode__Error: {e}")
        return None


from fastapi import FastAPI, Depends, Form
from fastapi import Response, Cookie, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.responses import RedirectResponse as redirect
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Union
from fastapi import Form

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/js", StaticFiles(directory="./statics/js"), name="static")
app.mount("/css", StaticFiles(directory="./statics/css"), name="static")
app.mount("/img", StaticFiles(directory="./statics/img"), name="static")
app.mount("/genesis", StaticFiles(directory="./blog", html=True), name="static")
app.add_middleware(GZipMiddleware, minimum_size=1000)

from fastapi.templating import Jinja2Templates
template = Jinja2Templates(directory='templates').TemplateResponse

no_robot_meta_tag = '<meta name="robots" content="noindex,nofollow">'

@app.get("/", response_class=HTMLResponse)
def home(response: Response, request: Request, yuki: Union[str] = Cookie(None)):
    if checkCookie(yuki):
        response.set_cookie("yuki", "True", max_age=60 * 60 * 24 * 7)
        return template("home.html", {"request": request})
    print(checkCookie(yuki))
    return redirect("/genesis")

@app.get('/watch', response_class=HTMLResponse)
def video(v: str, response: Response, request: Request, yuki: Union[str, None] = Cookie(None), proxy: Union[str, None] = Cookie(None)):
    if not checkCookie(yuki):
        return redirect("/")
    response.set_cookie("yuki", "True", max_age=7*24*60*60)
    video_data = getVideoData(v)
    return template('video.html', {
        "request": request,
        "videoid": v,
        "videourls": video_data[0]['video_urls'],
        "highstream_url": video_data[0]['highstream_url'],
        "audio_url": video_data[0]['audio_url'],
        "quality_streams": video_data[0]['quality_streams'],
        "description": video_data[0]['description_html'],
        "video_title": video_data[0]['title'],
        "author_id": video_data[0]['author_id'],
        "author_icon": video_data[0]['author_thumbnails_url'],
        "author": video_data[0]['author'],
        "length_text": video_data[0]['length_text'],
        "view_count": video_data[0]['view_count'],
        "like_count": video_data[0]['like_count'],
        "subscribers_count": video_data[0]['subscribers_count'],
        "recommended_videos": video_data[1],
        "proxy": proxy
    })

@app.get('/api/ytdlp/{video_id}')
def get_ytdlp(video_id: str, response: Response, yuki: Union[str, None] = Cookie(None)):
    if not checkCookie(yuki):
        return {"error": "unauthorized"}
    try:
        import yt_dlp
        ydl_opts = {
    "quiet": True,
    "format": "bestvideo[ext=webm]+bestaudio[ext=m4a]/best",
    # Botチェック回避
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "web"],
        }
    },
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    },
    "sleep_interval": 1,
    "max_sleep_interval": 3,
}

        # 画質ストリーム
        quality_streams = []
        audio_url = None
        for f in info.get("formats", []):
            if f.get("vcodec") != "none" and f.get("acodec") == "none":
                quality_streams.append({
                    "url": f["url"],
                    "resolution": f"{f.get('height', '?')}p",
                })
            elif f.get("acodec") != "none" and f.get("vcodec") == "none":
                if not audio_url:
                    audio_url = f["url"]

        quality_streams.sort(
            key=lambda x: int(x["resolution"].replace("p","")) if x["resolution"].replace("p","").isdigit() else 0,
            reverse=True
        )
        # 重複解像度を除去
        seen = set()
        unique_streams = []
        for s in quality_streams:
            if s["resolution"] not in seen:
                seen.add(s["resolution"])
                unique_streams.append(s)

        # HLS（ライブ）
        hls_url = None
        if info.get("is_live"):
            for f in info.get("formats", []):
                if f.get("protocol", "").startswith("m3u8"):
                    hls_url = f["url"]
                    break

        return {
            "quality_streams": unique_streams,
            "audio_url": audio_url,
            "hlsUrl": hls_url,
            "provider": "ytdlp"
        }
    except Exception as e:
        return {"error": str(e)}
  
@app.get('/w', response_class=HTMLResponse)
def video(v:str, response: Response, request: Request, yuki: Union[str] = Cookie(None), proxy: Union[str] = Cookie(None)):
    # v: video_id
    if not(checkCookie(yuki)):
        return redirect("/")
    response.set_cookie(key="yuki", value="True", max_age=7*24*60*60)
    video_data = getVideoData(v)
    '''
    return [
        {
            'video_urls': list(reversed([i["url"] for i in t["formatStreams"]]))[:2],
            'highstream_url': highstream_url,
            'audio_url': audio_url,
            'description_html': t["descriptionHtml"].replace("\n", "<br>"),
            'title': t["title"],
            'length_text': str(datetime.timedelta(seconds=t["lengthSeconds"]))
            'author_id': t["authorId"],
            'author': t["author"],
            'author_thumbnails_url': t["authorThumbnails"][-1]["url"],
            'view_count': t["viewCount"],
            'like_count': t["likeCount"],
            'subscribers_count': t["subCountText"]
        },
        [
            {
                "video_id": i["videoId"],
                "title": i["title"],
                "author_id": i["authorId"],
                "author": i["author"],
                "length_text": str(datetime.timedelta(seconds=i["lengthSeconds"])),
                "view_count_text": i["viewCountText"]
            } for i in recommended_videos
        ]
    ]
    '''
    response.set_cookie("yuki", "True", max_age=60 * 60 * 24 * 7)
    return template('hiquo.html', {
        "request": request,
        "videoid": v,
        "videourls": video_data[0]['video_urls'],
        "highstream_url": video_data[0]['highstream_url'],
        "audio_url": video_data[0]['audio_url'],
        "description": video_data[0]['description_html'],
        "video_title": video_data[0]['title'],
        "author_id": video_data[0]['author_id'],
        "author_icon": video_data[0]['author_thumbnails_url'],
        "author": video_data[0]['author'],
        "length_text": video_data[0]['length_text'],
        "view_count": video_data[0]['view_count'],
        "like_count": video_data[0]['like_count'],
        "subscribers_count": video_data[0]['subscribers_
