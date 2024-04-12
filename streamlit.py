# import streamlit as st
# from langchain.agents import AgentType, create_react_agent
# from langchain_openai import ChatOpenAI, OpenAI
# from langchain.agents.tools import Tool
# from langchain.agents import AgentExecutor
# from langchain.prompts import PromptTemplate
# from langchain_community.tools.human import HumanInputRun
# from tools import *
# from prompts import agent_prompt1, agent_prompt2

# def create_research_agent(llm, tools, prompt):
#     """
#     Creates an agent for research and optimization.
#     :param llm: Language model to use for the agent.
#     :param tools: List of tools the agent can use.
#     :param prompt: Prompt template for the agent.
#     :return: The created agent.
#     """
#     return create_react_agent(llm, tools, prompt)

# def create_content_agent(llm, tools, prompt):
#     """
#     Creates an agent for content creation.
#     :param llm: Language model to use for the agent.
#     :param tools: List of tools the agent can use.
#     :param prompt: Prompt template for the agent.
#     :return: The created agent.
#     """
#     return create_react_agent(llm, tools, prompt)

# def validate_user_input(user_input):
#     """
#     Validates and sanitizes user input for products.
#     :param user_input: The user input string.
#     :return: The validated and sanitized user input.
#     """
#     # Perform validation and sanitization logic here
#     # Example: Split the input by commas and strip whitespace
#     products = [p.strip() for p in user_input.split(",")]
#     return

# def main():
#     st.title("Research and Content Creation Agent")

#     if "messages" not in st.session_state:
#         st.session_state.messages = []

#     research_tools = [
#         Tool(
#             name="Search Trend Analysis",
#             func=search_trend_analysis,
#             description="Analyze recent search trends using external data sources")
#     ]
#     content_tools = [
#         Tool(
#             name="User Interaction",            
#             func=HumanInputRun,
#             description="Deliver the completed article to the user for final review and gather feedback."
#         )
#     ]
#     llm = OpenAI()
#     research_agent = create_research_agent(llm, research_tools, PromptTemplate(template=agent_prompt1, input_variables=['agent_scratchpad', 'input', 'tool_names', 'tools']))
#     content_agent = create_content_agent(llm, content_tools, PromptTemplate(template=agent_prompt2, input_variables=['agent_scratchpad', 'input', 'tool_names', 'tools']))
#     research_agent_executor = AgentExecutor(
#         agent=research_agent, tools=research_tools, verbose=True, handle_parsing_errors=True
#     )
#     content_agent_executor = AgentExecutor(
#         agent=content_agent, tools=content_tools, verbose=True, handle_parsing_errors=True    )

#     try:
#         # Get user input for the Research and Optimization Agent
#         research_agent_input = st.text_input("Enter topic, key ideas, products, potential key phrases, and example articles:")

#         if research_agent_input:
#             st.session_state.messages.append({"role": "user", "content": research_agent_input})
#             # Execute the Research and Optimization Agent
#             research_output = research_agent_executor.invoke(research_agent_input)
#             st.write("Research Output:")
#             st.write(research_output["output"])
#             st.session_state.messages.append({"role": "assistant", "content": research_output["output"]})

#             # Get user input for products to mention
#             user_input = st.text_input("Enter any products you want to mention and link, separated by commas:")
#             products = validate_user_input(user_input)
#             st.session_state.messages.append({"role": "user", "content": user_input})

#             # Use the output of the Research and Optimization Agent and user input as input for the Content Creation Agent
#             content_agent_input = {
#                 "input": research_output["output"],
#                 "products": products
#             }
#             # Execute the Content Creation Agent with the research output and user product input
#             content_output = content_agent_executor.invoke(content_agent_input)
#             st.write("Final Output:")
#             st.write(content_output)
#             st.session_state.messages.append({"role": "assistant", "content": content_output})
#     except Exception as e:
#         st.error(f"An error occurred: {str(e)}")
#         st.session_state.messages.append({"role": "assistant", "content": f"An error occurred: {str(e)}"})

# if __name__ == "__main__":
#     main()