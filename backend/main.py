import os
import platform
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp

app = FastAPI(
    title="SleekDL API",
    description="Backend for the SleekDL browser extension.",
    version="1.0.0"
)

# ---------------------------------------------------------
# CORS設定 (ブラウザ拡張機能からローカルサーバーを叩くために必須)
# FIXME: 今はガバガバの"*"にしてるけど、公開時は拡張機能のIDで絞るべき（忘れないこと！）
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# リクエストのデータ構造を定義
class DownloadRequest(BaseModel):
    url: str
    format: str = "mp4_1080" # デフォルト値

# OSごとの「ダウンロード」フォルダのパスを雑に取得する関数
def get_download_path():
    if platform.system() == "Windows":
        return os.path.join(os.environ['USERPROFILE'], 'Downloads')
    else:
        return os.path.join(os.path.expanduser('~'), 'Downloads')

# 実際のダウンロード処理（重いので裏で回す用）
def process_download(url: str, format_type: str):
    dl_path = get_download_path()
    print(f"[*] Starting download for: {url}")
    print(f"[*] Target directory: {dl_path}")

    # yt-dlpのオプション設定
    ydl_opts = {
        'outtmpl': os.path.join(dl_path, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': False, # ターミナルで進捗を見たいからFalseにする
        'extractor_args': {'generic': ['impersonate']},
    }

    # フォーマットによる条件分岐（実務っぽい泥臭さ）
    if format_type == "mp3":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        # とりあえず最高画質（mp4）を狙う
        ydl_opts.update({
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("[+] Download completed successfully!")
    except Exception as e:
        # TODO: エラーログをちゃんとファイルに吐くようにする
        print(f"[!] Download failed: {e}")

@app.post("/api/download")
async def trigger_download(req: DownloadRequest, background_tasks: BackgroundTasks):
    # バリデーション（人が書いたっぽい簡単なチェック）
    if not req.url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL format. C'mon, give me a real link.")

    # FastAPIのBackgroundTasksを使って、APIのレスポンスは即座に返しつつ裏でダウンロードを開始する
    # これをやらないと、ブラウザ側がタイムアウトしちゃう
    background_tasks.add_task(process_download, req.url, req.format)

    return {
        "status": "success",
        "message": "Download process started in the background.",
        "target_url": req.url
    }
