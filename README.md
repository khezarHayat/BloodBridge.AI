# BloodBridge — Peshawar Prototype

> **Connecting Lives. One Donation at a Time.**

An AI-powered emergency blood coordination platform connecting patients, donors, blood banks, and hospitals in Peshawar, Khyber Pakhtunkhwa, Pakistan.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![React](https://img.shields.io/badge/react-18-61DAFB.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.115-009688.svg)

---

## 🏗 Architecture

```
┌─────────────────┐     REST API     ┌──────────────────┐     SQL/Client     ┌──────────────┐
│   React + Vite  │ ◄──────────────► │  Python FastAPI   │ ◄───────────────► │   Supabase   │
│   (Frontend)    │                  │   (Backend)       │                   │  PostgreSQL  │
└─────────────────┘                  └──────────────────┘                   └──────────────┘
        │                                                                          │
        └──────────────── Supabase Auth / Realtime / Storage ─────────────────────┘
```

## 🚀 Tech Stack

### Frontend
- React 18 + TypeScript + Vite
- Tailwind CSS + shadcn/ui
- Framer Motion (animations)
- Leaflet + OpenStreetMap (maps)
- Recharts (analytics)
- React Hook Form + Zod (forms)
- TanStack Query (data fetching)

### Backend
- Python 3.13 + FastAPI
- Pydantic (validation)
- Supabase Python Client
- JWT Authentication
- Intelligent Matching Engine
- Structured Logging (structlog)

### Database & Services
- Supabase (PostgreSQL)
- Row Level Security (RLS)
- Supabase Auth / Storage / Realtime

---

## 📁 Project Structure

```
bloodbridge/
├── frontend/              # React application
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── layouts/       # Layout components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # API service layer
│   │   ├── contexts/      # React contexts
│   │   ├── types/         # TypeScript types
│   │   └── utils/         # Utility functions
│   └── public/
│
├── backend/               # Python FastAPI application
│   ├── app/
│   │   ├── api/           # API route handlers
│   │   ├── core/          # Config, security, DB client
│   │   ├── models/        # Database models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   ├── matching/      # Intelligent matching engine
│   │   └── utils/         # Helpers
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── supabase/              # Database migrations
│   ├── migrations/
│   └── seed.sql
│
└── README.md
```

---

## 🏁 Getting Started

### Prerequisites

- Python 3.13+
- Node.js 20+
- Supabase account (free tier works)

### 1. Clone the repository

```bash
git clone <repo-url>
cd bloodbridge
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env         # Edit with your Supabase credentials
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env         # Edit with your API URL
npm run dev
```

### 4. Database Setup

1. Create a new Supabase project
2. Run the SQL migrations in order from `supabase/migrations/`
3. Optionally run `supabase/seed.sql` for demo data

### 5. Environment Variables

**Backend** (`.env`):
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
JWT_SECRET=your-jwt-secret
CORS_ORIGINS=http://localhost:5173
```

**Frontend** (`.env`):
```
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

---

## 🔑 User Roles

| Role | Description |
|------|-------------|
| **Patient** | Create blood requests, track status, find donors |
| **Donor** | Register, manage availability, respond to invitations |
| **Blood Bank** | Manage inventory, accept requests, track batches |
| **Admin** | Platform management, verification, analytics |

---

## 🧠 Matching Engine

The Python-powered matching engine scores and ranks potential donors based on:

1. **Blood group compatibility** — medical compatibility rules
2. **Geographic proximity** — Haversine distance calculation
3. **Availability** — donor's current availability status
4. **Verification status** — verified donors score higher
5. **Emergency priority** — critical requests get boosted matching
6. **Donation recency** — ensures safe donation intervals (56+ days)

> ⚠️ **Medical Disclaimer**: Automated matching identifies *potential* donors. Final compatibility and donor eligibility must be confirmed by qualified healthcare professionals before any transfusion.

---

## 🗺 Geographic Coverage

**Initial scope**: Peshawar, Khyber Pakhtunkhwa

Supported areas:
- Hayatabad
- University Town
- Saddar
- Gulbahar
- Warsak Road
- Ring Road
- And other Peshawar areas

---

## 📊 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔒 Security

- JWT token verification on all protected endpoints
- Row Level Security (RLS) on all database tables
- Input validation with Pydantic
- Rate limiting on API endpoints
- Audit logging for sensitive operations
- Environment-based configuration (no secrets in code)

---

## ⚠️ Disclaimer

This is a **prototype** for demonstration purposes. Demo data is synthetic and clearly marked. This platform does not replace professional medical advice or blood bank operations. All blood compatibility and donor eligibility must be confirmed by qualified healthcare professionals.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

Built with ❤️ for Peshawar, Pakistan.
