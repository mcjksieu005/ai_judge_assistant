# AI Judge Assistant for ADA & DSA

**2026 ASUS UGen AI League - Workplace AI (Battlefield Thunderstorm)**

## Overview

This project is designed to reduce the heavy grading and debugging workload of Teaching Assistants (TAs) in large-scale university computer science courses such as **Algorithm Design and Analysis (ADA)** and **Data Structures and Algorithms (DSA)**.

By combining a **Self-Contained C++ Sandbox Judge Engine** with **Large Language Models (LLMs)**, the system compiles and evaluates student C++ submissions against multiple test cases with configurable CPU time limits. Whenever a submission fails (`Time Limit Exceeded`, `Wrong Answer`, `Runtime Error`, or `Compilation Error`), the system immediately renders the execution verdict and triggers a **Guided AI Teaching Assistant** to provide:

1. **Pinpoint Bug Localization & Root Cause Diagnosis**
2. **Automated Time & Space Complexity (Big-O) Analysis**
3. **Guided Optimization Hints** (helping students improve their own code without leaking the full solution)
4. **Interactive Follow-up Q&A Chat** for continuous learning

## Key Features

* **Self-Contained C++ Judge Engine:** Compiles C++ code (`g++ -O2`) in an isolated temporary directory, pipes `stdin`, enforces strict configurable CPU timeouts (`0.1s` to `10.0s`), and compares normalized `stdout` against expected outputs.
* **Multi-Testcase & `.zip` Archive Pairing:** Supports uploading a `.zip` test package or multiple `.in` and `.out`/`.ans` files, automatically pairing them by filename (e.g., `1.in` with `1.out`, `2.in` with `2.out`) and reporting per-testcase execution time and status.
* **Instant Verdict Rendering:** Immediately displays the overall verdict banner and per-testcase breakdown table before streaming the AI diagnostic report below.
* **Bilingual UI & AI Diagnostics:** One-click toggle between **English** and **Traditional Chinese (繁體中文)**.

## Prerequisites

* Python 3.8+
* `g++` compiler (GCC) installed on the system (`sudo apt install -y g++` on Ubuntu/WSL2)
* An active OpenRouter API Key

## Setup and Installation

### 1. Clone the Repository & Install Dependencies

    git clone https://github.com/mcjksieu005/ai_judge_assistant.git
    cd ai_judge_assistant
    pip install -r requirements.txt

### 2. Configure API Key

Set your OpenRouter API key as an environment variable (recommended so your key stays secure locally) or replace the placeholder inside `app.py`:

    export OPENROUTER_API_KEY="your_openrouter_api_key_here"

### 3. Run the Application

    streamlit run app.py

Access the web interface in your browser at `http://localhost:8501`.

## Usage Walkthrough

1. **Upload or Edit Code:** Upload a `.cpp` file or edit the C++ source code directly in the workspace.
2. **Set CPU Time Limit:** Adjust the time limit per test case (default: `1.0s`).
3. **Select Test Case Mode:**
   * **Built-in Multi-Testcase Benchmark:** Evaluates 3 built-in sorting test cases (`1.in` with $N=10$, `2.in` with $N=1,000$, and `3.in` with $N=80,000$).
   * **Batch Upload (`.zip` or Multiple `.in`/`.out`):** Upload your own `.zip` archive or multiple `.in`/`.out` files (you can also click **Download Sample Test Cases (.zip)** to inspect the format).
   * **Single Custom Input / Output:** Type custom `stdin` and `expected stdout` directly.
4. **Evaluate & Interact:** Click **Compile, Run Test Cases & Start AI Diagnosis**. View the instant per-testcase verdict breakdown, read the AI complexity report, and ask follow-up questions in the chat box below.