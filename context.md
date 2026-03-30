# 🧠 SANCTUM AI — Structural Intelligence System
> **"Engineering the Future: Automated Structural Analysis with Blockchain Integrity."**

SANCTUM AI is a sophisticated, end-to-end platform that transforms 2D floor plans into intelligent, material-optimized 3D models. It leverages Computer Vision, Soroban Smart Contracts on Stellar, and Generative AI (LLMs) to provide real-time, actionable engineering insights.

---

## 🚀 Key Features (For PPT Slides)

### 1. 🔍 Vision-First Layout Extraction
*   **Intelligent Parsing**: Converts JPG/PNG floor plans into precise boundary coordinates using OpenCV.
*   **LLM Visual Fallback**: Utilizes **Gemini 1.5 Flash** to interpret complex, non-standard layouts where traditional CV detection is insufficient.
*   **Spatial Awareness**: Automatically identifies and classifies room types (Bedroom, Kitchen, Living, etc.) based on dimensional logic.

### 2. 🏗️ Autonomous Structural Analysis
*   **Load-Bearing Inference**: Calculates span lengths and beam requirements based on floor plan geometry.
*   **Smart Partitioning**: Differentiates between structural walls and partition walls.
*   **Material Selection**: Executes a rule-based engine to assign specific materials (RCC, Steel, AAC Blocks) based on calculated structural demands.

### 3. 💬 Engineering Intelligence (AI-Powered)
*   **LLM Justification**: For every wall and room, SANCTUM generates professional engineering reasoning using **Google Gemma-3** (via OpenRouter).
*   **Real-time Insights**: Provides predictive risk assessments and optimal mitigation strategies for specific wall segments.

### 4. 🔗 Blockchain Integrity (Stellar Integration)
*   **Soroban Smart Contracts**: Report hashes are stored on the **Stellar Testnet** using Rust-based Soroban contracts (WASM).
*   **Project Immutability**: Every analysis is assigned a unique `Project ID` and hashed (SHA-256) to ensure the report hasn't been tampered with.
*   **Live Verification**: Features a dedicated `/verify` endpoint and a frontend "Verify Now" button to pull live ledger data.

### 5. 📊 Interactive 3D Visualization
*   **Phase-by-Phase Rendering**: Users can autoplay through five distinct phases: Layout → Walls → Analysis → Materials → Final.
*   **Dynamic 3D Plotly View**: Full 3D rotation and zoom-to-mesh interaction—click any room on the 3D model to see detailed modal reports.
*   **Premium Glassmorphic UI**: High-contrast, dark-themed dashboard with real-time status badges and copy-to-clipboard functionality.

---

## 🏗️ System Architecture

### 🔵 Backend (The Logic Core)
*   **`server.py`**: Flask-based REST API with ND-JSON streaming for zero-latency UI updates.
*   **`blockchain.py`**: Asynchronous integration layer for Stellar CLI and ledger commitment.
*   **`pipeline.py` & `materials.py`**: The structural "brain" that calculates spans and matches material physics.
*   **`vision_parser.py`**: Dual-layer detection (OpenCV + Gemini Vision).

### 🎨 Frontend (The User Experience)
*   **Tech Stack**: Vanilla Javascript (Modern ES6+), Plotly.js, CSS Glassmorphism.
*   **Interaction Model**: Drag-and-drop ingestion, Sidebar analysis drawer, and Modal detail view for 3D room objects.

---

## 🛠️ Execution & Testing

### Installation
```bash
pip install -r requirements.txt
# Requirements: Flask, OpenCV, Plotly, Python-Dotenv, Requests
```

### Hosting & Monitoring
1.  **Backend**: `python server.py` (Port 5000)
2.  **Frontend**: `python -m http.server 8000` (Port 8000)
3.  **Tests**: `python test_runner.py` (Automated suite for pipeline and blockchain endpoints).

---

## 🎯 Project Impact (Closing Slide)
*   **Efficiency**: Reduces manual CAD-to-Analysis workflow from hours to seconds.
*   **Trust**: Guaranteed data integrity via decentralized ledger storage.
*   **Insight**: Bridging the gap between 2D sketches and architectural 3D intelligence.

---

## 📍 Environment Configuration
*   **Blockchain**: Stellar Testnet
*   **Contract Address**: `CDLIC3HMOLOBD5E3BZSKLENWZZ52LGUDW5YGFNWJHVAHZKK7XFIDHDDJ`
*   **LLM Providers**: OpenRouter (Gemma-3), Google AI (Gemini 1.5 Flash).
