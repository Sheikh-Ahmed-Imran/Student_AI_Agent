from langgraph.graph import StateGraph, MessagesState, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.schema import HumanMessage, AIMessage
from tools import add_student, get_student, update_student, delete_student, list_students,get_total_students,get_students_by_department,get_recent_onboarded_students,get_active_students_last_7_days,campus_faq
from db import init_db
# --- Setup Gemini ---
key = "YOUR-GEMINI-KEY"
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=key,streaming=True)

# Collect tools
tools = [campus_faq,add_student, get_student, update_student, delete_student, list_students,get_total_students,get_students_by_department,get_recent_onboarded_students,get_active_students_last_7_days]
system_prompt = """    
You are a campus assistant. Use the tools as follows:
- For general campus info (cafeteria, library, events, departments, faculty, clubs, sports, guidelines, general info), always use the 'campus_faq' tool.
- For structured student database queries (add, update, delete, list, count), use the respective student management tools.
- Always prefer the most specific tool for a query.
"""
llm_with_tools = llm.bind_tools(tools, system_message=system_prompt)


# --- Define nodes ---
def llm_node(state: MessagesState):  
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# Build graph
graph = StateGraph(MessagesState)
graph.add_node("llm", llm_node)
graph.add_node("tools", ToolNode(tools))

graph.set_entry_point("llm")
graph.add_conditional_edges("llm", tools_condition, {"tools": "tools", END: END})
graph.add_edge("tools", "llm")

app = graph.compile()

# --- Simple console loop ---
if __name__ == "__main__":
    init_db() 
    print("🎓 Student Agent (type 'exit' to quit)\n")
    state = {"messages": []}
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        state["messages"].append({"role": "user", "content": user_input})
        for event in app.stream(state, stream_mode="values"):
            state = event
        print("🤖:", state["messages"][-1].content)
   