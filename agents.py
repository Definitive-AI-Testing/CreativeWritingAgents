from langchain.agents import AgentType, create_react_agent
from langchain_openai import ChatOpenAI, OpenAI
from langchain_anthropic import ChatAnthropic
from langchain.agents.tools import Tool
from langchain.agents import AgentExecutor
from langchain.prompts import PromptTemplate
from tools import human_interaction_tool, web_search, keyword_research
from prompts import agent_prompt1, agent_prompt2, agent_prompt3, agent_prompt4, agent_prompt5

import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

anth_api_key = os.environ['anth_apikey']
llm = ChatAnthropic(temperature=0.3, anthropic_api_key=anth_api_key, model='claude-3-opus-20240229')
search = GoogleCustomSearchAPIWrapper()
human_input = HumanInputRun()

def create_keyword_researcher_agent():
    """Create and return the Keyword Researcher Agent."""
    keyword_researcher_tools = [
        Tool(
            name="Keyword Research Tool",
            func=search.run,
            description="Useful for researching keywords and analyzing search trends related to a topic."
        ),
        Tool(
            name="Human Input",
            func=human_input.run,
            description="Useful for when you need to ask a human for additional input or clarification."
        )
    ]

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
    """Create and return the Writing Style Analyzer Agent."""
    writing_style_analyzer_tools = [
        Tool(
            name="Human Input",
            func=human_input.run,
            description="Useful for when you need to ask the human for example article links or other input."
        ),
        Tool(
            name="Google Search",
            func=web_search,
            description="Useful for searching the web for the example article links provided by the human."
        )
    ]

    writing_style_analyzer_prompt = PromptTemplate(
        template=agent_prompt2,
        input_variables=['agent_scratchpad', 'input', 'tool_names', 'tools']  
    )

    writing_style_analyzer_agent = create_react_agent(
        llm=llm,
        tools=writing_style_analyzer_tools,
        prompt=writing_style_analyzer_prompt,
        verbose=True
    )

    return AgentExecutor(
        agent=writing_style_analyzer_agent,
        tools=writing_style_analyzer_tools,
        verbose=True,
        handle_parsing_errors=True
    )

def create_topic_researcher_agent():
    """Create and return the Topic Researcher Agent."""
    topic_researcher_tools = [
        Tool(
            name="Human Input",
            func=human_input.run,
            description="Useful for when you need to ask a human for input, like the article topic and key points to research."
        ),
        Tool(
            name="Web Search",
            func=search.run,
            description="Useful for searching the internet for information on the article topic and key points."
        )
    ]

    topic_researcher_prompt = PromptTemplate(
        template=agent_prompt3,
        input_variables=['agent_scratchpad', 'input', 'tool_names', 'tools']  
    )

    topic_researcher_agent = create_react_agent(
        llm=llm,
        tools=topic_researcher_tools,
        prompt=topic_researcher_prompt,
        verbose=True
    )

    return AgentExecutor(
        agent=topic_researcher_agent,
        tools=topic_researcher_tools,
        verbose=True,
        handle_parsing_errors=True
    )

def create_article_writer_agent():
    """Create and return the Article Writer Agent."""
    article_writer_tools = []

    article_writer_agent = create_react_agent(
        llm, 
        article_writer_tools, 
        PromptTemplate(template=agent_prompt4, input_variables=['agent_scratchpad', 'input', 'tool_names', 'tools'])
    )

    return AgentExecutor(
        agent=article_writer_agent,
        tools=article_writer_tools,
        verbose=True,
        handle_parsing_errors=True
    )

def create_editor_agent():
    """Create and return the Editor Agent."""
    editor_tools = [
        Tool(
            name="Human Input",
            func=human_interaction_tool,
            description="A tool that allows the human to review the final article, provide feedback, and approve or request revisions."
        )
    ]

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

def article_writer(keyphrases, style_guide, research_notes):
    """Run the Article Writer Agent with the provided inputs."""
    input_data = {
        "keyphrases": keyphrases,
        "style_guide": style_guide, 
        "research_notes": research_notes
    }
    
    try:
        output = article_writer_executor.invoke(input_data)
        return output
    except Exception as e:
        logger.error(f"Error in Article Writer Agent: {str(e)}")
        raise

if __name__ == "__main__":
    keyword_researcher_executor = create_keyword_researcher_agent()
    writing_style_analyzer_executor = create_writing_style_analyzer_agent()
    topic_researcher_executor = create_topic_researcher_agent()
    article_writer_executor = create_article_writer_agent()
    editor_executor = create_editor_agent()

    # Example usage
    try:
        input_data_keyword = {"input": "The article topic is 'Best practices for training a new puppy'"}
        output_keyword = keyword_researcher_executor.invoke(input_data_keyword["input"])
        logger.info(f"Keyword Researcher Agent output: {output_keyword}")

        input_data_style = {"input": "Please provide 1-3 links to example articles to analyze their writing style."}
        output_style = writing_style_analyzer_executor.invoke(input_data_style)
        logger.info(f"Writing Style Analyzer Agent output: {output_style}")

        input_data_topic_research = {"input": "Article topic: The benefits and risks of artificial intelligence. Key points to cover: Current and future AI applications, ethical considerations, impact on jobs and the economy."}
        output_topic_research = topic_researcher_executor.invoke(input_data_topic_research["input"])
        logger.info(f"Topic Researcher Agent output: {output_topic_research}")

        output_writer = article_writer(output_keyword, output_style, output_topic_research)
        logger.info(f"Article Writer Agent output: {output_writer}")

        input_data_editor = {"input": output_writer["output"]}
        output_editor = editor_executor.invoke(input_data_editor)
        logger.info(f"Editor Agent output: {output_editor}")
    except Exception as e:
        logger.error(f"Error in AI Agent chain: {str(e)}")
