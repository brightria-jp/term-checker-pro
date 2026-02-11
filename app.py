import streamlit as st
import streamlit.components.v1 as components

# 1. ページの設定
st.set_page_config(
    page_title="TermChecker PRO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 画面レイアウト固定・スクロール制御
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

# 3. HTMLコード (添付いただいたロジックを100%移植)
html_code = r'''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TermChecker PRO - Precision Overlay</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #2563eb; --danger: #ef4444; --warning: #f59e0b;
            --bg: #f8fafc; --card: #ffffff; --text-main: #1e293b;
            --text-sub: #64748b; --border: #e2e8f0; --shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        }

        * { box-sizing: border-box; font-family: 'Inter', 'Noto Sans JP', sans-serif; }
        body { background: var(--bg); color: var(--text-main); margin: 0; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
        
        /* モーダル：同意ボタンの活性化制御 */
        #consentModal { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(12px); z-index: 9999; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .modal-content { background: white; padding: 2.5rem; border-radius: 28px; max-width: 620px; width: 100%; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); animation: modalUp 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
        @keyframes modalUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        .scroll-terms { height: 250px; overflow-y: auto; background: #f1f5f9; padding: 1.5rem; border-radius: 16px; font-size: 0.85rem; line-height: 1.8; color: var(--text-sub); margin: 1.5rem 0; border: 1px solid var(--border); }

        header { background: #fff; border-bottom: 1px solid var(--border); padding: 0.8rem 2rem; display: flex; justify-content: space-between; align-items: center; z-index: 100; height: 65px; }
        .logo { font-size: 1.2rem; font-weight: 800; color: var(--primary); display: flex; align-items: center; gap: 8px; }

        main { display: flex; flex: 1; overflow: hidden; padding: 1.5rem; gap: 1.5rem; }
        
        /* 左右 50:50 の比率 */
        .panel-left { flex: 1; display: flex; flex-direction: column; gap: 1rem; position: relative; overflow: hidden; }
        .panel-right { flex: 1; display: flex; flex-direction: column; gap: 1.5rem; overflow-y: auto; }
        
        .editor-card { flex: 1; background: white; border-radius: 24px; border: 1px solid var(--border); box-shadow: var(--shadow); display: flex; flex-direction: column; position: relative; overflow: hidden; }
        .container-box { position: relative; flex: 1; overflow: hidden; margin: 70px 0; background: #fff; }
        
        textarea, #highlightOverlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            padding: 24px !important; font-size: 16px !important; line-height: 1.8 !important;
            font-family: 'Inter', 'Noto Sans JP', sans-serif !important; white-space: pre-wrap !important;
            word-wrap: break-word !important; margin: 0 !important; border: none !important; outline: none !important;
            box-sizing: border-box !important; letter-spacing: normal !important;
        }
        textarea { z-index: 2; background: transparent !important; color: #334155; resize: none; -webkit-text-fill-color: currentColor; }
        #highlightOverlay { z-index: 1; color: transparent !important; pointer-events: none; overflow-y: auto; background: white; }
        .hl { color: transparent !important; background-color: rgba(239, 68, 68, 0.2); border-bottom: 2px solid var(--danger); font-weight: 800; }

        .btn { display: inline-flex; align-items: center; justify-content: center; height: 48px; padding: 0 1.5rem; border-radius: 12px; font-weight: 700; cursor: pointer; transition: 0.2s; border: 1px solid var(--border); background: #fff; line-height: 1; }
        .btn-primary { background: var(--primary); color: white; border: none; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2); }
        .btn-primary:disabled { background-color: #94a3b8; opacity: 0.6; cursor: not-allowed; box-shadow: none; }

        .toolbar, .actionbar { height: 70px; padding: 0 1.5rem; display: flex; align-items: center; background: white; width: 100%; z-index: 10; position: absolute; }
        .toolbar { border-bottom: 1px solid var(--border); top: 0; gap: 12px; }
        .actionbar { border-top: 1px solid var(--border); bottom: 0; justify-content: space-between; }

        .risk-card { padding: 1.5rem; border-radius: 24px; color: white; box-shadow: var(--shadow); }
        .risk-card.high { background: linear-gradient(135deg, #ef4444, #b91c1c); }
        .risk-card.mid { background: linear-gradient(135deg, #f59e0b, #d97706); }
        .risk-card.low { background: linear-gradient(135deg, #10b981, #059669); }
        .risk-val { font-size: 2.6rem; font-weight: 800; margin: 5px 0; }

        .analysis-item { background: white; border-radius: 20px; border: 1px solid var(--border); padding: 1.5rem; margin-bottom: 1rem; }
        .clause-badge { background: var(--primary); color: white; padding: 2px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 800; margin-bottom: 8px; display: inline-block; }
        .verbatim-text { font-size: 0.85rem; color: #334155; background: #fff5f5; padding: 10px; border-left: 4px solid var(--danger); border-radius: 4px; line-height: 1.6; margin-top: 10px; }

        .hidden { display: none; }
    </style>
</head>
<body>

<div id="consentModal">
    <div class="modal-content">
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 10px;">⚖️</div>
            <h2 style="margin: 0; font-weight: 800;">ご利用前の承諾事項</h2>
        </div>
        <div class="scroll-terms">
            <p><b>1. 本サービスの目的</b><br>本ツールは、AIによる自然言語処理を用いて利用規約内の一般的なリスクを抽出する補助ツールです。情報の正確性や完全性を保証するものではありません。</p>
            <p><b>2. 法的助言の否定</b><br>本ツールの解析結果は法的助言を構成しません。個別の事案については、必ず弁護士等の専門家にご相談ください。本ツールの利用により生じた損害について、提供者は一切の責任を負いません。</p>
            <p><b>3. PDF解析の限界</b><br>PDFファイルの構造により、テキストが正しく抽出されない場合や、条文番号が誤認される場合があります。必ず元の文章と照らし合わせて確認してください。</p>
            <p><b>4. プライバシーとデータ</b><br>入力されたテキストはブラウザ上での解析にのみ使用され、サーバー側で保存されることはありません。</p>
            <p><b>5. 同意の確認</b><br>本ツールの利用を開始することで、上記全ての免責事項に同意したものとみなされます。判断は全て自己責任において行ってください。</p>
        </div>
        <label style="display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 1.5rem; font-weight: 700; cursor: pointer;">
            <input type="checkbox" id="consentCheck" style="transform: scale(1.3);" onchange="document.getElementById('startBtn').disabled = !this.checked">
            <span>免責事項を理解し、自己責任で利用することに同意します</span>
        </label>
        <button id="startBtn" class="btn btn-primary" style="width: 100%; height: 56px; font-size: 1.1rem;" onclick="document.getElementById('consentModal').style.display='none'" disabled>同意して解析を開始する</button>
    </div>
</div>

<header><div class="logo">⚖️ TermChecker <span>PRO</span></div></header>

<main>
    <section class="panel-left">
        <div class="editor-card">
            <div class="toolbar">
                <button class="btn" onclick="document.getElementById('fileInput').click()">＋ PDF/TXTを読み込む</button>
                <input type="file" id="fileInput" class="hidden" accept=".pdf,.txt">
            </div>
            <div class="container-box">
                <div id="highlightOverlay"></div>
                <textarea id="inputText" onscroll="syncScroll()" oninput="handleInput()" placeholder="規約を貼り付けてください..."></textarea>
            </div>
            <div class="actionbar">
                <button class="btn" onclick="loadSample()">サンプル</button>
                <button class="btn btn-primary" style="min-width: 200px;" onclick="runAnalysis()">規約を解析する</button>
            </div>
        </div>
    </section>

    <section class="panel-right">
        <div id="emptyState" style="text-align: center; margin-top: 10rem; opacity: 0.4;"><p>解析結果が表示されます</p></div>
        <div id="resultsUI" class="hidden">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                <div id="riskCard" class="risk-card">
                    <span style="font-size: 0.75rem; font-weight: 800; opacity: 0.9;">TOTAL RISK</span>
                    <div id="riskLevel" class="risk-val">---</div>
                </div>
                <div class="risk-card" style="background: #1e293b;">
                    <span style="font-size: 0.75rem; font-weight: 800; opacity: 0.9;">ALERTS</span>
                    <div id="matchCount" class="risk-val">0</div>
                </div>
            </div>
            <h3 style="margin-top: 2rem; font-weight: 800;">🚩 重点確認項目 (条文特定済み)</h3>
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
                    if (lastY !== -1 && Math.abs(lastY - item.transform[5]) > 12) fullText += "\n";
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

    // リスク判定辞書（添付いただいたHTMLファイルを100%再現）
    const DICT = [
        { name: '返金不可・制限', weight: 15, patterns: ["返金", "致しません", "不可", "応じない", "戻りません", "キャンセル料"], desc: '支払った料金が戻らない条項です。' },
        { name: '不利益な自動更新', weight: 12, patterns: ["自動更新", "更新する", "自動的に", "解約しない限り"], desc: '手続きを忘れると契約が継続されるリスクがあります。' },
        { name: '広範な免責事項', weight: 10, patterns: ["一切の責任を負わない", "免責", "保証しません", "補償いたしません"], desc: '運営側のミスでも責任を逃れる可能性がある条項です。' },
        { name: '著作権の譲渡・利用', weight: 8, patterns: ["著作権", "帰属", "無償で利用", "当社に許諾"], desc: '投稿内容を自由に使う権利に関する条項です。' },
        { name: '規約変更・管轄', weight: 7, patterns: ["予告なく変更", "合意管轄", "裁判所"], desc: 'ルール変更やトラブル時の裁判場所に注意。' }
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
                    
                    if (m.length > 0 && fullSentence.length > 2) {
                        const clauseName = m[m.length - 1][0].replace(/\s/g, '');
                        matches.push({ clause: clauseName, text: fullSentence });
                        sentencesToHighlight.push(fullSentence);
                    }
                    idx = text.indexOf(p, idx + 1);
                }
            });

            if(matches.length > 0) {
                const uniqueMatches = matches.filter((v, i, a) => a.findIndex(t => (t.clause === v.clause && t.text === v.text)) === i);
                score += item.weight;
                results.push({ ...item, items: uniqueMatches });
            }
        });

        const uniqueSentences = [...new Set(sentencesToHighlight)].sort((a,b) => b.length - a.length);
        uniqueSentences.forEach(s => {
            const escapedS = s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
            if(escapedS.length < 3) return;
            const reg = new RegExp(escapedS.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&'), 'g');
            htmlContent = htmlContent.replace(reg, `<span class="hl">${escapedS}</span>`);
        });

        $('highlightOverlay').innerHTML = htmlContent + "\n\n ";
        render(score, results);
        syncScroll();
    }

    function render(score, items) {
        $('emptyState').classList.add('hidden');
        $('resultsUI').classList.remove('hidden');
        const card = $('riskCard');
        
        // 判定基準：25点以上でHIGH、12点以上でMID
        if(score >= 25) { card.className='risk-card high'; $('riskLevel').textContent='HIGH'; }
        else if(score >= 12) { card.className='risk-card mid'; $('riskLevel').textContent='MID'; }
        else { card.className='risk-card low'; $('riskLevel').textContent='LOW'; }
        
        $('matchCount').textContent = items.length;
        $('analysisList').innerHTML = items.map(category => `
            <div class="analysis-item">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:800; font-size:1.1rem;">${category.name}</span>
                    <span style="background:#f1f5f9; color:var(--primary); font-size:0.75rem; padding:4px 10px; border-radius:6px; font-weight:800;">Risk: ${category.weight}</span>
                </div>
                <p style="font-size:0.85rem; color:var(--text-sub); margin: 5px 0 10px 0;">${category.desc}</p>
                ${category.items.map(it => `
                    <div style="margin-bottom:12px;">
                        <span class="clause-badge">${it.clause}</span>
                        <div class="verbatim-text">${it.text}</div>
                    </div>
                `).join('')}
            </div>
        `).join('');
    }

    function loadSample() {
        $('inputText').value = "第5条（更新）本サービスは自動更新されます。本契約は、期間満了までに解約の申し出がない限り自動的に更新されます。\n第12条（免責）当社は損害について一切の責任を負わないものとします。理由の如何を問わず、一度支払われた料金の返金には一切応じません。";
        handleInput();
    }
</script>
</body>
</html>
'''

# 表示
components.html(html_code)
