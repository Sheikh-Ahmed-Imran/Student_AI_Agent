from langchain_core.tools import tool
from db import get_connection
import datetime
from campus_faq import CAFETERIA_TIMINGS, LIBRARY_HOURS,EVENTS
from rag import rag_chain

# ===========================
# 🎓 Student Management Tools
# ===========================

@tool
def add_student(name: str, id: str, department: str, email: str) -> str:
    """Add a new student to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Student (id, name, department, email, created_at, last_active) VALUES (?, ?, ?, ?, ?, ?)",
        (id, name, department, email, datetime.datetime.now(), datetime.datetime.now())
    )
    conn.commit()
    conn.close()  
    return f"✅ Student {name} added."


@tool
def get_student(id: str) -> str:
    """Get student details by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Student WHERE id=?", (id,))
    row = cursor.fetchone()
    conn.close()
    return str(row) if row else "❌ Student not found."


@tool
def update_student(id: str, field: str, new_value: str) -> str:
    """Update a student field (name, department, email)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE Student SET {field}=? WHERE id=?", (new_value, id))
    conn.commit()
    conn.close()
    return f"✅ Student {id} updated."


@tool
def delete_student(id: str) -> str:
    """Delete a student by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Student WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return f"🗑️ Student {id} deleted."


@tool
def list_students() -> str:
    """List all students in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Student")
    rows = cursor.fetchall()
    conn.close()
    return str(rows) if rows else "No students found."


# ======================
# 📊 Analytics Functions
# ======================

@tool
def get_total_students() -> str:
    """Get the total number of students in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Student")
    count = cursor.fetchone()[0]
    conn.close()
    return f"👥 Total students: {count}"


@tool
def get_students_by_department() -> str:
    """Get the number of students grouped by department."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT department, COUNT(*) FROM Student GROUP BY department")
    rows = cursor.fetchall()
    conn.close()
    return str(rows) if rows else "No students found."


@tool
def get_recent_onboarded_students(limit: int = 5) -> str:
    """Get the most recently onboarded students (default 5)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Student ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return str(rows) if rows else "No students found."


@tool
def get_active_students_last_7_days() -> str:
    """Get students active in the last 7 days (mock based on last_active field)."""
    conn = get_connection()
    cursor = conn.cursor()
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=7)
    cursor.execute("SELECT * FROM Student WHERE last_active >= ?", (cutoff_date,))
    rows = cursor.fetchall()
    conn.close()
    return str(rows) if rows else "No active students in the last 7 days."



@tool
def get_cafeteria_timings(day: str = None) -> str:
    """Returns cafeteria timings. Optional: specify a day (e.g., 'Saturday')."""
    if day:
        day = day.title()
        for key, val in CAFETERIA_TIMINGS.items():
            if day in key:
                return f"🕒 Cafeteria Timing on {day}: {val}"
        return f"❌ No timings found for {day}."
    return f"🕒 Cafeteria Timings: {CAFETERIA_TIMINGS}"


@tool
def get_library_hours(day: str = None) -> str:
    """Returns library hours. Optional: specify a day (e.g., 'Saturday')."""
    if day:
        day = day.title()
        for key, val in LIBRARY_HOURS.items():
            if day in key:
                return f"📚 Library Hours on {day}: {val}"
        return f"❌ No hours found for {day}."
    return f"📚 Library Hours: {LIBRARY_HOURS}"


@tool
def get_event_schedule(month: str = None) -> str:
    """
    Returns campus events. 
    Optionally filter by month (e.g., 'September' or '10' for October).
    """
    try:
        filtered_events = EVENTS
        if month:
            # Try to convert month to number
            try:
                month_num = int(month)  # if user sends "10" for October
            except ValueError:
                # convert month name to number
                month_num = datetime.datetime.strptime(month[:3], "%b").month if len(month) > 2 else datetime.datetime.strptime(month, "%B").month
            
            # Filter events by month
            filtered_events = [e for e in EVENTS if datetime.datetime.strptime(e["date"], "%Y-%m-%d").month == month_num]

            if not filtered_events:
                return f"No events found in {month}."
        
        # Format the output
        output = "\n".join([f"{e['date']} - {e['event']} at {e['time']}" for e in filtered_events])
        return output
    except Exception as e:
        return f"Error: {e}"



@tool
def campus_faq(query: str) -> str:
    """
    Provides detailed campus information. This tool can answer questions about:

    - Cafeteria timings and menu
    - Library hours and resources
    - Campus events and schedules
    - Departments and courses
    - Faculty members and subjects they teach
    - Student clubs and societies
    - Sports facilities
    - Campus guidelines and general info


    Returns:
        str: A detailed answer generated by the RAG system.
    """
    try:
        answer = rag_chain.run(query)
        return answer
    except Exception as e:
        return f"❌ Error: {e}"
