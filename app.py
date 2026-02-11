import streamlit as st
import streamlit.components.v1 as components

# 1. ページの設定（余白をゼロにする）
st.set_page_config(
    page_title="TermChecker PRO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Streamlit自体のスクロールを抑制し、iframeを画面いっぱいに広げるCSS
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0px; height: 100vh;}
    iframe {position: fixed; top: 0; left: 0; width: 100%; height: 100% !important; border: none;}
    body {overflow: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. HTMLコードを変数に格納
html_code = r'''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TermChecker PRO</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #2563eb; --danger: #ef4444; --bg: #f8fafc; --card: #ffffff;
            --text-main: #1e293b; --text-sub: #64748b; --border: #e2e8f0;
        }

        * { box-sizing: border-box; font-family: 'Inter', 'Noto Sans JP', sans-serif; }
        
        /* 画面全体の高さを100%に固定し、はみ出しを禁止 */
        html, body { height: 100%; margin: 0; overflow: hidden; background: var(--bg); }
        
        /* ヘッダー固定 */
        header { background: #fff; border-bottom: 1px solid var(--border); padding: 0 2rem; height: 60px; display: flex; align-items: center; flex-shrink: 0; }
        .logo { font-size: 1.2rem; font-weight: 800; color: var(--primary); }

        /* メインエリアのレイアウト固定 */
        main { display: flex; height: calc(100% - 60px); padding: 1rem; gap: 1rem; overflow: hidden; }
        
        /* 左パネル：エディタ */
        .panel-left { flex: 1; display: flex; flex-direction: column; height: 100%; overflow: hidden; }
        .editor-card { 
            flex: 1; background: white; border-radius: 16px; border: 1px solid var(--border); 
            display: flex; flex-direction: column; overflow: hidden; position: relative;
        }
        
        /* 上下のバーを固定 */
        .toolbar { height: 60px; padding: 0 1rem; display: flex; align-items: center; background: white; border-bottom: 1px solid var(--border); flex-shrink: 0; }
        .actionbar { height: 60px; padding: 0 1rem; display: flex; align-items: center; justify-content: space-between; background: white; border-top: 1px solid var(--border); flex-shrink: 0; }

        /* スクロールエリアの固定：ここが重要 */
        .container-box { flex: 1; position: relative; overflow: hidden; background: #fff; }
        
        textarea, #highlightOverlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            padding: 24px !important; font-size: 16px !important; line-height: 1.8 !important;
            white-space: pre-wrap !important; word-wrap: break-word !important;
            margin: 0 !important; border: none !important; outline: none !important;
        }
        textarea { z-index: 2; background: transparent !important; color: #334155; resize: none; overflow-y: auto; }
        #highlightOverlay { z-index: 1; color: transparent !important; overflow-y: auto; }
        .hl { background-color: rgba(239, 68, 68, 0.15); border-bottom: 2px solid var(--danger); }

        /* 右パネル：解析結果 */
        .panel-right { width: 450px; display: flex; flex-direction: column; gap: 1rem; height: 100%; overflow-y: auto; padding-right: 5px; }
        
        /* モーダル */
        #consentModal { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(8px); z-index: 10000; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .modal-content { background: white; padding: 2rem; border-radius: 24px; max-width: 600px; width: 100%; }
        .scroll-terms { height: 200px; overflow-y: auto; background: #f1f5f9; padding: 1rem; border-radius: 12px; font-size: 0.85rem; line-height: 1.7; margin: 1rem 0; border: 1px solid var(--border); }

        .btn { padding: 0 1rem; height: 40px; border-radius: 8px; font-weight: 700; cursor: pointer; border: 1px solid var(--border); background: #fff; }
        .btn-primary { background: var(--primary); color: white; border: none; }
        .hidden { display: none; }
        .analysis-item { background: white; border-radius: 16px; border: 1px solid var(--border); padding: 1.2rem; margin-bottom: 1rem; }
        .verbatim-text { font-size: 0.85rem; background: #fff5f5; padding: 10px; border-left: 4px solid var(--danger); margin-top: 8px; border-radius: 4px; }
    </style>
</head>
<body>

<div id="consentModal">
    <div class="modal-content">
        <h2 style="text-align:center; margin-top:0;">⚖️ ご利用前の承諾事項</h2>
        <div class="scroll-terms">
            <p><b>1. 本サービスの目的</b><br>AIを用いた補助ツールであり、正確性を保証しません。</p>
            <p><b>2. 法的助言の否定</b><br>法的助言ではありません。専門家にご相談ください。</p>
            <p><b>3. PDF解析の限界</b><br>構造によりテキスト抽出が不完全になる場合があります。</p>
            <p><b>4. プライバシー</b><br>データはブラウザ内でのみ処理され、保存されません。</p>
            <p><b>5. 同意の確認</b><br>利用開始により、全ての免責事項に同意したものとみなされます。</p>
        </div>
        <label style="display:flex; align-items:center; gap:10px; margin-bottom:1.5rem; cursor:pointer;">
            <input type="checkbox" id="consentCheck" onchange="document.getElementById('startBtn').disabled = !this.checked">
            <span style="font-size:0.9rem;">免責事項に同意し、自己責任で利用します</span>
        </label>
        <button id="startBtn" class="btn btn-primary" style="width:100%; height:48px;" onclick="document.getElementById('consentModal').style.display='none'" disabled>解析を開始する</button>
    </div>
</div>

<header><div class="logo">⚖️ TermChecker PRO</div></header>

<main>
    <section class="panel-left">
        <div class="editor-card">
            <div class="toolbar">
                <button class="btn" onclick="document.getElementById('fileInput').click()">＋ PDF/TXTを読み込む</button>
                <input type="file" id="fileInput" class="hidden" accept=".pdf,.txt">
            </div>
            <div class="container-box">
                <div id="highlightOverlay"></div>
                <textarea id="inputText" onscroll="syncScroll()" oninput="handleInput()" placeholder="ここに規約を貼り付けるか、ファイルを読み込んでください..."></textarea>
            </div>
            <div class="actionbar">
                <button class="btn" onclick="loadSample()">サンプル</button>
                <button class="btn btn-primary" style="min-width: 150px;" onclick="runAnalysis()">解析実行</button>
            </div>
        </div>
    </section>

    <section class="panel-right">
        <div id="emptyState" style="text-align:center; margin-top:5rem; color:var(--text-sub);">
            解析結果がここに表示されます
        </div>
        <div id="resultsUI" class="hidden">
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                <div id="riskCard" style="padding:1rem; border-radius:12px; color:white; background:var(--primary);">
                    <div style="font-size:0.7rem; font-weight:800;">TOTAL RISK</div>
                    <div id="riskLevel" style="font-size:1.5rem; font-weight:800;">---</div>
                </div>
                <div style="padding:1rem; border-radius:12px; color:white; background:#1e293b;">
                    <div style="font-size:0.7rem; font-weight:800;">ALERTS</div>
                    <div id="matchCount" style="font-size:1.5rem; font-weight:800;">0</div>
                </div>
            </div>
            <h3 style="font-size:1rem;">🚩 重点確認項目 (条文特定済み)</h3>
            <div id="analysisList"></div>
        </div>
    </section>
</main>

<script>
    const $ = (id) => document.getElementById(id);
    const pdfjsLib = window['pdfjs-dist/build/pdf'];
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

    function syncScroll() {
        $('highlightOverlay').scrollTop = $('inputText').scrollTop;
    }

    function handleInput() {
        $('highlightOverlay').textContent = $('inputText').value;
        syncScroll();
    }

    document.getElementById('fileInput').onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        if (file.type === 'application/pdf') {
            const pdf = await pdfjsLib.getDocument({data: await file.arrayBuffer()}).promise;
            let fullText = "";
            for (let i = 1; i <= pdf.numPages; i++) {
                const page = await pdf.getPage(i);
                const content = await page.getTextContent();
                let lastY = -1;
                content.items.forEach(item => {
                    if (lastY !== -1 && Math.abs(lastY - item.transform[5]) > 10) fullText += "\n";
                    fullText += item.str;
                    lastY = item.transform[5];
                });
                fullText += "\n\n";
            }
            $('inputText').value = fullText;
        } else {
            const reader = new FileReader();
            reader.onload = (ev) => $('inputText').value = ev.target.result;
            reader.readAsText(file);
        }
        handleInput();
    };

    const DICT = [
        { name: '返金不可・制限', weight: 15, patterns: ["返金", "致しません", "不可", "応じない", "戻りません"], desc: '支払った料金が戻らない条項です。' },
        { name: '不利益な自動更新', weight: 12, patterns: ["自動更新", "更新する", "自動的に", "解約しない限り"], desc: '手続きを忘れると継続されるリスク。' },
        { name: '免責事項', weight: 10, patterns: ["一切の責任を負わない", "免責", "保証しません"], desc: '運営側が責任を負わないとする条項。' }
    ];

    function runAnalysis() {
        const text = $('inputText').value;
        if(!text) return;
        let htmlContent = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        const results = [];
        let score = 0;
        let sentencesToHighlight = [];

        DICT.forEach(item => {
            let matches = [];
            item.patterns.forEach(p => {
                let idx = text.indexOf(p);
                while(idx !== -1) {
                    const startIdx = text.lastIndexOf("。", idx) + 1;
                    let endIdx = text.indexOf("。", idx);
                    if (endIdx === -1) endIdx = text.length;
                    const fullSentence = text.substring(startIdx, endIdx + 1).trim();
                    const sub = text.substring(0, idx);
                    const m = [...sub.matchAll(/第\s*\d+\s*条/g)];
                    if (m.length > 0) {
                        const clauseName = m[m.length - 1][0].replace(/\s/g, '');
                        matches.push({ clause: clauseName, text: fullSentence });
                        sentencesToHighlight.push(fullSentence);
                    }
                    idx = text.indexOf(p, idx + 1);
                }
            });
            if(matches.length > 0) {
                const uniqueItems = matches.filter((v, i, a) => a.findIndex(t => (t.text === v.text)) === i);
                score += item.weight;
                results.push({ ...item, items: uniqueItems });
            }
        });

        const uniqueSentences = [...new Set(sentencesToHighlight)].sort((a,b) => b.length - a.length);
        uniqueSentences.forEach(s => {
            const escapedS = s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
            const reg = new RegExp(escapedS.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&'), 'g');
            htmlContent = htmlContent.replace(reg, `<span class="hl">${escapedS}</span>`);
        });

        $('highlightOverlay').innerHTML = htmlContent + "\n\n ";
        render(score, results);
    }

    function render(score, items) {
        $('emptyState').classList.add('hidden');
        $('resultsUI').classList.remove('hidden');
        const card = $('riskCard');
        if(score >= 25) { card.style.background='#ef4444'; $('riskLevel').textContent='HIGH'; }
        else if(score >= 12) { card.style.background='#f59e0b'; $('riskLevel').textContent='MID'; }
        else { card.style.background='#10b981'; $('riskLevel').textContent='LOW'; }
        $('matchCount').textContent = items.length;
        $('analysisList').innerHTML = items.map(category => `
            <div class="analysis-item">
                <span style="font-weight:800;">${category.name}</span>
                <p style="font-size:0.8rem; color:var(--text-sub); margin:4px 0;">${category.desc}</p>
                ${category.items.map(it => `
                    <div style="margin-top:8px;">
                        <span style="font-size:0.7rem; background:var(--primary); color:white; padding:2px 6px; border-radius:4px;">${it.clause}</span>
                        <div class="verbatim-text">${it.text}</div>
                    </div>
                `).join('')}
            </div>
        `).join('');
    }

    function loadSample() {
        $('inputText').value = "第5条（更新）本サービスは自動更新されます。期間満了までに解約の申し出がない限り自動的に更新されます。\n第12条（免責）当社は一切の責任を負わないものとします。";
        handleInput();
    }
</script>
</body>
</html>
'''

# 表示を実行
components.html(html_code)
