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

def formatViewCount(count):
    try:
        count = int(count)
        if count >= 100000000:
            return f"{count // 100000000}億"
        elif count >= 10000:
            return f"{count // 10000}万"
        elif count >= 1000:
            return f"{count // 1000}千"
        else:
            return str(count)
    except:
        return str(count)

def convertSubCount(text):
    try:
        text = str(text).upper().replace(',', '')
        if 'K' in text:
            return formatViewCount(int(float(text.replace('K', '')) * 1000)) + "人"
        elif 'M' in text:
            return formatViewCount(int(float(text.replace('M', '')) * 1000000)) + "人"
        elif 'B' in text:
            return formatViewCount(int(float(text.replace('B', '')) * 1000000000)) + "人"
        else:
            return formatViewCount(int(text)) + "人"
    except:
        return text

def formatPublished(timestamp):
    try:
        now = int(time.time())
        diff = now - int(timestamp)
        if diff < 60:
            return "たった今"
        elif diff < 3600:
            return f"{diff // 60}分前"
        elif diff < 86400:
            return f"{diff // 3600}時間前"
        elif diff < 86400 * 7:
            return f"{diff // 86400}日前"
        elif diff < 86400 * 30:
            return f"{diff // (86400 * 7)}週間前"
        elif diff < 86400 * 365:
            return f"{diff // (86400 * 30)}ヶ月前"
        else:
            return f"{diff // (86400 * 365)}年前"
    except:
        return ""

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
            "view_count": t.get("viewCount", 0),
            "view_count_text": formatViewCount(t.get("viewCount", 0)),
            "published_text": formatPublished(t.get("published", 0)),
            "like_count": t.get("likeCount", 0),
            "subscribers_count": convertSubCount(t.get("subCountText", "")),
            "streamUrls": streamUrls
        },
        [
            {
                "video_id": i["videoId"],
                "title": i["title"],
                "author_id": i["authorId"],
                "author": i["author"],
                "length_text": str(datetime.timedelta(seconds=i["lengthSeconds"])),
                "view_count_text": i.get("viewCountText", ""),
                "published_text": i.get("publishedText", ""),
            } for i in recommended_videos
        ]
    ]
  
def getSearchData(q, page):

    def formatSearchData(data_dict):
        if data_dict["type"] == "video":
          print("published:", data_dict.get("published"), "publishedText:", data_dict.get("publishedText"))
          return {
            "type": "video",
            "title": data_dict["title"] if 'title' in data_dict else failed,
            "id": data_dict["videoId"] if 'videoId' in data_dict else failed,
            "authorId": data_dict["authorId"] if 'authorId' in data_dict else failed,
            "author": data_dict["author"] if 'author' in data_dict else failed,
            "published": data_dict.get("publishedText", "") or formatPublished(data_dict.get("published", 0)),
            "length": str(datetime.timedelta(seconds=data_dict.get("lengthSeconds", 0))),
            "view_count_text": formatViewCount(data_dict.get("viewCount", 0)),
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

def getChannelData(channelid, sort_by="newest"):
    t = json.loads(requestAPI(f"/channels/{urllib.parse.quote(channelid)}?hl=ja&gl=JP", invidious_api.channel))

    # 動画一覧を別エンドポイントから取得（ソート対応）
    try:
        videos_data = json.loads(requestAPI(
            f"/channels/{urllib.parse.quote(channelid)}/videos?sort_by={sort_by}&hl=ja&gl=JP",
            invidious_api.channel
        ))
        latest_videos = videos_data.get("videos", [])
    except:
        # フォールバック
        if 'latestvideo' in t:
            latest_videos = t['latestvideo']
        elif 'latestVideos' in t:
            latest_videos = t['latestVideos']
        else:
            latest_videos = []

    videos = []
    shorts = []
    for i in latest_videos:
        length = i.get("lengthSeconds", 0)
        is_short = i.get("isShort", False) or (length > 0 and length <= 60)
        item = {
            "type": "video",
            "title": i["title"],
            "id": i["videoId"],
            "authorId": t["authorId"],
            "author": t["author"],
            "published": i.get("published", 0),
            "published_text": i.get("publishedText", ""),
            "view_count": i.get("viewCount", 0),
            "view_count_text": formatViewCount(i.get("viewCount", 0)),
            "length_str": str(datetime.timedelta(seconds=length)),
            "is_short": is_short
        }
        if is_short:
            shorts.append(item)
        else:
            videos.append(item)

    # プレイリスト取得
    playlists = []
    try:
        pl_data = json.loads(requestAPI(
            f"/channels/{urllib.parse.quote(channelid)}/playlists?hl=ja&gl=JP",
            invidious_api.channel
        ))
        for pl in pl_data.get("playlists", []):
            thumb = pl.get("playlistThumbnail", "")
            if thumb and not thumb.startswith("http"):
                thumb = f"https://img.youtube.com/vi/{thumb}/mqdefault.jpg"
            playlists.append({
                "id": pl.get("playlistId", ""),
                "title": pl.get("title", ""),
                "video_count": pl.get("videoCount", 0),
                "thumbnail": thumb,
            })
    except:
        pass

    # コミュニティ投稿取得
    community = []
    try:
        comm_data = json.loads(requestAPI(
          f"/channels/{urllib.parse.quote(channelid)}/community?hl=ja&gl=JP",
          invidious_api.channel
        ))
        for post in comm_data.get("comments", []):
            community.append({
               "id": post.get("commentId", ""),
                "content": post.get("contentHtml", "").replace("\n", "<br>"),
                "published_text": post.get("publishedText", ""),
                "likes": formatViewCount(post.get("likeCount", 0)),
                "author": t["author"],
                "author_icon": t["authorThumbnails"][-1]["url"],
            })
    except:
        pass
  
    # 登録者数
    sub_count = t.get("subCount", 0)
    if sub_count:
        subscribers = formatViewCount(sub_count) + "人"
    else:
        subscribers = convertSubCount(t.get("subCountText", ""))

    return [
        videos,
        shorts,
        playlists,
        community,
        {
            "channel_name": t["author"],
            "channel_icon": t["authorThumbnails"][-1]["url"],
            "channel_profile": t.get("descriptionHtml", ""),
            "author_banner": urllib.parse.quote(t["authorBanners"][0]["url"], safe="-_.~/:") if t.get("authorBanners") else "",
            "subscribers_count": subscribers,
            "total_videos": str(len(videos) + len(shorts)) if (videos or shorts) else "",
        }
    ]

def getPlaylistData(listid, page):
    try:
        t = json.loads(requestAPI(f"/playlists/{urllib.parse.quote(listid)}?page={urllib.parse.quote(str(page))}", invidious_api.playlist))
        videos = t.get("videos", [])
        return [
            {
                "title": i["title"],
                "id": i["videoId"],
                "authorId": i["authorId"],
                "author": i["author"],
                "type": "video",
                "length": str(datetime.timedelta(seconds=i.get("lengthSeconds", 0))),
                "view_count_text": formatViewCount(i.get("viewCount", 0)),
                "published": formatPublished(i.get("published", 0)),
            }
            for i in videos
        ], len(videos) > 0
    except:
        return [], False

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

# MongoDB接続
from pymongo import MongoClient
from pydantic import BaseModel

MONGODB_URI = os.environ.get("MONGODB_URI")
TREND_API_URL = "https://plus-trend-api.vercel.app"

if MONGODB_URI:
    mongo_client = MongoClient(MONGODB_URI)
    db = mongo_client["ytplusplus"]
    trend_collection = db["trends"]
else:
    mongo_client = None
    db = None
    trend_collection = None

def cleanup_old_trends():
    if trend_collection is None:
        return
    try:
        cutoff = int(time.time()) - (30 * 24 * 60 * 60)
        trend_collection.delete_many({"last_watched": {"$lt": cutoff}})
    except:
        pass

def formatViewCount(count):
    try:
        count = int(count)
        if count >= 100000000:
            return f"{count // 100000000}億"
        elif count >= 10000:
            return f"{count // 10000}万"
        elif count >= 1000:
            return f"{count // 1000}千"
        else:
            return str(count)
    except:
        return str(count)

def formatPublished(timestamp):
    try:
        now = int(time.time())
        diff = now - int(timestamp)
        if diff < 60:
            return "たった今"
        elif diff < 3600:
            return f"{diff // 60}分前"
        elif diff < 86400:
            return f"{diff // 3600}時間前"
        elif diff < 86400 * 7:
            return f"{diff // 86400}日前"
        elif diff < 86400 * 30:
            return f"{diff // (86400 * 7)}週間前"
        elif diff < 86400 * 365:
            return f"{diff // (86400 * 30)}ヶ月前"
        else:
            return f"{diff // (86400 * 365)}年前"
    except:
        return ""

def convertSubCount(text):
    try:
        text = str(text).upper().replace(',', '')
        if 'K' in text:
            return formatViewCount(int(float(text.replace('K', '')) * 1000)) + "人"
        elif 'M' in text:
            return formatViewCount(int(float(text.replace('M', '')) * 1000000)) + "人"
        elif 'B' in text:
            return formatViewCount(int(float(text.replace('B', '')) * 1000000000)) + "人"
        else:
            return formatViewCount(int(text)) + "人"
    except:
        return text

app.mount("/js", StaticFiles(directory="./statics/js"), name="static")
app.mount("/css", StaticFiles(directory="./statics/css"), name="static")
app.mount("/img", StaticFiles(directory="./statics/img"), name="static")
app.mount("/genesis", StaticFiles(directory="./blog", html=True), name="static")
app.add_middleware(GZipMiddleware, minimum_size=1000)

from fastapi.templating import Jinja2Templates
_templates = Jinja2Templates(directory='templates')

def template(name, context, status_code=200):
    request = context.get("request")
    ctx = {k: v for k, v in context.items() if k != "request"}
    return _templates.TemplateResponse(
        request=request,
        name=name,
        context=ctx,
        status_code=status_code
    )

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

    # サイトトレンドに記録
    try:
        requests.post(
            f"{TREND_API_URL}/trend",
            json={
                "video_id": v,
                "title": video_data[0]["title"],
                "author": video_data[0]["author"],
                "thumbnail": f"https://img.youtube.com/vi/{v}/mqdefault.jpg",
                "length": video_data[0]["length_text"],
            },
            timeout=(1.0, 2.0)
        )
    except:
        pass

    return template('video.html', {
        "request": request,
        "videoid": v,
        "videourls": video_data[0]['video_urls'],
        "highstream_url": video_data[0].get('highstream_url'),
        "audio_url": video_data[0].get('audio_url'),
        "quality_streams": video_data[0].get('quality_streams', []),
        "hlsUrl": video_data[0].get('hlsUrl'),
        "description": video_data[0]['description_html'],
        "video_title": video_data[0]['title'],
        "author_id": video_data[0]['author_id'],
        "author_icon": video_data[0]['author_thumbnails_url'],
        "author": video_data[0]['author'],
        "length_text": video_data[0]['length_text'],
        "view_count": video_data[0]['view_count'],
        "view_count_text": video_data[0].get('view_count_text', ''),
        "published_text": video_data[0].get('published_text', ''),
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
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "web"],
                    "player_skip": ["js", "configs"],
                }
            },
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36",
                "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
            },
            "sleep_interval": 2,
            "max_sleep_interval": 5,
            "socket_timeout": 30,
            "retries": {"max_retries": 3, "backoff_factor": 0.5},
            "nocheckcertificate": True,
        }
      
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)

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

@app.get("/api/channel_videos/{channel_id}")
def get_channel_videos(channel_id: str, yuki: Union[str, None] = Cookie(None)):
    if not checkCookie(yuki):
        return {"error": "unauthorized"}
    try:
        t = json.loads(requestAPI(f"/channels/{urllib.parse.quote(channel_id)}?hl=ja&gl=JP", invidious_api.channel))
        latest = t.get('latestVideos', t.get('latestvideo', []))
        videos = [
            {
                "id": v["videoId"],
                "title": v["title"],
                "author": t["author"],
                "length": str(datetime.timedelta(seconds=v["lengthSeconds"])),
                "published": v.get("published", 0),
                "published_text": v.get("publishedText", ""),
                "view_count_text": formatViewCount(v.get("viewCount", 0)),
            }
            for v in latest
        ]
        return {"videos": videos}
    except Exception as e:
        return {"error": str(e), "videos": []}

# ===== トレンドAPI（書き込み・メインサイト用） =====
class TrendData(BaseModel):
    video_id: str
    title: str
    author: str
    thumbnail: str
    length: str

@app.post("/trend")
def record_trend(data: TrendData):
    if trend_collection is None:
        return {"ok": False, "reason": "no db"}
    try:
        now = int(time.time())
        trend_collection.update_one(
            {"video_id": data.video_id},
            {
                "$inc": {"count": 1},
                "$set": {
                    "title": data.title,
                    "author": data.author,
                    "thumbnail": data.thumbnail,
                    "length": data.length,
                    "last_watched": now,
                },
                "$setOnInsert": {"first_watched": now}
            },
            upsert=True
        )
        if random.randint(1, 100) == 1:
            cleanup_old_trends()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.get("/api/trending")
def get_yt_trending(category: str = "default", yuki: Union[str, None] = Cookie(None)):
    if not checkCookie(yuki):
        return {"error": "unauthorized"}
    try:
        category_map = {
            "default": "default",
            "gaming": "gaming",
            "music": "music",
            "movies": "movies",
            "news": "news",
        }
        cat = category_map.get(category, "default")
        data = json.loads(requestAPI(
            f"/trending?region=JP&type={cat}&hl=ja&gl=JP",
            invidious_api.search
        ))
        videos = [
            {
                "id": v["videoId"],
                "title": v["title"],
                "author": v.get("author", ""),
                "author_id": v.get("authorId", ""),
                "length": str(datetime.timedelta(seconds=v.get("lengthSeconds", 0))),
                "published_text": v.get("publishedText", ""),
                "view_count_text": formatViewCount(v.get("viewCount", 0)),
                "thumbnail": f"https://img.youtube.com/vi/{v['videoId']}/mqdefault.jpg",
            }
            for v in data
        ]
        return {"videos": videos}
    except Exception as e:
        return {"error": str(e), "videos": []}

@app.get("/api/site_trending")
def get_site_trending(period: str = "7days", yuki: Union[str, None] = Cookie(None)):
    if not checkCookie(yuki):
        return {"error": "unauthorized"}
    try:
        res = requests.get(
            f"{TREND_API_URL}/trending?period={period}",
            timeout=(1.0, 3.0)
        )
        return res.json()
    except Exception as e:
        return {"error": str(e), "videos": []}

@app.get("/trending", response_class=HTMLResponse)
def trending_page(request: Request, yuki: Union[str, None] = Cookie(None)):
    if not checkCookie(yuki):
        return redirect("/")
    return template("trending.html", {"request": request})

@app.get("/history", response_class=HTMLResponse)
def history_page(request: Request, yuki: Union[str, None] = Cookie(None)):
    if not checkCookie(yuki):
        return redirect("/")
    return template("history.html", {"request": request})

@app.get("/subscriptions", response_class=HTMLResponse)
def subscriptions_page(request: Request, yuki: Union[str, None] = Cookie(None)):
    if not checkCookie(yuki):
        return redirect("/")
    return template("subscriptions.html", {"request": request})

@app.get("/settings", response_class=HTMLResponse)
def subscriptions_page(request: Request, yuki: Union[str, None] = Cookie(None)):
    if not checkCookie(yuki):
        return redirect("/")
    return template("settings.html", {"request": request})

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
        "subscribers_count": video_data[0]['subscribers_count'],
        "recommended_videos": video_data[1],
        "proxy":proxy
    })

@app.get("/search", response_class=HTMLResponse)
def search(q: str, response: Response, request: Request, page: Union[int, None] = 1, yuki: Union[str] = Cookie(None), proxy: Union[str] = Cookie(None)):
    if not checkCookie(yuki):
        return redirect("/")
    response.set_cookie("yuki", "True", max_age=60 * 60 * 24 * 7)
    results = getSearchData(q, page)
    return template("search.html", {
        "request": request,
        "results": results,
        "word": q,
        "page": page,
        "next": f"/search?q={q}&page={page + 1}",
        "prev": f"/search?q={q}&page={page - 1}" if page > 1 else None,
        "proxy": proxy
    })

@app.get("/hashtag/{tag}")
def search(tag:str, response: Response, request: Request, page:Union[int, None]=1, yuki: Union[str] = Cookie(None)):
    if not(checkCookie(yuki)):
        return redirect("/")
    return redirect(f"/search?q={tag}")

@app.get("/channel/{channelid}", response_class=HTMLResponse)
def channel(channelid: str, response: Response, request: Request,
            sort_by: str = "newest",
            yuki: Union[str] = Cookie(None),
            proxy: Union[str] = Cookie(None)):
    if not checkCookie(yuki):
        return redirect("/")
    response.set_cookie("yuki", "True", max_age=60 * 60 * 24 * 7)
    t = getChannelData(channelid, sort_by=sort_by)
    return template("channel.html", {
        "request": request,
        "results": t[0],
        "shorts": t[1],
        "playlists": t[2],
        "community": t[3],
        "channel_id": channelid,
        "channel_name": t[4]["channel_name"],
        "channel_icon": t[4]["channel_icon"],
        "channel_profile": t[4]["channel_profile"],
        "cover_img_url": t[4]["author_banner"],
        "subscribers_count": t[4]["subscribers_count"],
        "total_videos": t[4]["total_videos"],
        "sort_by": sort_by,
        "proxy": proxy
    })

@app.get("/playlist", response_class=HTMLResponse)
def playlist(list: str, response: Response, request: Request, page: Union[int, None] = 1, yuki: Union[str] = Cookie(None), proxy: Union[str] = Cookie(None)):
    if not checkCookie(yuki):
        return redirect("/")
    response.set_cookie("yuki", "True", max_age=60 * 60 * 24 * 7)
    results, has_next = getPlaylistData(list, str(page))
    return template("search.html", {
        "request": request,
        "results": results,
        "word": "",
        "page": page,
        "next": f"/playlist?list={list}&page={page + 1}" if has_next else None,
        "prev": f"/playlist?list={list}&page={page - 1}" if page > 1 else None,
        "proxy": proxy
    })

@app.get("/comments")
def comments(request: Request, v:str):
    return template("comments.html", {"request": request, "comments": getCommentsData(v)})

@app.get("/thumbnail")
def thumbnail(v:str):
    return Response(content = requests.get(f"https://img.youtube.com/vi/{v}/0.jpg").content, media_type=r"image/jpeg")

@app.get("/suggest")
def suggest(keyword:str):
    return [i[0] for i in json.loads(requests.get("http://www.google.com/complete/search?client=youtube&hl=ja&ds=yt&q=" + urllib.parse.quote(keyword), headers=getRandomUserAgent()).text[19:-1])[1]]

@cache(seconds=120)
def getSource(name):
    return requests.get(f'https://raw.githubusercontent.com/LunaKamituki/yuki-source/refs/heads/main/{name}.html', headers=getRandomUserAgent()).text

@app.get("/bbs", response_class=HTMLResponse)
def bbs(request: Request, name: Union[str, None] = "", seed:Union[str, None]="", channel:Union[str, None]="main", verify:Union[str, None]="false", yuki: Union[str] = Cookie(None)):
    if not(checkCookie(yuki)):
        return redirect("/")
    res = HTMLResponse(no_robot_meta_tag + requests.get(f"{url}bbs?name={urllib.parse.quote(name)}&seed={urllib.parse.quote(seed)}&channel={urllib.parse.quote(channel)}&verify={urllib.parse.quote(verify)}", cookies={"yuki":"True"}).text.replace('AutoLink(xhr.responseText);', 'urlConvertToLink(xhr.responseText);') + getSource('bbs'))
    return res

@cache(seconds=5)
def getCachedBBSAPI(verify, channel):
    return requests.get(f"{url}bbs/api?t={urllib.parse.quote(str(int(time.time()*1000)))}&verify={urllib.parse.quote(verify)}&channel={urllib.parse.quote(channel)}", cookies={"yuki":"True"}).text

@app.get("/bbs/api", response_class=HTMLResponse)
def bbsAPI(request: Request, t: str, channel:Union[str, None]="main", verify: Union[str, None] = "false"):
    return getCachedBBSAPI(verify, channel)

@app.get("/bbs/result")
def write_bbs(request: Request, name: str = "", message: str = "", seed:Union[str, None] = "", channel:Union[str, None]="main", verify:Union[str, None]="false", yuki: Union[str] = Cookie(None)):
    if not(checkCookie(yuki)):
        return redirect("/")
    if 'Google-Apps-Script' in str(request.scope["headers"][1][1]):
        raise UnallowedBot("GASのBotは許可されていません")
      
    params = {
      'name': urllib.parse.quote(name),
      'message': urllib.parse.quote(message),
      'seed': urllib.parse.quote(seed),
      'channel': urllib.parse.quote(channel),
      'verify': urllib.parse.quote(verify),
      'info': urllib.parse.quote(getInfo(request)),
      'serververify': getVerifyCode()
    }
  
    url_querys = ''
    for key, value in params.items():
      url_querys += f'{key}={value}&'

    if url_querys != '':
      url_querys = '?' + url_querys[:-1]
      
    t = requests.get(f"{url}bbs/result" + url_querys, cookies={"yuki": "True"}, allow_redirects=False)
    if t.status_code != 307:
        return HTMLResponse(no_robot_meta_tag + t.text.replace('AutoLink(xhr.responseText);', 'urlConvertToLink(xhr.responseText);') + getSource('bbs'))
        
    return redirect(f"/bbs?name={urllib.parse.quote(name)}&seed={urllib.parse.quote(seed)}&channel={urllib.parse.quote(channel)}&verify={urllib.parse.quote(verify)}")

@cache(seconds=120)
def getCachedBBSHow():
    return requests.get(f"{url}bbs/how").text

@app.get("/bbs/how", response_class=PlainTextResponse)
def view_commonds(request: Request, yuki: Union[str] = Cookie(None)):
    if not(checkCookie(yuki)):
        return redirect("/")
    return getCachedBBSHow()



@app.get("/info", response_class=HTMLResponse)
def viewlist(response: Response, request: Request, yuki: Union[str] = Cookie(None)):
    if not(checkCookie(yuki)):
        return redirect("/")
    response.set_cookie("yuki", "True", max_age=60 * 60 * 24 * 7)
    
    return template("info.html", {"request": request, "Youtube_API": invidious_api.video[0], "Channel_API": invidious_api.channel[0], "comments": invidious_api.comments[0]})

@app.get("/reset", response_class=PlainTextResponse)
def home():
    global url, invidious_api
    url = requests.get('https://raw.githubusercontent.com/yuto1106110/yuto-yuki-youtube-1/main/APItati', headers=getRandomUserAgent()).text.rstrip()
    invidious_api = InvidiousAPI()
    return 'Success'

@app.get("/version", response_class=PlainTextResponse)
def displayVersion():
    return str({'version': version, 'new_instance_version': new_instance_version})

@app.get("/api/update", response_class=PlainTextResponse)
def updateAllAPI():
  global invidious_api
  return str((invidious_api := InvidiousAPI()).info())

@app.get("/api/{api_name}", response_class=PlainTextResponse)
def displayAPI(api_name: str):
  
  match api_name:
    case 'all':
      api_value = invidious_api.info()
        
    case 'video':
      api_value = invidious_api.video
  
    case 'search':
      api_value = invidious_api.search
  
    case 'channel':
      api_value = invidious_api.channel
  
    case 'comments':
      api_value = invidious_api.comments

    case 'playlist':
      api_value = invidious_api.playlist
      
    case _:
      api_value = f'API Name Error: {api_name}'
        
  return str(api_value)
    
@app.get("/api/{api_name}/next", response_class=PlainTextResponse)
def rotateAPI(api_name: str):
  match api_name:
    case 'video':
      updateList(invidious_api.video, invidious_api.video[0])
  
    case 'search':
      updateList(invidious_api.search, invidious_api.search[0])
  
    case 'channel':
      updateList(invidious_api.channel, invidious_api.channel[0])
  
    case 'comments':
      updateList(invidious_api.comments, invidious_api.comments[0])

    case 'playlist':
      updateList(invidious_api.playlist, invidious_api.playlist[0])

    case _:
      return f'API Name Error: {api_name}'
        
  return 'Finish'
    
@app.get("/api/video/check", response_class=PlainTextResponse)
def displayCheckVideo():
    return str(invidious_api.check_video)

@app.get("/api/video/check/toggle", response_class=PlainTextResponse)
def toggleVideoCheck():
    global invidious_api
    invidious_api.check_video = not invidious_api.check_video
    return f'{not invidious_api.check_video} to {invidious_api.check_video}'
@app.get("/help", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("help.html", {"request": request})
  
@app.get("/proxypage", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("proxy.html", {"request": request})

@app.get("/url", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("url.html", {"request": request})

@app.get("/light", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("light.html", {"request": request})
@app.get("/sitsumon", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("otoiawase.html", {"request": request})
@app.get("/news", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("news.html", {"request": request})
@app.get("/space", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("space.html", {"request": request})
@app.get("/update", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("update.html", {"request": request})
@app.get("/others", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("others.html", {"request": request})
@app.get("/qanda", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("Q&A.html", {"request": request})
@app.get("/1v1lol", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("1v1-lol.html", {"request": request})
@app.get("/drive", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("drive.html", {"request": request})
@app.get("/paper", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("paper.html", {"request": request})
@app.get("/snow", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("snow.html", {"request": request})
@app.get("/2048", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("block.html", {"request": request})
@app.get("/ose", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("ose.html", {"request": request})
@app.get("/game", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("game.html", {"request": request})
@app.get("/and", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("android.html", {"request": request})
@app.get("/cone", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("cone.html", {"request": request})
@app.get("/usa", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("usa.html", {"request": request})
@app.get("/chat", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("chat.html", {"request": request})
@app.get("/ball", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("ball.html", {"request": request})
@app.get("/bj", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("bj.html", {"request": request})
@app.get("/tools", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("tools.html", {"request": request})
@app.get("/news", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("news.html", {"request": request})
@app.get("/re", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("re.html", {"request": request})
@app.get("/among", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("among.html", {"request": request})
@app.get("/among-1", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("among-1.html", {"request": request})
@app.get("/among-2", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("among-2.html", {"request": request})
@app.get("/interland", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("interland.html", {"request": request})
@app.get("/denki", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("denki.html", {"request": request})
@app.get("/dog", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("dog.html", {"request": request})
@app.get("/dash", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("dash.html", {"request": request})
@app.get("/dairan", response_class=HTMLResponse)
def list_page(response: Response, request: Request):
    return template("dairan.html", {"request": request})

@app.exception_handler(500)
async def error500(request: Request, exc):
    return template("error.html", {"request": request, "context": '500 Internal Server Error'}, status_code=500)

@app.exception_handler(404)
async def error404(request: Request, exc):
    return template("error.html", {"request": request, "context": '404 Error、あれれ'}, status_code=404)

@app.exception_handler(APITimeoutError)
async def apiWait(request: Request, exception: APITimeoutError):
    return template("apiTimeout.html", {"request": request}, status_code=504)

@app.exception_handler(UnallowedBot)
async def returnToUnallowedBot(request: Request, exception: UnallowedBot):
    return template("error.html", {"request": request, "context": '403 Forbidden'}, status_code=403)
