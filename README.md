# 🧬 BioCure Swarm: Real-Time Proteomics Discovery Engine

⚡ **Live Demo Website:** [therahulgoel.github.io/BioCure-Swarm](https://therahulgoel.github.io/BioCure-Swarm/)

**BioCure Swarm** is a real-time scientific discovery engine powered by **Cerebras Wafer-Scale CS-3 inference engines** and **Google Gemma 4** designed to accelerate candidate therapeutic discovery for global diseases.

By utilizing Cerebras' high-throughput, low-latency wafer-scale engine, BioCure Swarm orchestrates a multi-agent ensemble of specialized biological experts (Sequence Analyst, Folding Predictor, Literature Cross-Referencer, Synthesis Optimizer) to deliver near-instantaneous proteomics and genomics hypotheses.

---

## 📂 Project Architecture

The repository is structured as follows:
```text
BioCure-Swarm/
├── requirements.txt         # Package dependencies (pip install -r requirements.txt)
├── README.md                # Main project documentation & guide (this file)
├── WHY_CEREBRAS.md          # Technical analysis (GPU bottlenecks vs Wafer-Scale)
├── LICENSE                  # Open-source MIT License
├── main.py                  # Main Flask application and server
│
├── 📂 dashboard/            # BioCure Swarm Web Application Frontend
│   ├── index.html           # Main dashboard web interface
│   ├── style.css            # Dark biotech design stylesheet
│   └── app.js               # Interactive 3D molecular viewer and API controller
│
├── 📂 agent/                # Multi-Agent Coordination Pipeline
│   └── multi_agent_pipeline.py # Chains scientific agents (Sequence, Folding, PubMed, Synthesis)
│
└── 📂 scripts/              # Developer Testing Scripts
    ├── test_cerebras.py     # Liveness API key validation test
    └── list_models.py       # Cerebras model catalog query tool
```

---

## ⚡ The Core Innovation: Cerebras CS-3 vs. Legacy GPU Showdown

Scientific sequence exploration is highly iterative. Legacy GPUs bottleneck the research loop due to memory-bandwidth limitations. By leveraging the **Cerebras CS-3**, we process the entire 4-step coordination loop in **~1.1 seconds**, running at **1,450+ tokens/second**.

| Performance Metric | Traditional GPU (NVIDIA A100) | Cerebras Wafer-Scale (CS-3) | Scientific Impact |
| :--- | :--- | :--- | :--- |
| **Inference Speed** | ~50 - 80 tokens/sec | **1,450+ tokens/sec** | ~18x throughput increase |
| **Sequential Swarm Loop** | ~18.0 seconds | **~1.1 seconds** | Preserves researcher's cognitive flow state |
| **Combinatorial Sweep (1k)** | ~5 hours | **~18 minutes** | Turns overnight batch jobs into interactive sessions |
| **Handoff Memory Overhead** | High (VRAM model swapping) | **Zero (On-wafer SRAM execution)** | Makes dense, multi-agent debates practical |

---

## 🛠️ Setup & Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Cerebras API Key
Copy the `.env.example` file to `.env` and fill in your Cerebras API key, or set it directly in your environment:
```bash
export CEREBRAS_API_KEY="your-key-here"
```

### 3. Start the Application
Start the unified Flask server to launch the backend and serve the dashboard:
```bash
python3 main.py
```
Open **[http://localhost:8080](http://localhost:8080)** in your local browser to access the BioCure Swarm interface.
