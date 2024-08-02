from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain.agents import initialize_agent, AgentType
from langchain_community.tools import Tool, DuckDuckGoSearchResults
import streamlit as st
from tools import CustomWebScraperTool


def search_relevant_content(search_prompt):
    search = DuckDuckGoSearchResults()
    search_tools = [
        Tool(
            name="search",
            func=search.run,
            description="Search DuckDuckGo for recent results.",
            return_direct=True
        ),
    ]
    llm = ChatNVIDIA(model="nvidia/usdcode-llama3-70b-instruct", temperature=0)
    agent = initialize_agent(
        tools=search_tools,
        agent_type=AgentType.SELF_ASK_WITH_SEARCH,
        llm=llm,
        handle_parsing_errors=True,
        verbose=True
    )
    return agent.run(search_prompt)


def write_content(write_prompt):
    scraper = CustomWebScraperTool()
    writing_tools = [
        Tool(
            name=scraper.name,
            func=scraper.run,
            description=scraper.description
        ),
    ]
    llm = ChatNVIDIA(model="mistralai/mistral-7b-instruct-v0.3", temperature=0)
    agent = initialize_agent(
        tools=writing_tools,
        agent_type=AgentType.SELF_ASK_WITH_SEARCH,
        llm=llm,
        handle_parsing_errors=True,
        verbose=True
    )
    return agent.run(write_prompt)


if __name__ == "__main__":
    topic = st.text_input("Topic")
    content = ""
    search_prompt = f"""
                You are a researcher. Your task is to use the tools at your disposal to search
                and return the latest development in {topic}.
    """

    if topic:
        search_result = search_relevant_content(search_prompt)
        if search_result:
            write_prompt = f"""
                                 The following content is about {topic}.
                                ---------------------
                                {search_result}
                                ---------------------
                                Use the tools at your disposals to create a list of links called websites_links 
                                from the search_result content, then extract the content of each link.
                                the websites_links must be of type list and must hold a list of string representing 
                                the urls of website from the search_result content
            """

            rev_resp = write_content(write_prompt)
            st.write(rev_resp)
