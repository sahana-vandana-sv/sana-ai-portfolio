#AgentState is the single object that flows through every node in the graph.

from typing import TypedDict, Optional

class AgentState(TypedDict):

    days_back:int  #how many days of transactions to summarise

    # Populated by fetch_node
    transactions : list[dict] #the transactions to summarise
    total_spend : float # sum of all amounts
    category_breakdown : dict[str, float]  # {category: total_amount}

    # populated by detect_node 
    anomalies : list[dict]             # transactions flagged as anomalous

    # populated by summarise_node 
    summary : Optional[str] # a natural language summary of the transactions and anomalies
    error: Optional[str]              # set if any node fails

