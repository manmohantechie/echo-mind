# 🧠 EchoMind – AI-Powered Document Chat (RAG System)

EchoMind is a production-style Retrieval-Augmented Generation (RAG) system that enables conversational querying over large document sets using semantic search and LLM-based responses.

Built with a focus on **low latency, scalability, and real-world system design**, rather than demo-level implementations.

---

## 🚀 Overview

Most RAG tutorials work for small datasets but break down with:
- Large documents
- Slow retrieval times
- Poor context handling

EchoMind addresses these challenges by implementing an optimized pipeline for **efficient document ingestion, semantic retrieval, and response generation**.

---

## ⚙️ Key Features

- 🔍 Semantic document search using vector embeddings  
- 💬 Context-aware conversational responses (LLM integration)  
- ⚡ Optimized retrieval pipeline (low-latency responses)  
- 📦 Efficient document chunking and embedding strategy  
- 🔄 Scalable backend APIs using FastAPI  
- 🖥 Simple React-based UI for interaction  

---

## 🏗 Architecture

<img width="749" height="746" alt="Screenshot 2026-03-09 at 11 35 03 AM" src="https://github.com/user-attachments/assets/b19ea249-6d1a-4303-82bd-67826136e535" />


---

## 🧠 Design Decisions

### 1. Chunking Strategy
- Implemented intelligent document chunking to balance:
  - Context relevance
  - Token limits
- Avoids loss of semantic meaning in large documents

---

### 2. Retrieval Optimization
- Semantic similarity search via embeddings
- Reduced unnecessary context retrieval to improve latency

---

### 3. Low-Latency Pipeline
- Async API handling with FastAPI
- Optimized request flow for faster response times

---

### 4. Cost Efficiency
- Reuse embeddings where possible
- Minimized redundant API calls

---

## 📊 Performance

- ⚡ Sub-200ms retrieval latency (local testing)
- 📄 Handles large document sets efficiently
- 🔍 High relevance in retrieved context for queries

---

## ⚠️ Challenges & Learnings

- Managing context window limitations in LLMs  
- Balancing chunk size vs retrieval accuracy  
- Reducing latency while maintaining response quality  
- Handling large document ingestion efficiently  

---

## 🛠 Tech Stack

- **Backend:** FastAPI (Python)  
- **Vector DB:** ChromaDB  
- **LLM:** OpenAI API  
- **Frontend:** React.js  
- **Storage:** Local / extensible  

---

## 🚀 Getting Started

### 1. Clone the repo and run Docker
```bash
git clone https://github.com/manmohantechie/echo-mind.git
cd echo-mind 
docker-compose up --build 
```


# Demo Screenshot
<img width="1432" height="798" alt="Screenshot 2026-03-13 at 9 35 07 AM" src="https://github.com/user-attachments/assets/2f3763f6-9527-4dd0-9062-9877487f3afd" />
