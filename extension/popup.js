document.addEventListener('DOMContentLoaded', async () => {
    const urlInput = document.getElementById('url');
    const form = document.getElementById('dl-form');
    const statusDiv = document.getElementById('status');

    // 開いたタブのURLを自動取得
    try {
        let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (tab && tab.url) {
            urlInput.value = tab.url;
        }
    } catch (e) {
        console.log("Not running as extension, URL auto-fill skipped.");
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const targetUrl = urlInput.value;
        const format = document.getElementById('format').value;

        // UIを処理中状態に
        statusDiv.textContent = "API(v10)で解析中...";
        statusDiv.style.color = "#94a3b8";
        statusDiv.classList.remove('hidden');

        // 直リンクのバイパス処理（前回仕込んだ神機能はそのままキープ！）
        const lowerUrl = targetUrl.toLowerCase();
        if (lowerUrl.includes('.mp4') || lowerUrl.includes('.webm')) {
            statusDiv.textContent = "✨ 直リンクを検出！APIを通さず直接ダウンロードします。";
            statusDiv.style.color = "#22d3ee";
            chrome.downloads.download({ url: targetUrl, saveAs: false });
            return;
        }

        try {
            // Cobalt v10 APIの最新仕様に合わせたデータ構造
            const payload = { url: targetUrl };
            if (format === 'mp3') {
                payload.downloadMode = 'audio'; // v10仕様の音声抽出コマンド
            }

            // v10の公式エンドポイント
            // ※もし将来公式が落ちたら、ここを 'https://cobalt.qwy2.dev/' などの有志サーバーに変えるだけで復活します
            const apiUrl = 'http://127.0.0.1:8000'; 

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            let data;
            try {
                data = await response.json();
            } catch (parseError) {
                throw new Error(`サーバーから不正な応答がありました (HTTP ${response.status})`);
            }

            // Cobalt v10仕様のエラーハンドリング
            if (!response.ok || data.status === 'error') {
                // v10はエラー理由を data.error.code に入れてくることがある
                const errorMsg = (data.error && data.error.code) ? data.error.code : (data.text || `HTTP ${response.status}`);
                throw new Error(errorMsg);
            }
            
            statusDiv.textContent = "✨ ダウンロードを開始しました！";
            statusDiv.style.color = "#22d3ee";

            // ChromeのネイティブAPIでダウンロード実行（v10は直接urlを返してくる）
            chrome.downloads.download({
                url: data.url,
                saveAs: false
            });

        } catch (error) {
            statusDiv.textContent = `🚨 エラー: ${error.message}`;
            statusDiv.style.color = "#f87171";
            console.error("Fetch/Cobalt Error:", error);
        }
    });
});
