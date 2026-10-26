import streamlit as st
import requests
import openai
import json
from datetime import datetime

OPENROUTER_API_KEY = "YOUR_API_KEY"

st.set_page_config(page_title="AI 助教判題系統", layout="wide")

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.header("📚 診斷歷史紀錄")
    if not st.session_state.history:
        st.info("尚無歷史紀錄")
    else:
        for idx, record in enumerate(reversed(st.session_state.history)):
            with st.expander(f"[{record['time']}] {record['status']}"):
                st.code(record['code'][:100] + "...", language="cpp")
                st.markdown(f"**AI 建議**:\n{record['feedback']}")

st.title("👨‍🏫 AI 程式作業批改與複雜度分析助理")

def process_file_input(uploaded_file, default_text):
    if uploaded_file is not None:
        content = uploaded_file.getvalue().decode("utf-8")
        preview = content if len(content) < 2000 else content[:2000] + "\n\n... [檔案過大，僅顯示前 2000 字元預覽]"
        return content, preview
    return default_text, default_text

col1, col2 = st.columns(2)

with col1:
    st.subheader("學生提交區")
    
    code_file = st.file_uploader("上傳 C++ 程式碼 (.cpp)", type=["cpp", "txt", "c"])
    raw_code, preview_code = process_file_input(code_file, "#include <iostream>\nusing namespace std;\nint main() {\n    // O(N^2) 測試\n    return 0;\n}")
    code = st.text_area("程式碼內容", value=preview_code, height=200)

    in_file = st.file_uploader("上傳測試輸入資料 (.txt)", type=["txt"])
    raw_in, preview_in = process_file_input(in_file, "100000")
    test_input = st.text_area("輸入內容", value=preview_in, height=100)

    out_file = st.file_uploader("上傳預期輸出 (.txt)", type=["txt"])
    raw_out, preview_out = process_file_input(out_file, "答案")
    expected_output = st.text_area("預期輸出內容", value=preview_out, height=100)

    submit = st.button("提交並進行 AI 診斷", type="primary")

with col2:
    st.subheader("Judge0 & AI 診斷結果")
    if submit:
        with st.spinner("Judge0 執行中..."):
            payload = {
                "source_code": raw_code,  # 傳送完整檔案字串
                "language_id": 54, 
                "stdin": raw_in,          # 傳送完整 10 萬筆測資
                "expected_output": raw_out
            }
            try:
                res = requests.post("http://localhost:2358/submissions?base64_encoded=false&wait=true", json=payload)
                judge_result = res.json()
                status_desc = judge_result.get('status', {}).get('description', 'Unknown')
                st.error(f"**Judge0 判題結果**: {status_desc}")
                st.write(f"執行時間: {judge_result.get('time', 'N/A')} 秒")
            except Exception as e:
                st.error("Judge0 連線失敗，請確認 Docker 是否啟動。")
                st.stop()

        if status_desc != "Accepted":
            with st.spinner("AI 助教分析中..."):
                client = openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)
                prompt = f"""
                你是資料結構與演算法助教。學生的 C++ 程式碼得到 '{status_desc}'。
                編譯/執行錯誤訊息：{judge_result.get('compile_output') or judge_result.get('stderr')}
                程式碼：\n{raw_code}\n
                請以繁體中文簡要提供：
                1. 錯誤原因診斷 (例如為何 TLE 或 RE)
                2. 時間與空間複雜度 (Big O)
                3. 優化提示 (不給完整解答)
                """
                completion = client.chat.completions.create(
                    model="meta-llama/llama-3-70b-instruct",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                ai_feedback = completion.choices[0].message.content
                st.success("**AI 助教回饋**")
                st.markdown(ai_feedback)
                
                st.session_state.history.append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "status": status_desc,
                    "code": raw_code,
                    "feedback": ai_feedback
                })