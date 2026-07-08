import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from database import get_schema, execute_query
from state import AgentState

# Initialize LLM (Ensure OPENAI_API_KEY is set in environment)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def clean_sql(text: str) -> str:
    """Strips markdown code blocks from the generated SQL."""
    text = re.sub(r"```sql\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```\s*", "", text)
    return text.strip()

def retrieve_schema_node(state: AgentState) -> AgentState:
    """Node 1: Pulls the latest database schema into the state."""
    schema = get_schema()
    state["schema_context"] = schema
    state["retry_count"] = 0
    return state

def generate_sql_node(state: AgentState) -> AgentState:
    """Node 2: Generates syntactic SQL based on the user prompt and DDL."""
    sys_prompt = f"""You are an expert SQL engineer. 
Write a valid SQLite query to answer the user's question based strictly on the schema below.
Return ONLY the raw SQL query. Do not include markdown formatting, explanations, or quotes.

SCHEMA:
{state['schema_context']}
"""
    response = llm.invoke([
        SystemMessage(content=sys_prompt),
        HumanMessage(content=state["user_query"])
    ])
    
    state["generated_sql"] = clean_sql(response.content)
    return state

def execute_sql_node(state: AgentState) -> AgentState:
    """Node 3: Executes the SQL query in the sandbox and captures tracebacks."""
    sql = state["generated_sql"]
    results, error = execute_query(sql)
    
    if error:
        state["execution_error"] = error
        state["query_results"] = None
    else:
        state["execution_error"] = None
        state["query_results"] = results
        
    return state

def critique_and_fix_node(state: AgentState) -> AgentState:
    """Node 4 (Self-Healing): Analyzes database execution errors and rewrites the SQL."""
    state["retry_count"] += 1
    
    sys_prompt = f"""You are an expert SQL syntax debugger.
Your previous SQL query generated an execution error in SQLite.
Analyze the schema, the failed query, and the database error message. Write a corrected SQL query.
Return ONLY the raw corrected SQL query. No markdown, no explanations.

SCHEMA:
{state['schema_context']}

FAILED QUERY:
{state['generated_sql']}

DATABASE ERROR:
{state['execution_error']}
"""
    response = llm.invoke([
        SystemMessage(content=sys_prompt),
        HumanMessage(content="Fix the query to resolve the database error.")
    ])
    
    state["generated_sql"] = clean_sql(response.content)
    return state

def narrate_results_node(state: AgentState) -> AgentState:
    """Node 5: Synthesizes raw database tuples into executive insights."""
    if state["execution_error"]:
        state["final_summary"] = f"Pipeline failed after {state['retry_count']} retries. Last error: {state['execution_error']}"
        return state
        
    sys_prompt = """You are a Principal Data Analyst. 
Translate the raw SQL execution results into a concise, professional executive summary.
Highlight key figures, regional distributions, or anomalies. Do not mention SQL terminology in your output."""
    
    user_content = f"""
Original Question: {state['user_query']}
Executed Query: {state['generated_sql']}
Raw Results: {state['query_results']}
"""
    response = llm.invoke([
        SystemMessage(content=sys_prompt),
        HumanMessage(content=user_content)
    ])
    
    state["final_summary"] = response.content
    return state