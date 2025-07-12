from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

app = Flask(__name__)

# スクレイピングした最新ニュースを保持するグローバル変数
news_data = []

def summarize_text(text, max_length=200):
    """
    文章を max_length 文字以内に切り詰める簡易な要約関数
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def scrape_yahoo_news(limit=5):
    """
    Yahoo!ニュース（例：ピックアップページ）の人気記事をスクレイピングして
    タイトル、要約、URLを抽出する関数

    ※HTML構造に合わせてセレクターを変更してください。
    """
    global news_data
    base_url = "https://news.yahoo.co.jp/pickup"  # Yahoo!ニュース ピックアップページの例
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        # ※下記セレクターはYahoo!ニュースの実際のHTMLに合わせて調整してください
        # ここでは「ul.news-list li.news-item」内に各記事が存在する前提
        news_items = soup.select("ul.news-list li.news-item")
        
        # 先頭から上位 limit 件を抽出
        scraped_news = []
        for item in news_items[:limit]:
            # タイトルとリンクを含む a タグを抽出
            a_tag = item.find("a")
            if not a_tag:
                continue
            
            title = a_tag.get_text(strip=True)
            article_url = a_tag.get("href")
            if article_url and not article_url.startswith("http"):
                article_url = base_url + article_url
            
            # 各記事の内容を取得して要約（記事本文取得はサイトへの負荷に注意）
            try:
                article_response = requests.get(article_url)
                article_response.raise_for_status()
                article_soup = BeautifulSoup(article_response.content, "html.parser")
                # 例：記事本文は複数の p タグに分かれていると仮定
                paragraphs = article_soup.find_all("p")
                content = " ".join([p.get_text(strip=True) for p in paragraphs])
                summary = summarize_text(content, max_length=200)
            except Exception as e:
                summary = "記事の要約を取得できませんでした。"
            
            scraped_news.append({
                "title": title,
                "summary": summary,
                "url": article_url
            })
        
        news_data = scraped_news
        print("Yahoo!ニュースのスクレイピングにより最新情報（上位5件）を更新しました。")
    except Exception as e:
        print("Yahoo!ニュースのスクレイピング中にエラーが発生しました:", e)

# APScheduler で 1 時間ごとにスクレイピングを実行するジョブをセットアップ
scheduler = BackgroundScheduler()
scheduler.add_job(func=lambda: scrape_yahoo_news(limit=5), trigger="interval", hours=1)
scheduler.start()

# アプリ終了時にスケジューラーをクリーンアップ
atexit.register(lambda: scheduler.shutdown())

@app.route("/news")
def news():
    # /news にアクセスされると、最新のスクレイピング結果（上位5件）を表示する
    # ※必要に応じて scrape_yahoo_news(limit=5) をここで呼び出してリロードしてもよい
    return render_template("news.html", news=news_data)

if __name__ == "__main__":
    # 初回実行時にスクレイピングを実施（上位5件のみ）
    scrape_yahoo_news(limit=5)
    app.run(debug=True)
