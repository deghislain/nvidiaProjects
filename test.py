from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain.agents import initialize_agent, AgentType
from langchain_community.tools import Tool, DuckDuckGoSearchResults
from langchain.utilities import GoogleSearchAPIWrapper
import streamlit as st
from tools import CustomWebScraperTool
from crewai_tools import ScrapeWebsiteTool
import newspaper
import re
from datetime import date
from langchain_community.utilities import SerpAPIWrapper


def search_relevant_content(s_prompt):
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
    return agent.run(s_prompt)


def write_content(w_prompt):
    scraper = CustomWebScraperTool()
    search = GoogleSearchAPIWrapper()
    writing_tools = [
        Tool(
            name=scraper.name,
            func=scraper.run,
            description=scraper.description
        ),
        Tool(
            name="search",
            func=search.run,
            description="Search Google for recent results.",
            return_direct=True
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
    content = agent.run(w_prompt)
    content += references
    if content:
        store_the_content(search_result, topic, "doc/content/")


def summarize_content(sum_prompt):
    scraper = ScrapeWebsiteTool()
    search = SerpAPIWrapper()
    writing_tools = [
        Tool(
            name=scraper.name,
            func=scraper.run,
            description=scraper.description
        ),
        Tool(
            name="search",
            func=search.run,
            description="Search Google for recent results.",
            return_direct=True
        ),

    ]
    llm = ChatNVIDIA(model="mistralai/mixtral-8x22b-instruct-v0.1", temperature=0)
    agent = initialize_agent(
        tools=writing_tools,
        agent_type=AgentType.SELF_ASK_WITH_SEARCH,
        llm=llm,
        handle_parsing_errors=True,
        verbose=True
    )
    return agent.run(sum_prompt)


references = '\n' + '\n' + '\n' + '\n' + '\n' + "References:" + '\n'


def get_the_urls(search_result):
    global references
    urls = set()
    links = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', search_result)
    for link in links:
        try:
            la = link.split(",", 1)
            link = la[0]
            link = link.replace('],', '')
            link = link.replace(']', '')
            references = references + link + '\n'
            urls.add(link)
        except Exception as ex:
            print("Error while retrieving the urls", ex)
    return urls


def add_document_sources(pages_content, urls):
    pages_content + '\n' + '\n'
    pages_content = pages_content + "References" + '\n'
    for l in urls:
        pages_content = pages_content + l + '\n'
    return pages_content


def parse_search_results(search_result):
    pages_content = ""
    urls = get_the_urls(search_result)
    for url in urls:
        try:
            article = newspaper.Article(url)
            article.download()
            article.parse()
            if len(article.text) > 0:
                pages_content = pages_content + article.text + '\n'
        except:
            continue
    return add_document_sources(pages_content, urls)


def store_the_content(content, topic, path):
    today = str(date.today())
    f = open(path + today + "_" + topic + ".txt", "w")
    f.write(content)
    f.close()


search_result = ""
content = ""


def get_research_content(search_result, topic):
    global content
    if search_result:
        write_prompt = f"""
                             The following content is about {topic}.
                            ---------------------
                            {search_result}
                            ---------------------
                            You are an expert copywriter and content creator. Please use your skills and the tools 
                            at your disposal to complete the following tasks:
                            Content Review: Examine the content in the search_result to ensure that all information are accurate and up-to-date.
                            Content Enrichment: Enhance the original text with additional factual information about {topic}, 
                            making sure the new details are accurate, relevant, and informative.
                            Quality Improvement: Revise the search_result content to improve readability and understanding for a non-technical audience.
                            Use clear, engaging language to make the text accessible.
                            References and Citations: At the end of your revised content, provide a list of all references and sources used, 
                            including any relevant website links.
        """

        write_content(write_prompt)

    return content


def get_research_results(topic):
    global search_result
    search_prompt = f"""
                        You are a researcher. Your task is to use the tools at your disposal to search
                        and return the latest development in {topic}.
            """
    if topic:
        search_result = search_relevant_content(search_prompt)
        store_the_content(search_result, topic, "doc/search/")  # here we store the search result
        search_result = parse_search_results(search_result)

    return search_result


def start_research(topic):
    s_result = get_research_results(topic)
    return get_research_content(s_result, topic)


if __name__ == "__main__":
    topic = st.text_input("Research Topic")
    if st.button("Start Research"):
        if topic:
            content = start_research(topic)
            #if content:
                #store_the_content(search_result, topic, "doc/content/")
        else:
            st.write("Please, enter a research topic")







  if left.button("Start Research", key="leftbt"):
        if topic:
            content = start_research(topic)
            if content:
                right.button("Export content as pdf", key="rightbt")
                content += references
                st.write(content)
                middle.button("Show summary", key="middlebt", on_click=get_content_summary, args=[content, topic])
                st.write("content_summary")
            else:
                st.write("No result found, try a another topic ")
        else:
            st.write("Please, enter a research topic")
