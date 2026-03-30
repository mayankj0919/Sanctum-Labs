# 🧠 SANCTUM AI — Structural Intelligence System

SANCTUM AI is an end-to-end structural analysis platform that transforms 2D floor plans into intelligent, material-optimized 3D models. It combines computer vision, engineering logic, and generative AI to provide clear, actionable construction insights.

---

## 🚀 Key Features

*   **🔍 Intelligent Floor Plan Parsing**: Automatically extracts room layouts and wall geometries from images using OpenCV, with a robust **Gemini 2.0 Flash fallback** for complex plans.
*   **🏗️ Structural Analysis**: Infers structural properties (load-bearing vs. partition walls) based on span lengths and spatial layout.
*   **🧱 Material Recommendation Engine**: Recommends optimal construction materials (RCC, Steel, Brick, etc.) using a rule-based logic system.
*   **💬 Engineering Explanations**: Generates clear, professional engineering reasoning for every material choice using LLM-powered insights (OpenRouter/Gemma).
*   **📊 Interactive 3D Visualization**: Renders the complete structure in real-time using Plotly, allowing users to inspect the model phase-by-phase.

---

## 🏗️ System Architecture

### 🔵 Backend (Python / Flask)
*   `server.py`: The main REST API serving the `/analyze` endpoint with streaming support.
*   `vision_parser.py`: Handles image processing (OpenCV) and layout extraction (Gemini Vision).
*   `pipeline.py`: Orchestrates the flow from raw geometry to material selection and explanations.
*   `materials.py`: Contains the core logic for structural assessment and material mapping.
*   `explain.py`: Connects to LLM APIs to generate professional engineering justifications.
*   `data.py`: Centralized schemas and fallback structural data.

### 🎨 Frontend (HTML / CSS / JS)
*   **Tech Stack**: Vanilla Javascript, CSS3 (Glassmorphism), Plotly.js for 3D rendering.
*   **Location**: Hosted in the `/frontend` directory.
*   **Features**: Drag-and-drop upload, real-time analysis streaming, interactive 3D viewer, and detailed results panel.

---

## 🛠️ Setup & Execution

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file with:
```env
GEMINI_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
```

### 3. Run the Backend
```bash
python server.py
# Running on http://localhost:5000
```

### 4. Run the Frontend
```bash
# From the root directory:
python -m http.server 8000 --directory frontend
# Access at http://localhost:8000
```

---

## 🔄 Data Pipeline Flow

1.  **Input**: JPG/PNG Floor Plan or JSON Geometry.
2.  **Vision**: Extract rooms and walls; classify rooms (Bedroom, Living, etc.).
3.  **Analysis**: Calculate spans and loads; determine wall types.
4.  **Intelligence**: Match materials to structural requirements and generate AI explanations.
5.  **Output**: ND-JSON stream of phases (Layout → Walls → Analysis → Materials → Final).

---

## 🎯 Core Philosophy
*"Build a system that not only recommends materials but also explains why, acting as a digital technical partner for engineers and architects."*
