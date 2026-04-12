---
TITLE: Agent-Testing-Framework
AUTHOR: Priyanka Rajeev Hichkad
---

# Agent Testing Framework

## Introduction

The **Agent Testing Framework** is a comprehensive system designed to **evaluate, benchmark, and improve AI agents** in a structured and reliable way. As AI systems become more powerful, ensuring their **accuracy, safety, and robustness** is critical.

This framework provides an **end-to-end evaluation pipeline** that allows developers to test any AI agent using predefined test cases, automated metrics, and adversarial inputs — all visualized through an interactive dashboard.

### Problem Statement: 
“One of the biggest challenges with AI systems today is reliability and safety.
We often don’t know:

- Whether the response is correct
- Whether it’s safe
- Or if the model is hallucinating

So make a framework to systematically test and evaluate the agents.”

---

## Objective

The primary objectives of this project are:

- Build an **agent-agnostic evaluation framework** (works with any AI model)  
- Automate evaluation using **correctness, relevance, and safety metrics**  
- Test robustness using **adversarial prompts and edge cases**  
- Ensure safety through **rule-based checks (PII detection, keyword filtering)**  
- Provide **interactive insights via a Streamlit dashboard**  
- Enable persistent logging using **Google Sheets integration**

---

## Architecture
```
Agent-Testing-Framework/
│
├── data/
│ ├── harmful_keywords.txt   # Keyword filter  
│ └── test_cases.json        # Structured Input
│
├── evaluation/
│ ├── results.csv            # Final evaluation of test case
│ └── logs.jsonl             # Logs CLI inputs and their evaluations
│
├── framework/
│ ├── agent.py               # Agent interface (agent-agnostic)
│ ├── evaluator.py           # LLM + rule-based evaluation
│ ├── runner.py              # Test execution pipeline
│ ├── metrics.py             # KPI computation
│ ├── report.py              # Final report generation
│ ├── judge                  # LLM evaluation
│ ├── rules                  # Rule-Based evaluation
│ ├── adversarial.py         # Adversarial test generator
│ ├── utils.py               # Test case loader
│ ├── log_logger.py          # Converts Logs into Test Case
│ ├── logger.py              # Local logging
│ ├── google_logger.py       # Google Sheets logging
│ └── web_hallucinations.py  # Detect Hallucinations
│
├── app.py                   # Streamlit Dashboard
├── run_tests.py             # CLI Test Runner
├── requirements.txt         # Required Installments
├── schemas.py               # Structured validation (Pydantic)
├── Architecture.md          # Project struture details
└── README.md                # Project Information
```

---

## How It Works

1. Load predefined test cases  
2. Generate adversarial inputs  
3. Run queries through the AI agent  
4. Evaluate responses using:
   - LLM-based scoring  
   - Rule-based safety checks  
5. Compute metrics and generate reports  
6. Visualize results in Streamlit dashboard  
7. Log results to Google Sheets or in json file

---

## How to Use

### Run Locally

```bash
git clone https://github.com/PriyankaHichkad/Agent-Testing-Framework.git
cd Agent-Testing-Framework
```
Setup Environment Variables:
```bash
touch .env
```
Add your Groq API key (in .env file):
```env
GROQ_API_KEY=your_groq_api_key_here
```
Install dependencies:
```bash
pip install -r requirements.txt
```
Run the CLI Code:
```bash
python run_tests.py
```

### Live App

- Deployed Link: https://agent-testing-framework-t6utdxnkt8kuxbzpefbsck.streamlit.app

---

## Logs (Google Sheets)

All evaluation logs are stored in a Google Sheet for persistence and analysis.

- View Logs Here: https://docs.google.com/spreadsheets/d/1LSgNvS5NFIf0DSwfda6zpiZmjVRv0cgKCiHmagJ0jSc/edit?gid=0#gid=0

---

## Demo Video

- Watch the demo here: https://drive.google.com/file/d/1LMB9IxhNBV2IvC4KZwhhJWx2P3qBCdAo/view?usp=drive_link

---

## Features
- Single query testing
- Structured test case input
- Full test suite execution
- Interactive dashboard with filtering
- KPI tracking (Correctness, Relevance, Safety)
- Safety comparison (LLM vs Rule-based)
- Failure analysis
- Google Sheets logging
- Safety & Evaluation
- LLM-Based Evaluation (Correctness (0/1), Relevance (0/1), Safety (0/1))
- Rule-Based Checks (PII Detection (emails, phone numbers), Keyword Filtering, Refusal Detection)
- Key Insights (Binary scoring improves consistency and reliability, Adversarial testing ensures robustness against attacks, Rule-based safety complements LLM evaluation)
- External logging solves Streamlit persistence limitations

---

## Future Improvements
- Hybrid scoring (binary + confidence)
- Improved hallucination detection
- Multi-agent benchmarking
- API-based evaluation system
- Advanced semantic similarity using embeddings

---

## Conclusion

The AI Agent Testing Framework provides a scalable and practical solution for evaluating AI systems in real-world scenarios. By combining LLM-based evaluation, rule-based safety checks, adversarial testing, and interactive visualization, it ensures that AI agents are not only accurate but also safe and reliable.

---

## Contributing

Contributions are welcome and appreciated! If you'd like to improve this project, feel free to fork the repository, create a new branch, and submit a pull request. 

Whether it's fixing bugs, improving evaluation logic, enhancing the dashboard, or adding new features, your contributions help make this framework better for everyone
