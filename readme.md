# Campus Admin AI System

A full-featured **Campus Administration System** powered by **FastAPI**, **LangGraph**, and **Gemini AI**, with a **React/Next.js frontend**. This system allows admins to:

- Chat with an AI agent for student-related queries.
- Manage student records (CRUD operations).
- Monitor analytics and activity metrics.
- Track and view previous chat threads.

---

## Table of Contents

- [Features](#features)  
- [Technologies](#technologies)  
- [Project Structure](#project-structure)  
- [Getting Started](#getting-started)  
- [Backend](#backend)  
- [Frontend](#frontend)  
- [API Endpoints](#api-endpoints)  
- [Database](#database)  
- [Analytics](#analytics)  
- [Chat System](#chat-system)  
- [Deployment](#deployment)  
- [Contributing](#contributing)  
- [License](#license)  

---

## Features

### Student Management
- Create, read, update, and delete student records.
- Filter students by department.
- Add new students via a dedicated page.

### Analytics Dashboard
- Total students overview.
- Students by department (pie chart visualization).
- Recently onboarded students (list view).
- Active students in the last 7 days (bar chart visualization).

### AI Chat Agent
- Real-time chat between admin and AI agent.
- Maintains conversation threads for reference.
- Streams AI responses using `StreamingResponse` from FastAPI.

### Backend AI Integration
- Powered by **Gemini AI** using **LangGraph** workflows.
- Stores chat conversation history for context-aware responses.
- Supports both synchronous and streaming chat responses.

---

## Technologies

**Backend**:

- [Python 3.12+](https://www.python.org/)  
- [FastAPI](https://fastapi.tiangolo.com/) – API framework  
- [SQLite](https://www.sqlite.org/) – Database for student & conversation data  
- [LangGraph](https://www.langgraph.com/) – AI workflow orchestration  
- [Gemini AI](https://developers.google.com/gemini) – AI agent engine  
- CORS Middleware for frontend integration  

**Frontend**:

- [Next.js / React](https://nextjs.org/)  
- [TypeScript](https://www.typescriptlang.org/)  
- [Recharts](https://recharts.org/) – Charting for analytics  
- [TailwindCSS](https://tailwindcss.com/) – Styling components  
- [Lucide Icons](https://lucide.dev/) – UI icons  

---

cd backend
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

uvicorn main:app --reload --host 0.0.0.0 --port 8000

Database

SQLite database students.db stores:

Student table: id, name, age, department, email, created_at, last_active

Conversations table: conversation_id, role, content, created_at

Analytics Dashboard

Stats Cards: Total students, recently onboarded, active last 7 days, growth rate

Pie Chart: Students by department

Bar Chart: Active students in last 7 days (newly added)

Recent Students List: Shows latest students with department and email

Chat System

Maintains conversation history for context-aware AI responses

Supports previous thread selection like ChatGPT

Uses Gemini + LangGraph for AI reasoning
