# main.py
from fastapi import FastAPI, Request, HTTPException,Query
from fastapi.responses import StreamingResponse
from fastapi.responses import StreamingResponse, JSONResponse
import sqlite3
from langchain.schema import HumanMessage, AIMessage
from agent import app as agent_app 
from fastapi.middleware.cors import CORSMiddleware
import uuid
from agent import init_db
from memory import add_message, get_conversation

import asyncio
import json

app = FastAPI()


init_db()

# /chat → sync endpoint
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["*"] for all origins
    allow_credentials=True,
    allow_methods=["*"],    # GET, POST, PUT, DELETE...
    allow_headers=["*"],    # Allow all headers
)
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message", "")
    conversation_id = data.get("conversation_id")  # Optional

    # If new conversation, generate UUID
    if not conversation_id:
        conversation_id = str(uuid.uuid4())

    # Save user message
    add_message(conversation_id, "user", user_message)

    # Get all previous messages for this conversation
    rows = get_conversation(conversation_id)
    state_messages = []
    for role, content, _ in rows:
        if role.lower() == "user":
            state_messages.append(HumanMessage(content=content))
        else:
            state_messages.append(AIMessage(content=content))

    # Add latest user message if not in rows (optional)
    if not rows or rows[-1][0] != "user":
        state_messages.append(HumanMessage(content=user_message))

    state = {"messages": state_messages}

    # Call agent
    try:
        result = await agent_app.ainvoke(state)
        assistant_reply = result["messages"][-1].content
      
    except Exception as e:
        assistant_reply = "Sorry, something went wrong."
        print(e)
        add_message(conversation_id, "assistant", assistant_reply)

    # Get assistant reply
   # assistant_reply = result["messages"][-1].content  

    # Save assistant reply  
   # add_message(conversation_id, "assistant", assistant_reply)

    return JSONResponse({
        "conversation_id": conversation_id,
        "reply": assistant_reply
    })




@app.get("/chat/stream")
async def chat_stream(conversation_id: str = Query(...), message: str = Query(...)):
    # Save user message
    add_message(conversation_id, "user", message)

    # Load conversation history
    rows = get_conversation(conversation_id)
    state_messages = [
        HumanMessage(content=c) if r == "user" else AIMessage(content=c)
        for r, c, _ in rows
    ]
    state = {"messages": state_messages}

    async def event_generator():
        async for event in agent_app.astream(state):
            if "messages" in event:
                for msg in event["messages"]:
                    if msg.type == "ai":
                        add_message(conversation_id, "assistant", msg.content)
                        yield f"data: {msg.content}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
def get_db():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn


# Create student
@app.post("/students")
def create_student(student: dict):
    conn = get_db()    
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Student (name, email, department) VALUES (?, ?, ?)",
        (student["name"], student["email"], student["department"])
    )
    conn.commit()
    student_id = cur.lastrowid
    conn.close()
    return {"id": student_id, **student}


# Get all students
@app.get("/students")
def list_students():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Student")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Get single student
@app.get("/students/{student_id}")
def get_student(student_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Student WHERE id=?", (student_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Student not found")
    return dict(row)


# Update student
@app.put("/students/{student_id}")
def update_student(student_id: int, student: dict):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE Student SET name=?, age=?, department=? WHERE id=?",
        (student["name"], student["age"], student["department"], student_id)
    )
    conn.commit()
    conn.close()
    return {"id": student_id, **student}


# Delete student
@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM Student WHERE id=?", (student_id,))
    conn.commit()
    conn.close()
    return {"deleted": student_id}


@app.get("/analytics")
def analytics():
    conn = get_db()
    cur = conn.cursor()

    # Total students
    cur.execute("SELECT COUNT(*) as total FROM Student")
    total_students = cur.fetchone()["total"]

    # Students by department
    cur.execute("SELECT department, COUNT(*) as count FROM Student GROUP BY department")
    by_department = [dict(row) for row in cur.fetchall()]

    # Recent onboarded students (latest 5 by id)
    cur.execute("SELECT * FROM Student ORDER BY id DESC LIMIT 5")
    recent_students = [dict(row) for row in cur.fetchall()]

    # Mock active students last 7 days (just random sample for now)
    # Later you can add an "activity_log" table to track real events
    cur.execute("SELECT * FROM Student ORDER BY RANDOM() LIMIT 3")
    active_last_7_days = [dict(row) for row in cur.fetchall()]

    conn.close()

    return {
        "total_students": total_students,
        "by_department": by_department,
        "recent_students": recent_students,
        "active_last_7_days": active_last_7_days
    }


# List all conversations
@app.get("/conversations")
def list_conversations():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT conversation_id FROM conversations ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return {"conversation_ids": [row[0] for row in rows]}

# Get all messages of a conversation
@app.get("/conversations/{conversation_id}")
def get_conversation_messages(conversation_id: str):
    rows = get_conversation(conversation_id)
    messages = [{"role": role, "content": content, "created_at": created_at} for role, content, created_at in rows]
    return {"conversation_id": conversation_id, "messages": messages}
