# Sentinel AI - Vehicle Intelligence & Clone Detection Platform

Sentinel AI is an enterprise-grade cyber intelligence platform designed for law enforcement departments to detect cloned vehicles from CCTV video clips, search target plates, and query a secure database via a secure, zero-hallucination Police AI Assistant.

---

## Technical Architecture

### 📊 Backend (FastAPI)
*   **Frame Optimization Engine**: Processes CCTV uploads using OpenCV and selects the sharpest frame utilizing Laplacian variance (maximizing contrast to counter motion blur).
*   **Computer Vision Pipeline**: Integrates YOLOv11 for vehicle bounding box segmentation and PaddleOCR for licence plate reading. Graceful simulated fallbacks ensure execution stability if hardware weight engines are uncompiled.
*   **Multi-Modal Auditing**: Uses Google's Gemini Multimodal API to read visual attributes (brand, model, color) directly from the extracted frames and compares them to registered registries.
*   **Spatial-Temporal Engine**: Analyzes travel records. If a plate is observed in Vijayawada and Hyderabad within a 3-minute span, the engine flags a Critical Clone Alert by calculating implied travel speeds.
*   **Security Context**: Secure Admin-Only authorization gates backed by JWT payloads, secure password hashing, and action auditing chains.

### 💻 Frontend (React 19 + TypeScript)
*   **NASA/FBI Control Room Style**: Glassmorphic dark widgets, aurora backdrops, scanline overlays, and neon glow accents.
*   **Interactive Analytics**: Recharts Area charts plotting weekly surveillance frequencies, pie chart threat distributions, and location trackers.
*   **Intelligence Assistant Dashboard**: Chat console yielding markdown logs paired with interactive database metadata widgets (auto-rendering charts or target logs).

---

## Project Structure

```text
├── backend/
│   ├── app/
│   │   ├── api/             # Router controllers, deps, auth
│   │   ├── core/            # Configs, Security, Loguru setups
│   │   ├── database/        # Motor MongoDB session client, seed scripts
│   │   ├── models/          # Pydantic schemas (User, Vehicle, Detection, Chat, Audit)
│   │   ├── services/        # AI Vision, Risk Engine, Chatbot RAG
│   │   └── main.py          # FastAPI application entrance
│   ├── uploads/             # Mounted directory for video & crop media
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/             # Axios API client
│   │   ├── components/      # Sidebar header frames
│   │   ├── context/         # AuthContext JWT state
│   │   ├── pages/           # Landing, Dashboard, Section 1, 2, 3, Login, Settings, History
│   │   └── index.css        # Cyber grid overlays, scanlines, scrollbars
│   ├── tailwind.config.js   # Glow configurations & theme colors
│   └── Dockerfile
├── docker-compose.yml
├── package.json             # Workspace runner scripts
└── .env                     # Shared environment configurations
```

---

## ⚡ Quick Start: Docker Compose

Launch the complete ecosystem (Database, Backend, Frontend) with a single command:

1.  **Configure API Keys**: Edit the `.env` file in the root directory and specify your Gemini API Key:
    ```env
    GEMINI_API_KEY=your_gemini_api_key_here
    ```
2.  **Spin up Services**:
    ```bash
    docker-compose up --build
    ```
3.  **Access Terminals**:
    *   **Frontend Hub**: http://localhost
    *   **Backend API**: http://localhost:8000
    *   **API Docs**: http://localhost:8000/docs

---

## 🛠️ Local Development Installation

### Prerequisites
*   Python 3.12+
*   Node.js 20+
*   MongoDB running locally on port 27017

### 1. Backend Setup
1.  Navigate to backend folder:
    ```bash
    cd backend
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Seed the database** (Creates Admin account & test registry logs):
    ```bash
    python app/database/seed.py
    ```
4.  Start FastAPI dev server:
    ```bash
    uvicorn app.main:app --reload
    ```

### 2. Frontend Setup
1.  Navigate to frontend folder:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start React dev client:
    ```bash
    npm run dev
    ```

---

## 🚦 Testing & Auditing Scenarios

### Operator Credentials
Access the operations panel using the seeded admin credentials:
*   **Username**: `admin`
*   **Password**: `admin123`

### Section 1: Clone Detection & Spatial-Temporal Anomaly
*   **Scenario**: Flagging impossible travel times.
*   **Steps**:
    1.  Select **Section 1: Clone Detection** from the sidebar.
    2.  Select the node location as **Hyderabad Outer Ring Road**.
    3.  Upload any CCTV clip (the seed data links files containing the plate name to test values).
    4.  **Result**: The system detects the plate `AP31CV1234` was registered in Vijayawada 2 minutes ago. The implied travel speed between Vijayawada and Hyderabad is calculated (~5400 km/h), triggering a **Critical Alert** with color mismatch details.

### Section 2: Target Vehicle Search
*   **Scenario**: Bounding box matches.
*   **Steps**:
    1.  Select **Section 2: Vehicle Search** from the sidebar.
    2.  Enter the search plate query: `TS09EX5678`.
    3.  Upload your CCTV video.
    4.  **Result**: The canvas visualizer highlights the matched car with a green bounding box and displays crop slices showing OCR confidence matches.

### Section 3: Secure AI Assistant
*   **Scenario**: Zero-hallucination RAG chatbot.
*   **Queries to try**:
    *   *"List all cloned vehicles detected"* (Renders a dynamic table logs)
    *   *"Show vehicle statistics summary chart"* (Renders an interactive Recharts bar chart)
    *   *"Vehicles detected in Hyderabad"* (Queries specific location coordinate matches)
