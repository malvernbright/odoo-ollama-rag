from langchain_ollama import ChatOllama
# from langgraph.prebuilt import create_react_agent
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from tools.tools import (
    get_res_users, 
    get_sales_orders, 
    get_partner_details, 
    get_products
)

# ==========================================
# 3. Initialize Agent & LLM
# ==========================================
# Using 7b for reliable JSON tool-calling capabilities.
llm = ChatOllama(model="qwen3.5:4b", temperature=0)

# Register the Python functions as tools for the LLM
tools = [get_res_users, get_sales_orders, get_partner_details, get_products]

system_message = """You are the Odoo ERP Intelligent Assistant.
You have access to real-time ERP data through your tools. 
When a user asks for data, strictly use the appropriate tool to fetch it.
Do not guess or hallucinate ERP data. 
Format the data returned from your tools into a clean, professional, human-readable summary.
If a tool returns an error, inform the user politely."""

# Compile the agent graph
agent_executor = create_agent(
    llm, 
    tools, 
    system_prompt=system_message 
)

# ==========================================
# 4. Interactive Loop
# ==========================================
if __name__ == "__main__":
    print("==================================================")
    print(" GONDO Agent Initialized (Odoo + LangGraph)")
    print(" Type 'exit' or 'quit' to terminate.")
    print("==================================================\n")
    
    while True:
        try:
            uq = input("User > ")
            if uq.lower() in ['exit', 'quit']:
                print("Shutting down GONDO Assistant...")
                break
            
            if not uq.strip():
                continue
                
            print("System is thinking... (Checking tools)")
            
            # Invoke the agent with the user's message using proper typing
            response = agent_executor.invoke(
                {"messages": [HumanMessage(content=uq)]}
            )
            
            print("\n************* AfriERP *************")
            # The final response from the LLM is the last message in the list
            print(response["messages"][-1].content)
            print("***********************************\n")
            
        except KeyboardInterrupt:
            print("\nProcess interrupted. Shutting down...")
            break
        except Exception as e:
            print(f"\n[System Error]: {str(e)}\n")