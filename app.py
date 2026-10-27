import os
import io
import re
import time
import zipfile
import tempfile
import subprocess
from datetime import datetime
import streamlit as st
import openai

# ================= 設定區 =================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "YOUR_OPENROUTER_API_KEY")
# ==========================================

st.set_page_config(
    page_title="AI Judge Assistant | ASUS UGen AI League",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

I18N = {
    "English": {
        "title": "⚡ AI Judge Assistant",
        "subtitle": "Automated C++ Judge Sandbox, Multi-Testcase Evaluation & Guided AI Diagnostics (Target: ASUS UGen Intel Arc Pro B70 32GB)",
        "sidebar_history": "📚 Submission History",
        "no_history": "No submissions recorded in this session yet.",
        "clear_history": "🗑️ Clear History",
        "sub_zone": "📥 Code & Test Case Workspace",
        "out_zone": "🔍 Execution Verdict & Guided AI Assistant",
        "up_code": "Upload C++ Source Code (.cpp / .c / .txt)",
        "code_label": "C++ Source Code Editor",
        "tl_label": "⏱️ CPU Time Limit per Test Case (seconds)",
        "tc_mode_label": "📂 Test Case Input Mode",
        "tc_modes": [
            "Built-in Multi-Testcase Benchmark (1.in ~ 3.in, up to N=80,000)",
            "Batch Upload (.zip Archive or Multiple .in / .out Files)",
            "Single Custom Input / Output"
        ],
        "dl_sample_zip": "📥 Download Sample Test Cases (1.in~3.in .zip)",
        "up_batch": "Upload a .zip archive OR select multiple .in and .out/.ans files (auto-paired by filename)",
        "paired_ok": "✅ Matched {count} test case pair(s): {names}",
        "paired_warn": "⚠️ No matching (.in, .out/.ans) filename pairs found yet. Please upload both input and output files (e.g., 1.in & 1.out).",
        "in_label": "Standard Input (stdin)",
        "out_label": "Expected Output (stdout)",
        "submit_btn": "🚀 Compile, Run Test Cases & Start AI Diagnosis",
        "spinner_judge": "Compiling with g++ and evaluating test cases in sandbox...",
        "spinner_ai": "AI Teaching Assistant is analyzing code structure and generating guided hints...",
        "verdict_label": "OVERALL VERDICT",
        "metric_passed": "Test Cases Passed",
        "metric_max_time": "Max Execution Time",
        "metric_limit": "Time Limit",
        "tc_detail_header": "📋 Individual Test Case Results",
        "ai_header": "🤖 Guided AI Teaching Assistant Report",
        "chat_header": "💬 Follow-up Q&A with AI Assistant",
        "chat_placeholder": "Ask follow-up questions about your bug, Big-O complexity, or algorithm hints...",
        "ac_congrats": "🎉 **All test cases passed!** Your program is correct and runs within the time limit across all inputs.",
        "empty_state": "👈 Configure your C++ code and test cases on the left, then click 'Compile, Run Test Cases & Start AI Diagnosis'."
    },
    "繁體中文": {
        "title": "⚡ AI 程式作業批改與複雜度分析助理",
        "subtitle": "自動化 C++ 沙盒評測、多筆測資配對與引導式 AI 除錯系統 (Target: ASUS UGen Intel Arc Pro B70 32GB)",
        "sidebar_history": "📚 提交歷史紀錄",
        "no_history": "本次連線尚無提交紀錄。",
        "clear_history": "🗑️ 清除歷史紀錄",
        "sub_zone": "📥 程式碼與測資設定區",
        "out_zone": "🔍 判題結果與引導式 AI 助教",
        "up_code": "上傳 C++ 原始碼檔案 (.cpp / .c / .txt)",
        "code_label": "C++ 程式碼編輯器",
        "tl_label": "⏱️ 單筆測資時間限制 Time Limit (秒)",
        "tc_mode_label": "📂 測試資料匯入模式",
        "tc_modes": [
            "內建多筆壓力測資 (1.in ~ 3.in，最高 N=80,000)",
            "批次上傳多筆測資 (.zip 壓縮包或多個 .in / .out 檔案)",
            "單筆自訂輸入 / 輸出"
        ],
        "dl_sample_zip": "📥 下載範例多筆測資包 (1.in~3.in .zip)",
        "up_batch": "上傳 .zip 測資壓縮檔，或同時選取多個同名之 .in 與 .out/.ans 檔案（系統將自動依檔名配對）",
        "paired_ok": "✅ 成功配對 {count} 組測試資料：{names}",
        "paired_warn": "⚠️ 尚未偵測到同名的 (.in, .out/.ans) 配對檔案，請確認已同時上傳輸入與輸出檔（例如 1.in 與 1.out）。",
        "in_label": "標準輸入 (stdin)",
        "out_label": "預期輸出 (stdout)",
        "submit_btn": "🚀 編譯執行測資並啟動 AI 診斷",
        "spinner_judge": "正在使用 g++ 編譯並於隔離沙盒逐筆執行測試資料...",
        "spinner_ai": "AI 助教正在分析程式碼結構並生成引導式優化建議...",
        "verdict_label": "最終判題結果",
        "metric_passed": "通過測資數",
        "metric_max_time": "最長執行時間",
        "metric_limit": "時間限制",
        "tc_detail_header": "📋 各筆測試資料執行明細",
        "ai_header": "🤖 引導式 AI 助教診斷報告",
        "chat_header": "💬 與 AI 助教連續對話追問",
        "chat_placeholder": "針對上述錯誤原因、Big-O 複雜度或演算法優化方向繼續提問...",
        "ac_congrats": "🎉 **恭喜通過所有測試資料！** 你的演算法正確無誤，且在所有測資規模下皆符合時間限制。",
        "empty_state": "👈 請於左側編輯 C++ 程式碼與選擇測資模式，並點擊「編譯執行測資並啟動 AI 診斷」。"
    }
}

DEFAULT_CPP_CODE = (
    "#include <iostream>\n"
    "#include <vector>\n"
    "#include <algorithm>\n"
    "using namespace std;\n\n"
    "// Problem: Sort N integers in ascending order\n"
    "void solve(vector<int>& arr, int n) {\n"
    "    // Currently using O(N^2) Bubble Sort -> Will TLE on Test Case #3 (N = 80,000)\n"
    "    for (int i = 0; i < n - 1; i++) {\n"
    "        for (int j = 0; j < n - i - 1; j++) {\n"
    "            if (arr[j] > arr[j + 1]) {\n"
    "                swap(arr[j], arr[j + 1]);\n"
    "            }\n"
    "        }\n"
    "    }\n"
    "}\n\n"
    "int main() {\n"
    "    ios_base::sync_with_stdio(false);\n"
    "    cin.tie(NULL);\n"
    "    int n;\n"
    "    if (!(cin >> n)) return 0;\n"
    "    vector<int> arr(n);\n"
    "    for (int i = 0; i < n; i++) cin >> arr[i];\n"
    "    solve(arr, n);\n"
    "    for (int i = 0; i < n; i++) cout << arr[i] << (i == n - 1 ? \"\" : \" \");\n"
    "    cout << \"\\n\";\n"
    "    return 0;\n"
    "}\n"
)


@st.cache_data
def get_builtin_benchmark_testcases():
    """在記憶體中建立 3 組完全真實的排序測資 (N=10, N=1000, N=80000)"""
    cases = []
    sizes = [("1", 10), ("2", 1000), ("3", 80000)]
    for name, n in sizes:
        inp_nums = " ".join(str(x) for x in range(n, 0, -1))
        out_nums = " ".join(str(x) for x in range(1, n + 1))
        cases.append({
            "name": f"#{name} ({name}.in / {name}.out | N={n:,})",
            "stdin": f"{n}\n{inp_nums}\n",
            "expected": out_nums
        })
    return cases


@st.cache_data
def generate_sample_zip_bytes():
    """產生可供使用者下載的範例 .zip 測資包 (含 1.in/out, 2.in/out, 3.in/out)"""
    buf = io.BytesIO()
    sizes = [("1", 10), ("2", 1000), ("3", 80000)]
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, n in sizes:
            inp_str = f"{n}\n" + " ".join(str(x) for x in range(n, 0, -1)) + "\n"
            out_str = " ".join(str(x) for x in range(1, n + 1)) + "\n"
            zf.writestr(f"{name}.in", inp_str)
            zf.writestr(f"{name}.out", out_str)
    return buf.getvalue()


def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", s)]


def parse_uploaded_testcases(uploaded_files):
    """從上傳的 .zip 或多個 .in/.out 檔案中自動配對同名測資"""
    in_map = {}
    out_map = {}

    def register_file(filename, content_str):
        base = os.path.basename(filename)
        if not base or base.startswith(".") or "__MACOSX" in filename:
            return
        stem, ext = os.path.splitext(base)
        ext = ext.lower()
        if ext in [".in", ".inp"]:
            in_map[stem] = content_str
        elif ext in [".out", ".ans", ".sol"]:
            out_map[stem] = content_str

    for uf in uploaded_files:
        if uf.name.lower().endswith(".zip"):
            try:
                with zipfile.ZipFile(io.BytesIO(uf.getvalue())) as zf:
                    for info in zf.infolist():
                        if not info.is_dir():
                            raw_bytes = zf.read(info.filename)
                            register_file(info.filename, raw_bytes.decode("utf-8", errors="replace"))
            except Exception:
                pass
        else:
            register_file(uf.name, uf.getvalue().decode("utf-8", errors="replace"))

    common_stems = sorted(set(in_map.keys()) & set(out_map.keys()), key=natural_sort_key)
    paired_cases = []
    for stem in common_stems:
        paired_cases.append({
            "name": f"{stem} ({stem}.in / {stem}.out)",
            "stdin": in_map[stem],
            "expected": out_map[stem]
        })
    return paired_cases


def normalize_output(text):
    lines = [line.rstrip() for line in text.strip().splitlines()]
    return "\n".join(lines)


def run_native_judge(source_code, test_cases, time_limit):
    """
    獨立的原生 C++ 判題沙盒引擎：
    1. 呼叫 g++ -O2 進行真實編譯
    2. 依序注入每筆測資之 stdin，透過計時器與 timeout 攔截 TLE / RE
    3. 比對正規化後的 stdout 與 expected output，回傳總 Verdict 與各測資明細
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        cpp_path = os.path.join(tmpdir, "main.cpp")
        bin_path = os.path.join(tmpdir, "main.out")
        with open(cpp_path, "w", encoding="utf-8") as f:
            f.write(source_code)

        # 步驟 1: 編譯
        comp = subprocess.run(["g++", "-O2", cpp_path, "-o", bin_path], capture_output=True, text=True)
        if comp.returncode != 0:
            return {
                "overall_status": "Compilation Error (CE)",
                "passed_count": 0,
                "total_count": len(test_cases),
                "max_time": 0.0,
                "error_log": comp.stderr,
                "tc_results": []
            }

        # 步驟 2: 逐筆執行測資
        tc_results = []
        passed_count = 0
        max_time = 0.0
        overall_status = "Accepted"
        first_error_log = ""

        for idx, tc in enumerate(test_cases, start=1):
            start_t = time.perf_counter()
            try:
                proc = subprocess.run(
                    [bin_path],
                    input=tc["stdin"],
                    capture_output=True,
                    text=True,
                    timeout=float(time_limit)
                )
                elapsed = time.perf_counter() - start_t
                max_time = max(max_time, elapsed)

                if proc.returncode != 0:
                    status = "Runtime Error (RE)"
                    detail = proc.stderr.strip() or f"Process exited with code {proc.returncode} (e.g., Segmentation fault)"
                    if overall_status == "Accepted":
                        overall_status = status
                        first_error_log = f"[Test Case {tc['name']}] {detail}"
                else:
                    actual_norm = normalize_output(proc.stdout)
                    expect_norm = normalize_output(tc["expected"])
                    if actual_norm == expect_norm:
                        status = "Accepted"
                        passed_count += 1
                        detail = "Output matched expected answer."
                    else:
                        status = "Wrong Answer (WA)"
                        act_preview = actual_norm[:120] + ("..." if len(actual_norm) > 120 else "")
                        exp_preview = expect_norm[:120] + ("..." if len(expect_norm) > 120 else "")
                        detail = f"Expected: '{exp_preview}' | Actual: '{act_preview}'"
                        if overall_status == "Accepted":
                            overall_status = status
                            first_error_log = f"[Test Case {tc['name']}] {detail}"

                tc_results.append({
                    "index": idx,
                    "name": tc["name"],
                    "status": status,
                    "time": f"{elapsed:.3f}s",
                    "detail": detail
                })

            except subprocess.TimeoutExpired:
                max_time = max(max_time, float(time_limit))
                status = "Time Limit Exceeded (TLE)"
                detail = f"Execution exceeded CPU time limit of {time_limit:.2f}s."
                if overall_status == "Accepted":
                    overall_status = status
                    first_error_log = f"[Test Case {tc['name']}] {detail}"
                tc_results.append({
                    "index": idx,
                    "name": tc["name"],
                    "status": status,
                    "time": f">{time_limit:.2f}s",
                    "detail": detail
                })

        return {
            "overall_status": overall_status,
            "passed_count": passed_count,
            "total_count": len(test_cases),
            "max_time": max_time,
            "error_log": first_error_log or "All test cases passed.",
            "tc_results": tc_results
        }


def build_initial_prompt(lang, status_desc, error_log, raw_code, time_limit):
    if lang == "English":
        return (
            "You are a helpful, guided-learning Teaching Assistant for a university Data Structures and Algorithms (DSA & ADA) course.\n"
            f"A student's C++ submission received the verdict: '{status_desc}' (Time Limit setting: {time_limit:.2f}s).\n"
            f"Diagnostic / Test Case Log: {error_log}\n\n"
            "Student's C++ Code:\n"
            f"{raw_code}\n\n"
            "Provide a structured, concise diagnostic report in English using clean Markdown with the following 3 sections:\n"
            "### 1. Bug Localization & Root Cause\n"
            "Explain clearly why the code failed on the test case(s).\n"
            "### 2. Time & Space Complexity Analysis (Big-O)\n"
            "State the exact Time Complexity and Space Complexity in Big-O notation based on the student's code and justify why.\n"
            "### 3. Guided Optimization Hints\n"
            "Provide step-by-step algorithmic hints or suggest appropriate data structures / standard library functions (such as Merge Sort, Quick Sort, or std::sort) "
            "so the student can fix the problem themselves. Do not output the full completed solution code."
        )
    else:
        return (
            "你是一位專業且友善的大學「資料結構與演算法 (DSA & ADA)」課程助教，採用引導式學習協助學生除錯。\n"
            f"學生的 C++ 程式碼獲得了 '{status_desc}' 的判題結果（單筆時限設定：{time_limit:.2f} 秒）。\n"
            f"測資診斷與錯誤紀錄：{error_log}\n\n"
            "學生的 C++ 程式碼：\n"
            f"{raw_code}\n\n"
            "請使用繁體中文與清晰的 Markdown 格式，提供包含以下三個區塊的結構化診斷報告：\n"
            "### 1. 錯誤原因定位與診斷\n"
            "清楚說明為何該程式碼在測資下會產生此錯誤或超時。\n"
            "### 2. 時間與空間複雜度分析 (Big-O)\n"
            "根據程式碼結構，明確列出目前的 Time Complexity 與 Space Complexity (Big-O)，並說明推導原因。\n"
            "### 3. 引導式演算法優化提示\n"
            "給予具體的演算法改進方向或資料結構建議（例如改用 Merge Sort 或 C++ 標準庫的 std::sort），引導學生自行完成修正，請勿直接給出完整的解答程式碼。"
        )


if "history" not in st.session_state:
    st.session_state.history = []
if "current_eval" not in st.session_state:
    st.session_state.current_eval = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# ================= 側邊欄 =================
with st.sidebar:
    st.markdown("### 🌐 Language / 語言切換")
    lang = st.radio("Language", ["English", "繁體中文"], horizontal=True, label_visibility="collapsed")
    t = I18N[lang]
    
    st.divider()
    st.markdown("### 🧠 Model Selection")
    model_options = [
        "meta-llama/llama-3.3-70b-instruct",
        "meta-llama/llama-3.1-8b-instruct",
        "google/gemini-2.5-pro",
        "Custom..."
    ]
    selected_model = st.selectbox("Choose AI Model", model_options, label_visibility="collapsed")
    
    if selected_model == "Custom...":
        custom_model = st.text_input("Enter OpenRouter Model ID", value="meta-llama/llama-3.3-70b-instruct")
        active_model = custom_model
    else:
        active_model = selected_model

    st.divider()
    st.subheader(t["sidebar_history"])
    if not st.session_state.history:
        st.info(t["no_history"])
    else:
        if st.button(t["clear_history"], use_container_width=True):
            st.session_state.history = []
            st.session_state.current_eval = None
            st.session_state.chat_messages = []
            st.rerun()
        for idx, record in enumerate(reversed(st.session_state.history)):
            badge = "🟢" if record["status"] == "Accepted" else "🔴"
            num = len(st.session_state.history) - idx
            with st.expander(f"{badge} #{num:02d} | {record['status']} ({record['time']})"):
                st.caption(f"Passed: {record['passed']} | Max Time: {record['exec_time']}s")
                st.code(record["code"][:150] + "\n// ...", language="cpp")
                if record.get("feedback"):
                    st.markdown(record["feedback"])

# ================= 頂部標題區 =================
with st.container(border=True):
    st.title(t["title"])
    st.caption(t["subtitle"])

# ================= 雙欄主工作區 =================
col1, col2 = st.columns([1.05, 1], gap="large")

with col1:
    with st.container(border=True):
        st.subheader(t["sub_zone"])

        code_file = st.file_uploader(t["up_code"], type=["cpp", "c", "txt"], key="code_up")
        default_code_val = code_file.getvalue().decode("utf-8", errors="replace") if code_file else DEFAULT_CPP_CODE
        raw_code = st.text_area(t["code_label"], value=default_code_val, height=250)

        time_limit = st.number_input(t["tl_label"], min_value=0.1, max_value=10.0, value=1.0, step=0.1, format="%.1f")

        tc_mode = st.radio(t["tc_mode_label"], t["tc_modes"], index=0)
        active_testcases = []

        if tc_mode == t["tc_modes"][0]:
            active_testcases = get_builtin_benchmark_testcases()
            st.caption(f"📦 Ready: 3 built-in test cases (`1.in` N=10, `2.in` N=1,000, `3.in` N=80,000)")
        elif tc_mode == t["tc_modes"][1]:
            st.download_button(
                label=t["dl_sample_zip"],
                data=generate_sample_zip_bytes(),
                file_name="sample_testcases.zip",
                mime="application/zip",
                use_container_width=True
            )
            batch_files = st.file_uploader(
                t["up_batch"],
                type=["zip", "in", "out", "ans", "txt"],
                accept_multiple_files=True,
                key="batch_up"
            )
            if batch_files:
                active_testcases = parse_uploaded_testcases(batch_files)
            if active_testcases:
                names_str = ", ".join(tc["name"].split(" ")[0] for tc in active_testcases)
                st.success(t["paired_ok"].format(count=len(active_testcases), names=names_str))
            else:
                st.warning(t["paired_warn"])
        else:
            in_col, out_col = st.columns(2)
            with in_col:
                custom_in = st.text_area(t["in_label"], value="5\n5 4 3 2 1", height=95)
            with out_col:
                custom_out = st.text_area(t["out_label"], value="1 2 3 4 5", height=95)
            active_testcases = [{"name": "#1 (Custom)", "stdin": custom_in, "expected": custom_out}]

        submit = st.button(
            t["submit_btn"],
            type="primary",
            use_container_width=True,
            disabled=(len(active_testcases) == 0)
        )

with col2:
    with st.container(border=True):
        st.subheader(t["out_zone"])

        if submit and active_testcases:
            # 階段 1: 執行原生 C++ 沙盒判題
            with st.spinner(t["spinner_judge"]):
                judge_res = run_native_judge(raw_code, active_testcases, time_limit)

            st.session_state.current_eval = {
                "overall_status": judge_res["overall_status"],
                "passed_count": judge_res["passed_count"],
                "total_count": judge_res["total_count"],
                "max_time": f"{judge_res['max_time']:.3f}",
                "time_limit": f"{time_limit:.2f}",
                "error_log": judge_res["error_log"],
                "tc_results": judge_res["tc_results"],
                "raw_code": raw_code,
                "feedback": t["ac_congrats"] if judge_res["overall_status"] == "Accepted" else None
            }
            st.session_state.chat_messages = []

        # 階段 2: 立即渲染 Verdict 橫幅、指標與各測資結果明細（不需等待 AI 完成）
        if st.session_state.current_eval is not None:
            ev = st.session_state.current_eval
            is_ac = ev["overall_status"] == "Accepted"

            if is_ac:
                st.success(f"✅ **{t['verdict_label']}**: {ev['overall_status']}")
            else:
                st.error(f"❌ **{t['verdict_label']}**: {ev['overall_status']}")

            m1, m2, m3 = st.columns(3)
            m1.metric(
                t["metric_passed"],
                f"{ev['passed_count']} / {ev['total_count']}",
                delta="100% Passed" if is_ac else "Incomplete",
                delta_color="normal" if is_ac else "inverse"
            )
            m2.metric(t["metric_max_time"], f"{ev['max_time']} s")
            m3.metric(t["metric_limit"], f"{ev['time_limit']} s")

            if ev["tc_results"]:
                with st.expander(t["tc_detail_header"], expanded=True):
                    for tc in ev["tc_results"]:
                        tc_icon = "🟢" if tc["status"] == "Accepted" else "🔴"
                        st.markdown(f"**{tc_icon} Test Case {tc['name']}** — `{tc['status']}` (`{tc['time']}`)")
                        if tc["status"] != "Accepted":
                            st.caption(tc["detail"])
            elif ev["overall_status"] == "Compilation Error (CE)":
                st.code(ev["error_log"], language="text")

            st.divider()
            st.markdown(f"#### {t['ai_header']}")

            # 階段 3: 若尚未產生 AI 報告，此時在下方獨立轉圈呼叫 LLM，前面的 Verdict 已經清晰呈現在畫面上
            if ev["feedback"] is None:
                with st.spinner(t["spinner_ai"]):
                    try:
                        client = openai.OpenAI(
                            base_url="https://openrouter.ai/api/v1",
                            api_key=OPENROUTER_API_KEY
                        )
                        init_prompt = build_initial_prompt(
                            lang,
                            ev["overall_status"],
                            ev["error_log"],
                            ev["raw_code"],
                            float(ev["time_limit"])
                        )
                        sys_msg = (
                            "You are a supportive university DSA & ADA Teaching Assistant using guided learning. "
                            "Provide clear bug diagnosis, Big-O analysis, and optimization hints without giving away full solution code."
                        )
                        st.session_state.chat_messages = [
                            {"role": "system", "content": sys_msg},
                            {"role": "user", "content": init_prompt}
                        ]
                        completion = client.chat.completions.create(
                            model=active_model,
                            messages=st.session_state.chat_messages
                        )
                        ai_feedback = completion.choices[0].message.content
                        st.session_state.chat_messages.append({"role": "assistant", "content": ai_feedback})
                    except Exception as e:
                        ai_feedback = f"⚠️ OpenRouter API Error: {e}"

                    ev["feedback"] = ai_feedback
                    st.session_state.history.append({
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "status": ev["overall_status"],
                        "passed": f"{ev['passed_count']}/{ev['total_count']}",
                        "exec_time": ev["max_time"],
                        "code": ev["raw_code"],
                        "feedback": ai_feedback
                    })
            elif submit and is_ac:
                st.session_state.history.append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "status": ev["overall_status"],
                    "passed": f"{ev['passed_count']}/{ev['total_count']}",
                    "exec_time": ev["max_time"],
                    "code": ev["raw_code"],
                    "feedback": ev["feedback"]
                })

            with st.container(border=True):
                st.markdown(ev["feedback"])

            # 階段 4: 連續追問互動聊天室
            if not is_ac and len(st.session_state.chat_messages) >= 3:
                st.markdown(f"#### {t['chat_header']}")
                for msg in st.session_state.chat_messages[3:]:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

                user_followup = st.chat_input(t["chat_placeholder"])
                if user_followup:
                    st.session_state.chat_messages.append({"role": "user", "content": user_followup})
                    with st.chat_message("user"):
                        st.markdown(user_followup)
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            client = openai.OpenAI(
                                base_url="https://openrouter.ai/api/v1",
                                api_key=OPENROUTER_API_KEY
                            )
                            resp = client.chat.completions.create(
                                model=active_model,
                                messages=st.session_state.chat_messages
                            )
                            reply = resp.choices[0].message.content
                            st.markdown(reply)
                            st.session_state.chat_messages.append({"role": "assistant", "content": reply})
        else:
            st.info(t["empty_state"])