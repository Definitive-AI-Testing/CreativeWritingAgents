import streamlit as st
from typing import TypedDict, Annotated, List, Union, Dict, Any
from langchain.agents import AgentType, create_react_agent
from langchain_openai import ChatOpenAI, OpenAI
from langchain_anthropic import ChatAnthropic
from langchain.agents.tools import Tool
from langchain.agents import AgentExecutor
from langchain.prompts import PromptTemplate
from tools import google_trends_tool, web_search
from StreamlitTools import streamlit_tool
from reflection import create_reflection_agent
from prompts import agent_prompt1, agent_prompt2, agent_prompt3, agent_prompt4, agent_prompt5
from langgraph.graph import END, StateGraph
from dotenv import load_dotenv
import os
import logging

load_dotenv('Outputs/enviroment.env')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

anth_api_key = os.environ['ANTH_API_KEY']
llm = ChatAnthropic(temperature=0.3, anthropic_api_key=anth_api_key, model='claude-3-opus-20240229')

class ArticleWritingState(TypedDict):
    input: str
    keyword_researcher_output: Dict[str, Any]
    writing_style_analyzer_output: Dict[str, Any]
    topic_researcher_output: Dict[str, Any]
    article_writer_output: Dict[str, Any]
    editor_output: Dict[str, Any]

def create_keyword_researcher_agent():
    keyword_researcher_tools = [ streamlit_tool, google_trends_tool] 

    keyword_researcher_agent = create_react_agent(
        llm, 
        keyword_researcher_tools, 
        PromptTemplate(template=agent_prompt1, input_variables=['agent_scratchpad', 'input', 'tool_names', 'tools'])
    )

    return AgentExecutor(
        agent=keyword_researcher_agent,
        tools=keyword_researcher_tools, 
        verbose=True,
        handle_parsing_errors=True
    )

def create_writing_style_analyzer_agent():
    writing_style_analyzer_tools = [streamlit_tool, web_search] 

    writing_style_analyzer_prompt = PromptTemplate(
        template=agent_prompt2,
        input_variables=['agent_scratchpad', 'input', 'tool_names', 'tools']  
    )

    writing_style_analyzer_agent = create_react_agent(
        llm=llm,
        tools=writing_style_analyzer_tools,
        prompt=writing_style_analyzer_prompt
    )

    return AgentExecutor(
        agent=writing_style_analyzer_agent,
        tools=writing_style_analyzer_tools,
        verbose=True,
        handle_parsing_errors=True
    )

def create_topic_researcher_agent():
    topic_researcher_tools = [streamlit_tool, web_search]
 
    topic_researcher_prompt = PromptTemplate(
        template=agent_prompt3,
        input_variables=['agent_scratchpad', 'input', 'tool_names', 'tools']  
    )

    topic_researcher_agent = create_react_agent(
        llm=llm,
        tools=topic_researcher_tools,
        prompt=topic_researcher_prompt
    )

    return AgentExecutor(
        agent=topic_researcher_agent,
        tools=topic_researcher_tools,
        verbose=True,
        handle_parsing_errors=True
    )

def create_article_writer_agent():

    article_writer_agent = create_reflection_agent(
        llm, 
        agent_prompt4, 
        4)
    return article_writer_agent

def create_editor_agent():
    editor_tools = [streamlit_tool]

    editor_agent = create_react_agent(
        llm, 
        editor_tools, 
        PromptTemplate(template=agent_prompt5, input_variables=['agent_scratchpad', 'input', 'tool_names', 'tools'])
    )

    return AgentExecutor(
        agent=editor_agent,
        tools=editor_tools,
        verbose=True,
        handle_parsing_errors=True
    )

keyword_researcher_executor = create_keyword_researcher_agent()
writing_style_analyzer_executor = create_writing_style_analyzer_agent()
topic_researcher_executor = create_topic_researcher_agent()
article_writer_executor = create_article_writer_agent()
editor_executor = create_editor_agent()

def keyword_researcher_node(state):
    output = keyword_researcher_executor.invoke({"input": state["input"]})
    return {**state, "keyword_researcher_output": output}

def writing_style_analyzer_node(state):
    output = writing_style_analyzer_executor.invoke({"input": state["keyword_researcher_output"]["output"]})
    return {**state, "writing_style_analyzer_output": output}

def topic_researcher_node(state):
    output = topic_researcher_executor.invoke({"input": state["writing_style_analyzer_output"]["output"]})
    return {**state, "topic_researcher_output": output}

def article_writer_node(state):
    input_data = {
        "keyphrases": state["keyword_researcher_output"]["output"],
        "style_guide": state["writing_style_analyzer_output"]["output"],
        "research_notes": state["topic_researcher_output"]["output"]
    }
    output = article_writer_executor.invoke(input_data)
    return {**state, "article_writer_output": output}

def editor_node(state):
    output = editor_executor.invoke({"input": state["article_writer_output"]["output"]})
    return {**state, "editor_output": output}

def should_revise(state):
    if "revise" in state["editor_output"]["output"].lower():
        return "revise"
    else:
        return "end"
      
def main():
    st.title("Research and Content Creation Agent")
    try:
        # Get user input for the Research and Optimization Agent
        research_agent_input = st.text_input("Enter topic, key ideas, products, potential key phrases, and example articles:")

        if research_agent_input:
            workflow = StateGraph(ArticleWritingState)
            workflow.add_node("keyword_researcher", keyword_researcher_node)
            workflow.add_node("writing_style_analyzer", writing_style_analyzer_node)
            workflow.add_node("topic_researcher", topic_researcher_node)
            workflow.add_node("article_writer", article_writer_node)
            workflow.add_node("editor", editor_node)

            workflow.set_entry_point("keyword_researcher")
            workflow.add_edge("keyword_researcher", "writing_style_analyzer")
            workflow.add_edge("writing_style_analyzer", "topic_researcher")
            workflow.add_edge("topic_researcher", "article_writer")
            workflow.add_conditional_edges(
                "article_writer",
                should_revise,
                {
                    "revise": "editor",
                    "end": END,
                },
            )
            workflow.add_edge("editor", END)

            app = workflow.compile()

            input_data = {"input": research_agent_input}
            for s in app.stream(input_data):
                print(s)
            # st.write("Final Output:")
            # st.write(content_output)
            # st.session_state.messages.append({"role": "assistant", "content": content_output})
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.session_state.messages.append({"role": "assistant", "content": f"An error occurred: {str(e)}"})

if __name__ == "__main__":
    main()