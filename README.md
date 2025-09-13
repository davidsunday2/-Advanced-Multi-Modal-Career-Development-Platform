<img width="2940" height="1646" alt="image" src="https://github.com/user-attachments/assets/1723c4b6-579c-450e-a67f-099ad1e7290c" />

An advanced, multi-modal AI Career Coach that provides personalized learning paths and simulation-based training to prepare students for the modern workforce. Powered by RAG and agentic AI workflows.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/react-v18+-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)

## 🎯 Project Concept

The AI Career Coach & Simulator is not just a chatbot—it's a practice field for professional careers. This platform addresses the urgent national need to prepare the workforce for modern jobs by teaching both technical skills and crucial soft skills through immersive simulations.

### Core Innovation: Simulation-Based Learning

Our platform creates realistic professional scenarios using agentic AI workflows:

- **Stakeholder Meetings**: Practice explaining technical concepts to non-technical managers
- **Technical Interviews**: Receive real-time feedback on coding and system design questions  
- **Presentation Skills**: Simulate conference talks and board presentations
- **Crisis Management**: Handle difficult client situations and team conflicts

## ✨ Key Features

### 🎯 Personalized Career Pathing
- AI analyzes user background against real-time job market data
- Generates customized learning roadmaps with specific skills and projects
- Adapts recommendations based on progress and market changes

### 🎮 Interactive Skill Development
- Project-based assignments aligned with career goals
- Hands-on coding challenges and portfolio building
- Integration with GitHub for project tracking

### 🎭 Professional Scenario Simulations
- **Multi-modal interactions** with voice and text support
- Real-time AI personas playing different professional roles
- Immediate feedback and performance analysis
- Recorded sessions for review and improvement

### 🗣️ Voice-Enabled Interactions
- **OpenAI Whisper** for natural speech recognition
- **Text-to-speech** for realistic AI responses
- Immersive conversation practice

## 🏗️ Technology Stack

### Backend
- **Python 3.9+** with **FastAPI** for high-performance APIs
- **LangChain** for complex AI workflow orchestration
- **OpenAI GPT-4** for coaching and simulations
- **Whisper API** for speech-to-text processing
- **Pinecone** for vector database and embeddings
- **PostgreSQL** for user data and session history
- **Redis** for real-time caching and session management

### Frontend
- **React 18** with modern hooks and context
- **TypeScript** for type safety
- **Tailwind CSS** for responsive design
- **WebSocket** connections for real-time interactions
- **Web Audio API** for voice processing

### AI/ML
- **RAG (Retrieval-Augmented Generation)** for job market intelligence
- **Agentic AI workflows** for complex simulations
- **Custom embeddings** for career and skills matching
- **Real-time job data** via SerpAPI integration

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose (recommended)
- OR Python 3.9+, Node.js 16+, PostgreSQL 14+, Redis 6+

### Option 1: Docker Setup (Recommended)

```bash
# Clone and setup
git clone <repository-url>
cd ai-career-coach-simulator

# Run setup script
./scripts/setup.sh

# Edit backend/.env with your API keys
# Required: OPENAI_API_KEY, PINECONE_API_KEY, SERPAPI_API_KEY

# Start all services
./scripts/start.sh
```

### Option 2: Manual Setup

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp env_template.txt .env
# Edit .env with your API keys

# Start PostgreSQL and Redis locally
# Update DATABASE_URL and REDIS_URL in .env accordingly

# Start the backend server
python main.py
```

#### Frontend Setup
```bash
cd frontend
npm install

# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000" > .env
echo "REACT_APP_WEBSOCKET_URL=ws://localhost:8000/ws" >> .env

# Start development server
npm start
```

## 📋 Environment Variables

### Backend (.env)
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Vector Database
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=career-coach-index

# Job Market Data
SERPAPI_API_KEY=your_serpapi_api_key_here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/career_coach
REDIS_URL=redis://localhost:6379

# Voice Processing
WHISPER_MODEL=whisper-1
TTS_MODEL=tts-1

# Security
SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend (.env)
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WEBSOCKET_URL=ws://localhost:8000/ws
REACT_APP_FIREBASE_API_KEY=your_firebase_api_key
REACT_APP_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your_project_id
```

## 🏛️ Project Structure

```
ai-career-coach-simulator/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   ├── core/              # Core functionality
│   │   ├── models/            # Database models
│   │   ├── services/          # Business logic
│   │   └── utils/             # Utilities
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Backend tests
│   └── requirements.txt       # Python dependencies
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/            # Page components
│   │   ├── hooks/            # Custom hooks
│   │   ├── services/         # API services
│   │   └── utils/            # Utilities
│   ├── public/               # Static assets
│   └── package.json          # Node dependencies
├── database/                  # Database scripts
│   ├── migrations/           # SQL migrations
│   └── seed/                 # Sample data
├── docs/                     # Documentation
│   ├── api/                  # API documentation
│   ├── user-guide/           # User guides
│   └── technical/            # Technical docs
├── scripts/                  # Deployment scripts
└── docker-compose.yml        # Container orchestration
```

## 🎬 Demo Scenarios

### 1. Career Path Discovery
```
User: "I want to become a Data Scientist"
AI Coach: Analyzes background → Generates personalized roadmap
Output: "Master Python → Learn ML → Build portfolio → Practice interviews"
```

### 2. Stakeholder Meeting Simulation
```
AI Manager: "Explain why our conversion rate dropped 15%"
User: [Provides technical analysis]
AI Manager: "But how does this translate to revenue impact?"
AI Coach: [Post-simulation] "Great analysis! Try using business metrics next time..."
```

### 3. Technical Interview Practice
```
AI Interviewer: "Design a recommendation system for Netflix"
User: [Describes architecture]
AI: "How would you handle the cold start problem?"
[Real-time feedback on system design thinking]
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests  
cd frontend
npm test

# Integration tests
npm run test:e2e
```



## 📖 Documentation

- [API Documentation](docs/api/README.md)
- [User Guide](docs/user-guide/README.md)
- [Technical Architecture](docs/technical/ARCHITECTURE.md)
- [Deployment Guide](docs/technical/DEPLOYMENT.md)


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

