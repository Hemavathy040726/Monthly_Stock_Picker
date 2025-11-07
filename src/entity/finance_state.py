from typing import Union, TypedDict, Annotated, Optional
from langgraph.graph import add_messages


# -------------------------------
# REDUCERS
# -------------------------------
def update_savings(existing: Union[float, None], new: Union[float, None]) -> float:
    return new if new is not None else (existing or 0.0)

def update_formatted_savings(existing: Optional[str], new: Optional[str]) -> Optional[str]:
    return new if new is not None else existing

def keep_first(existing, new):
    return existing if existing is not None else new

# -------------------------------
# STATE DEFINITION
# -------------------------------
class State(TypedDict):
    messages: Annotated[list, add_messages]
    total_savings: Annotated[Union[float, None], update_savings]
    formatted_savings: Annotated[Optional[str], update_formatted_savings]
    user_age: Annotated[Union[int, None], keep_first]
    insured: Annotated[Union[bool, None], keep_first]
    portfolio: Annotated[Union[dict, None], keep_first]
    investment_instruments: Annotated[Union[list, None], keep_first]


