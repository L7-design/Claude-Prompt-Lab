# ⚡ Claude Prompt Precision & System Evaluation Lab

An interactive testbed built with **Streamlit** and the **Anthropic Python SDK** (`claude-3-5-sonnet`) to benchmark baseline prompts against XML-structured system instructions using an LLM-as-a-Judge evaluation framework.

## 🌟 Key Features
- **Parallel Prompt Testing:** Compare raw unstructured system prompts against structured XML prompt architectures side-by-side.
- **Automated LLM-as-a-Judge Evaluation:** Uses Claude 3.5 Sonnet to score outputs on structure, pedagogical relevance, and actionability.
- **Real-Time Metrics:** Returns structured JSON scoring to quantify output improvements.

## 🛠️ Tech Stack
- **Language:** Python
- **LLM API:** Anthropic API (`claude-3-5-sonnet-20240620`)
- **Frontend Framework:** Streamlit

## 🚀 Quickstart
1. Clone this repository:
   ```bash
   git clone [https://github.com/L7-design/Claude-Prompt-Lab.git](https://github.com/L7-design/Claude-Prompt-Lab.git)
   cd Claude-Prompt-Lab
   pip install -r requirements.txt
   streamlit run app.py
