from src.utils.state import AgentState
from langchain_core.messages import SystemMessage
from src.utils.pretty_print import beautify

def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    print("==> LLM Response:", last_message.content)
    print("==> Tool Calls:\n", last_message.tool_calls)

    if not last_message.tool_calls:
        print("No tools called.")
        return "end"
    else:
        return "continue"


def call_model(state, config, model, prompt, token_logger):
    messages = state["messages"]
    messages = [SystemMessage(prompt)] + messages
    response = model.invoke(messages)

    beautify ()
    print(f"Tokens Used: {token_logger.total_tokens}\n")
    # print(f"Successful Requests: {token_logger.successful_requests}\n")
    print(f"Total Cost (USD): {token_logger.total_cost:.6f}\n\n")

    return {
        **state,
        "messages": [response],
    }