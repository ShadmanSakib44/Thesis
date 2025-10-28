# Automated User Story Generation from App Reviews Using Large Language Models

**Authors:**  
Oishy Fatema Akhand · Shadman Sakib · Tasnia Tasneem  
Department of Computer Science and Engineering  
Islamic University of Technology (IUT), Bangladesh

**Supervisor:**  
Shohel Ahmed (Assistant Professor)

**Co-Supervisor:**  
Md. Rafid Haque (Lecturer)

**Website Application:**  
[User Story Evaluator – Live Interface](https://human-evaluation-website-t7sf.vercel.app)

---

## Overview

This repository contains all materials related to the research project **"Automated User Story Generation from App Reviews Using Large Language Models (LLMs)"**.

The project explores how open and proprietary LLMs—**GPT-3.5 Turbo**, **Gemini 2 Flash**, and **Mistral 7B Instruct**—can transform **real-world mobile app reviews** into **agile-ready user stories** through zero-shot, one-shot, and two-shot prompting strategies.

The workflow integrates **data collection**, **prompt engineering**, **story generation**, and **evaluation** through both **human (RUST)** and **automated (RoBERTa + BLEU/ROUGE/BERTScore)** metrics.

---

## Repository Structure

```
Thesis/
├── data/
│   ├── processed/         # Processed and filtered datasets
│   └── raw/               # Original Mini-BAR subset data
├── notebooks/             # Jupyter notebooks for processing and analysis
├── src/                   # Python scripts for automation and metrics
├── docs/
│   └── relevant_papers/   # Research papers referenced in the study
├── website/
│   └── user-story-evaluator/  # Next.js web platform for human evaluation
├── figures/               # Visualization files
├── outputs/
│   └── metrics/           # Evaluation results
└── misc/
    └── pipeline.pdf       # Full-resolution pipeline figure
```

---

## Research Pipeline

![Pipeline Overview](/misc/pipeline.pdf)

The complete end-to-end research pipeline consists of the following stages:

### 1. Data Acquisition and Preprocessing
- **Source**: Mini-BAR dataset (Wei et al., 2023)
- **Process**: Merging and filtering reviews from Garmin Connect, Huawei Health, and Samsung Health
- **Action**: Removal of noise and standardization of text length

### 2. Prompt Engineering
- **Zero-shot**: Baseline prompting without examples
- **One-shot**: Single exemplar guiding tone and structure
- **Two-shot**: Two exemplars improving coherence and actionability

### 3. Model Inference
- `GPT-3.5 Turbo Instruct` (OpenAI)
- `Gemini 2.0 Flash` (Google DeepMind)
- `Mistral 7B Instruct` (Mistral AI)

Each model tested under all prompting strategies.

### 4. Evaluation Framework
- **Human Evaluation**: Via RUST dimensions — *Readability, Understandability, Specifiability, Technical aspects*
- **Automated Evaluation**: Fine-tuned RoBERTa classifier on UStAI dataset
- **Supporting Metrics**: BLEU, ROUGE-L, BERTScore

### 5. Results & Visualization
- Comparative metrics plotted in `notebooks/analysis.ipynb`
- Model-wise CSV outputs stored in `/outputs/`

---

## Key Findings

| Model | Prompt Type | Mean RUST Score | Automated (QUS) | Observation |
|-------|-------------|-----------------|-----------------|-------------|
| **Gemini 2 Flash** | Two-shot | **4.53 / 5** | **0.6628** | Most consistent and technically adequate |
| **GPT-3.5 Turbo** | One-shot | 4.49 / 5 | 0.6620 | Highest understandability |
| **Mistral 7B** | One-shot | 4.45 / 5 | 0.6618 | Competitive open-source baseline |
| **Human Baseline** | — | 4.39 / 5 | 0.6161 | Slightly lower readability variance |

**Key Insights:**
- Few-shot prompting consistently improves coherence and structure
- Gemini 2 Flash two-shot outputs show best balance between readability and specifiability
- Automated metrics correlate with human evaluation, confirming robustness of dual-pipeline analysis

---

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+
- Jupyter Notebook
- API keys for OpenAI, Google DeepMind, or OpenRouter

### Installation

#### 1. Clone Repository

```bash
git clone https://github.com/<username>/Thesis.git
cd Thesis
```

#### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Directory Structure

Ensure the following key folders exist:

```
data/raw/
outputs/
notebooks/
src/
website/
misc/pipeline.pdf
```

#### 4. Configure Environment Variables

Create a `.env.local` file in the website directory:

```env
OPENAI_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
```

### Usage

#### Run Notebooks

```bash
jupyter notebook notebooks/code.ipynb
```

Or to reproduce the entire pipeline automatically:

```bash
python src/organize.py
python src/token_count.py
```

#### Generate Stories via API

```bash
python src/generate_stories.py
```

#### Evaluate Outputs

```bash
python src/compare.py
```

Results are exported to:
- `outputs/metrics_results.csv`
- `outputs/bertscore_comparison.csv`
- `outputs/bleu_rouge_summary.csv`

### Website Development

To run the Next.js evaluation interface:

```bash
cd website/user-story-evaluator
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to access the evaluation interface.

---

## Figures

| File | Description |
|------|-------------|
| `misc/pipeline.pdf` | Full research workflow diagram |
| `figures/pipeline.png` | Simplified visual for README |
| `notebooks/analysis.ipynb` | Contains metric plots and graphs |

---

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

---

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

---

## License

This project is part of an academic research thesis. Please cite appropriately if you use any part of this work.
