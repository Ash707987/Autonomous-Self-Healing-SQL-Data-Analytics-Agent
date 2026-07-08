from typing import TypedDict, List, Any, Optional

class AgentState(TypedDict):
    user_query: str
    schema_context: str
    generated_sql: str
    execution_error: Optional[str]
    query_results: Optional[List[Any]]
    retry_count: int
    final_summary: str