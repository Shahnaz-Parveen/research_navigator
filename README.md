# 🧭 Research Navigator: AI-Powered Semantic Analyzer

Research Navigator is a state-of-the-art web application designed for researchers and students to explore, analyze, and organize scientific papers from ArXiv. It uses **Natural Language Processing (NLP)** and **Vector Search** to provide a "smarter" way to find and understand research.

## 🚀 Core Features

- **🔍 Semantic Search**: Find papers based on *meaning*, not just keywords. Powered by **Sentence-Transformers (SBERT)** and **FAISS** for lightning-fast similarity search.
- **🏷️ Automated NER**: Automatically extracts entities like "Methods", "Concepts", and "Data" using **spaCy**.
- **📊 Interactive Knowledge Graph**: Visualize relationships between papers and research concepts in 3D using **Vis.js**.
- **🤖 Research Assistant (Chatbot)**: A persistent AI companion that helps you search the database and answers research questions.
- **📄 AI Summarization**: One-paragraph TL;DR summaries for every paper to help you read faster.
- **☁️ Production Ready**: Optimized for deployment on **Hugging Face Spaces** with full user authentication and database monitoring.

## 🛠️ Tech Stack

- **Backend**: Python, Flask, Flask-Login, SQLAlchemy
- **Search Engine**: FAISS (Facebook AI Similarity Search), Sentence-Transformers
- **NLP**: spaCy (NER, Summarization)
- **Frontend**: Vanilla CSS (Glassmorphism), JavaScript (3D visualization), HTML5
- **Data Source**: ArXiv API

## ⚙️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Shahnaz-Parveen/research_navigator.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```

## 🛡️ Key Lessons & Architecture
During development, the project evolved from a simple scraper to a full-stack AI platform. Key challenges solved included:
- **Session Security**: Optimizing cookies for Hugging Face IFrame embedding.
- **Cold-Start Performance**: Lazy-loading heavy NLP models to ensure fast initial page loads.
- **Data persistence**: Building a robust SQLite/SQLAlchemy layer for metadata and user tracking.

---
*Created with ❤️ for the Research Community.*
