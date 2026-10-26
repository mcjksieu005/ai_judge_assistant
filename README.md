# AI Judge Assistant for Data Structures and Algorithms

**2026 ASUS UGen AI League - Workplace AI**

## Overview
This project aims to reduce the heavy workload of Teaching Assistants (TAs) in large-scale computer science courses like Data Structures and Algorithms (DSA). 

By integrating a lightweight UI with the **Judge0** execution engine and **Large Language Models (LLMs)**, this system automatically evaluates student C++ submissions. When a submission fails (e.g., Time Limit Exceeded, Wrong Answer, Segmentation Fault), the system automatically triggers an AI assistant to provide:
1. Exact bug location and error diagnosis.
2. Time and Space Complexity (Big O) analysis.
3. Algorithm optimization hints without giving away the direct solution.

## Architecture
- **Frontend:** Streamlit (Python) - Provides file uploading (.cpp, .txt) and historical record tracking.
- **Sandbox Execution:** Judge0 (Docker) - Compiles and runs student code against test cases securely.
- **AI Analysis:** OpenRouter API (Llama-3 / Claude-3.5) - Generates TA-like feedback based on execution errors.

## Prerequisites
- Python 3.8+
- Docker & Docker Compose (for Judge0)
- An active OpenRouter API Key

## Setup and Installation

### 1. Start the Judge0 Sandbox
The system relies on a local instance of Judge0 to safely execute code.
```bash
# Download and extract Judge0
wget https://github.com/judge0/judge0/releases/download/v1.13.0/judge0-v1.13.0.zip
unzip judge0-v1.13.0.zip
cd judge0-v1.13.0

# Start the database and redis first, wait for 15 seconds
sudo docker-compose up -d db redis

# Start the server and workers
sudo docker-compose up -d
```
Verify Judge0 is running by checking: `curl http://localhost:2358/system_info`

### 2. Setup the Web Application
Clone this repository and navigate into the folder.

```bash
# Install required Python packages
pip install -r requirements.txt
```

### 3. Configure API Key
Open `app.py` and replace the placeholder API key with your actual OpenRouter API key:
```python
OPENROUTER_API_KEY = "YOUR_API_KEY_HERE"
```

### 4. Run the Application
```bash
streamlit run app.py
```
Access the web interface at `http://localhost:8501`. 

## Usage
1. Drag and drop a student's `.cpp` file into the code area.
2. Upload the test cases (stdin and expected output) as `.txt` files.
3. Click "Submit" to run the code. If the code results in an error (e.g., TLE), the AI TA will automatically generate a feedback report.

## Note
This repository contains the full integration with the Judge0 backend. Ensure your Docker environment is properly configured before running.