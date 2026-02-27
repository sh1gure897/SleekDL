# ⚡️ SleekDL - Modern Video Downloader Extension

> A blazingly fast, brutally minimal video downloader bridging a Chrome Extension and a robust Python backend.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)

SleekDLは、「最高に使いやすいモダンなUI」と「絶対にダウンロードを失敗しない強靭なバックエンド」を融合させたProof of Concept（概念実証）プロジェクトです。

## 🤔 Why Backend?

ぶっちゃけ、普通にそれ系の拡張機能をウェブストアから持ってきた方が圧倒的に早いし楽なんですけどね（笑）。

## ✨ Features
- **🎨 Modern UI:** プレーンCSSによる軽量ダークモード。
- **🪄 Auto URL Fetching:** 開いているタブのURLを即座に取得。
- **🛡️ Strong Core:** `yt-dlp` + `curl_cffi` による強力なダウンロードエンジン。

## 🚀 Getting Started

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.02
```

Extension Setup
Chromeの chrome://extensions/ で「デベロッパーモード」をON。

「パッケージ化されていない拡張機能を読み込む」から extension フォルダを選択。
