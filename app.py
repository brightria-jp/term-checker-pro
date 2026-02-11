import streamlit as st
import streamlit.components.v1 as components

# 1. ページの設定
st.set_page_config(
    page_title="TermChecker PRO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 余計な余白をカットするCSS
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0px;}
    iframe {border: none;}
    </style>
    """, unsafe_allow_html=True)

# 3. HTMLコードを変数に格納
html_code = """
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
        
        #consentModal { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(12px); z-index: 9999; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .modal-content { background: white; padding: 2.5rem; border-radius: 28px; max-width: 620px; width: 100%; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); }
        .scroll-terms { height: 250px; overflow-y: auto; background: #f1f5f9; padding: 1.5rem; border-radius: 16px; font-size: 0.85rem; line-height: 1.8; color: var(--text-sub); margin: 1.5rem 0; border: 1px solid var(--border); }

        header { background: #fff; border-bottom: 1px solid var(--border); padding: 0.8rem 2rem; height: 70px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.2rem; font-weight: 800; color: var(--primary); display: flex; align-items: center; gap: 8px; }

        main { display: flex; flex: 1; overflow: hidden; padding: 1.5rem; gap: 1.5rem; }
        .panel-left { flex: 4; display: flex; flex-direction: column; position: relative; }
        .editor-card { flex: 1; background: white; border-radius: 24px; border: 1px solid var(--border); box-shadow: var(--shadow); display: flex; flex-direction: column; overflow: hidden; }
        
        .container-box { position: relative; flex: 1; overflow: hidden; margin-top: 70px; margin-bottom: 70px; background: #fff; }
        
        /* ① 左側テキスト表示箇所の行間修正 */
        textarea, #highlightOverlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            padding: 30px !important; 
            font-size: 16px !important; 
            line-height: 1.8 !important; /* 行間を元ファイルに合わせる */
            font-family: 'Inter', 'Noto Sans JP', sans-serif !important;
            white-space: pre-wrap !important;
            word-wrap: break-word !important;
            margin: 0 !important; border: none !important; outline: none !important;
            box-sizing: border-box !important;
        }

        textarea { z-index: 2; background: transparent !important; color: #334155; resize: none; -webkit-text-fill-color: currentColor; }
        #highlightOverlay { z-index: 1; color: transparent !important; pointer-events: none; overflow-y: auto; background: white; }
        .hl { color: transparent !important; background-color: rgba(239, 68, 68, 0.2); border-bottom: 2px solid var(--danger); font-weight: 800; }

        .toolbar, .actionbar { height: 70px; padding: 0 1.5rem; display: flex; align-items: center; background: white; width: 100%; z-index: 10; position: absolute; }
        .toolbar { border-bottom: 1px solid var(--border); top: 0; gap: 12px; }
        .actionbar { border-top: 1px solid var(--border); bottom: 0; justify-content: space-between; }

        .btn { display: inline-flex; align-items: center; justify-content: center; height: 44px; padding: 0 1.2rem; border-radius: 10px; font-weight: 700; cursor: pointer; border: 1px solid var(--border); background: #fff; }
        .btn-primary { background: var(--primary); color: white; border: none; }

        .panel-right { flex: 5; display: flex; flex-direction: column; gap: 1.5rem; overflow-y: auto; }
        .risk-card { padding: 1.5rem; border-radius: 24px; color: white; }
        .risk-card.high { background: linear-gradient(135deg, #ef4444, #b91c1c); }
        .risk-card.mid { background: linear-gradient(135deg, #f59e0b, #d97706); }
        .risk-card.low { background: linear-gradient(135deg, #10b981, #059669); }
        .risk-val { font-size: 2.6rem; font-weight: 800; }

        .analysis-item { background: white; border-radius: 20px; border: 1px solid var(--border); padding: 1.5rem; margin-bottom: 1rem; }
        .clause-badge { background: var(--primary); color: white; padding: 2px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 800; margin-bottom: 8px; display: inline-block; }
        .verbatim-text { font-size: 0.85rem; color: #334155; background: #fff5f5; padding: 10px; border-left: 4px solid var(--danger); border-radius: 4px; line-height: 1.6; margin-top: 10px; }

        .hidden { display: none; }
    </style>
</head>
<body>

<div id="consentModal">
    <div class="modal-content">
        <h2 style="text-align:center;">⚖️ ご利用前の承諾事項</h2>
        <div class="scroll-terms">
            <p><b>1. 本サービスの目的</b><br>補助ツールであり正確性を保証しません。</p>
            <p><b>2. 法的助言の否定</b><br>法的助言ではありません。専門家にご相談ください。</p>
        </div>
        <label style="display:block; text-align:center; margin-bottom:1.5rem;">
            <input type="checkbox" id="consentCheck" onchange="document.getElementById('startBtn').disabled = !this.checked"> 免責事項に同意します
        </label>
        <button id="startBtn" class="btn btn-primary" style="width: 100%; height: 50px;" onclick="document.getElementById('consentModal').style.display='none'" disabled>同意して開始</button>
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
                <button class="btn btn-primary" style="min-width: 180px;" onclick="runAnalysis()">規約を解析する</button>
            </div>
        </div>
    </section>

    <section class="panel-right">
        <div id="emptyState" style="text-align: center; margin-top: 10rem; opacity: 0.4;"><p>解析結果が表示されます</p></div>
        <div id="resultsUI" class="hidden">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                <div id="
