from typing import Optional, Type
from pydantic.v1 import BaseModel, BaseSettings, Field
from langchain.callbacks.manager import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from langchain.agents import tool
from langchain_community.tools.human import HumanInputRun
import pandas as pd
from pytrends.request import TrendReq
from dotenv import load_dotenv
from langchain.tools import BaseTool, StructuredTool, tool
from serpapi import GoogleSearch

def get_input() -> str:
    print("Insert your text. Enter 'q' or press Ctrl-D (or Ctrl-Z on Windows) to end.")
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "q":
            break
        contents.append(line)
    return "\n".join(contents)

human_tool = HumanInputRun(input_func=get_input)


load_dotenv()

import streamlit as st
with st.sidebar:
    serp_api_key = st.text_input("SERP API Key", key="feedback_api_key", type="password")


class GoogleTrendsInput(BaseModel):
    """Input for Google Trends API tool."""
    query: str = Field(..., description="The keyword or phrase to fetch trend data for.")
    #timeframe: str = Field("today 12-m", description="The time range to fetch data for, e.g. 'today 12-m', 'today 5-y', etc.")
    # geo: str = Field("", description="The geographic location to fetch data for, e.g. 'US', 'GB', etc.")
    # cat: int = Field(0, description="The category to fetch data for, default is 0 (all categories).")

class GoogleTrendsTool(BaseTool):
    name = "google_trends"
    description = "A tool to fetch and analyze Google Trends data for a given keyword or phrase."
    args_schema: Type[BaseModel] = GoogleTrendsInput

#'Union[str, Dict]', keyword:
    def _run(self, query: str, timeframe: str = "today 12-m", geo: str = "", cat: int = 0, 
             run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Fetch and analyze Google Trends data."""

        params1 = {
        "engine": "google_trends",
        "q": query,
        "date": timeframe,
        "tz": "420",
        "geo": "US",
        "data_type": "TIMESERIES",
        "api_key": serp_api_key
        }

        params2 = {
        "engine": "google_trends",
        "q": query,
        "geo": "US",
        "data_type": "RELATED_QUERIES",
        "api_key": "787635eb77da4daf42e7253408e4cf68fc878805f403eb41685dbb16dcbc34ff"
        }

        search = GoogleSearch(params1)
        results = search.get_dict()
        interest_over_time = results["interest_over_time"]

        search = GoogleSearch(params2)
        results = search.get_dict()
        try:
            related_queries = results["related_queries"]
        except:
            related_queries = "{}"

        result = {
            "interest_over_time":interest_over_time,
            # "interest_by_region": interest_by_region_df.to_dict(),
            "related_queries": related_queries
        }

        return result
        
    async def _arun(self, keyword: str, timeframe: str = "today 12-m", geo: str = "", cat: int = 0,
                    run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("GoogleTrendsTool does not support async")
    

from langchain_community.document_loaders.web_base import WebBaseLoader
from StreamlitTools import streamlit_tool
@tool("article_web_search")
def article_web_search(query: str) -> str:
    """Get's articles from human"""
    print(query)
    human_tool = streamlit_tool._run(query)
    loader = WebBaseLoader(human_tool)
    data = loader.load()
    return data[0]

@tool("google_trends", args_schema=GoogleTrendsInput, return_direct=True)
def google_trends(query: str, timeframe: str = "today 3-m",) -> str:
        """A custom tool that integrates with the Google Trends API to fetch data on potential key phrases, handle API requests, and process the response data in a structured format for analysis."""
        params1 = {
        "engine": "google_trends",
        "q": query,
        "date": timeframe,
        "tz": "420",
        "data_type": "TIMESERIES",
        "api_key": api_key
        }

        params2 = {
        "engine": "google_trends",
        "q": query,
        "data_type": "RELATED_QUERIES",
        "api_key": "787635eb77da4daf42e7253408e4cf68fc878805f403eb41685dbb16dcbc34ff"
        }

        search = GoogleSearch(params1)
        results = search.get_dict()
        if "interest_over_time" in results:
            interest_over_time = results["interest_over_time"]
        else:
            interest_over_time = "{}"

        search = GoogleSearch(params2)
        results = search.get_dict()
        try:
            related_queries = results["related_queries"]
        except:
            related_queries = "{}"

        result = {
            "interest_over_time":interest_over_time,
            # "interest_by_region": interest_by_region_df.to_dict(),
            "related_queries": related_queries
        }

        return result

google_trends_tool = GoogleTrendsTool()

class KeywordResearchInput(BaseModel):
    topic: str = Field(description="The main topic or theme to research keywords for")
    country: str = Field(default="US", description="The country code for keyword data (default: US)")

@tool("keyword_research", args_schema=KeywordResearchInput, return_direct=False)
def keyword_research(topic: str, country: str = "US") -> str:
    """
    Performs keyword research using the Google Trends API to find relevant keywords
    and data on their search volume.

    Args:
        topic (str): The main topic or theme to research keywords for.
        country (str, optional): The country code for keyword data (default: US).

    Returns:
        str: A string representation of the keyword research data, including the query,
             average monthly searches, and competition level (if available).

    Note:
        This tool requires the `pandas` and `pytrends` libraries to be installed.
        Make sure to install them using `pip install pandas pytrends`.
    """
    try:
        # Initialize pytrends
        pytrend = TrendReq()

        # Build payload for related queries
        pytrend.build_payload(kw_list=[topic], geo=country)

        # Get related queries
        related_queries = pytrend.related_queries()

        # Get rising related queries
        rising = related_queries[topic]['rising']

        # Get top related queries
        top = related_queries[topic]['top']

        # Combine rising and top queries
        keywords = rising.append(top)

        # Drop duplicates
        keywords = keywords.drop_duplicates(subset='query')

        # Get search volume for keywords
        pytrend.build_payload(kw_list=keywords['query'].tolist(), geo=country)
        interest_over_time = pytrend.interest_over_time()

        avg_search_volume = interest_over_time.drop(columns='isPartial').mean()

        # Combine keywords and search volume
        keyword_data = pd.concat([keywords, avg_search_volume], axis=1)
        keyword_data = keyword_data.rename(columns={0: "Avg Monthly Searches"})

        # Return keyword research data
        return keyword_data.to_string(index=False)

    except Exception as e:
        return f"An error occurred during keyword research: {str(e)}"


from typing import Optional, Type
from pydantic.v1 import BaseModel, Field
from langchain.agents import tool
from langchain.tools.base import BaseTool
from googleapiclient.discovery import build
from exa_py import Exa

exaapi = "35174999-f10c-4ae3-93ee-462f509851ef"
exa = Exa(api_key=exaapi)

@tool("web-search")
def web_search(input: str) -> str:
    """Searches the web for the given query using Google Custom Search API."""
    return exa.search_and_contents(
        f"{input}",
        use_autoprompt=True,
        num_results=5,
    )



from typing import Optional
from pydantic.v1 import BaseModel, Field
from langchain.agents import tool
import json

class HumanInteractionInput(BaseModel):
    article: str = Field(description="The article to review and provide feedback on")

class HumanInteractionOutput(BaseModel):
    feedback: str = Field(description="The human's feedback on the article")
    approved: bool = Field(description="Whether the human approves the article or not")
    revision_request: Optional[str] = Field(description="Details on requested revisions, if not approved", default=None)

@tool("human_interaction_tool", args_schema=HumanInteractionInput)
def human_interaction_tool(article: str) -> str:
    """
    Displays the article to the human for review, allows them to provide feedback and approve/request revisions.
    
    Args:
        input (HumanInteractionInput): The input containing the article to review.

    Returns:
        HumanInteractionOutput: The output containing the human's feedback, approval status, and revision request (if applicable).
    """

    print(f"Please review the following article:\n{article}\n")
    
    feedback = input("Please provide your feedback on the article. Consider commenting on the clarity, coherence, and overall quality: ")
    print(f"Your feedback: {feedback}")

    while True:
        approved_input = input("Do you approve the article? (y/n): ").lower()
        if approved_input in ['y', 'n']:
            approved = approved_input == 'y'
            break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")
    
    print(f"Approved: {approved}")

    revision_request = None
    if not approved:
        revision_request = input("Please provide specific details on the revisions you would like to see: ")
        print(f"Revision request: {revision_request}")

    res = HumanInteractionOutput(
        feedback=feedback,
        approved=approved,
        revision_request=revision_request
    )

    return json.dumps(res)
