from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain.agents import initialize_agent, AgentType
from langchain_community.tools import Tool, DuckDuckGoSearchResults
from langchain.utilities import GoogleSearchAPIWrapper
import streamlit as st
from tools import CustomWebScraperTool
import newspaper
import re
from datetime import date
from langchain_community.utilities import SerpAPIWrapper
import pdf_generator as pdf


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
    return agent.run(w_prompt)


def summarize_content(sum_prompt):
    scraper = CustomWebScraperTool()
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


def parse_search_results(search_result, additional_urls):
    pages_content = ""
    mod_urls = get_the_urls(search_result)
    user_urls = get_the_urls(additional_urls)
    urls = mod_urls.union(user_urls)
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


def get_research_results(topic,links):
    global search_result
    search_prompt = f"""
                        You are a researcher. Your task is to use the tools at your disposal to search
                        and return the latest development in {topic}.
            """
    if topic:
        search_result = search_relevant_content(search_prompt)
        store_the_content(search_result, topic, "doc/search/")  # here we store the search result
        search_result = parse_search_results(search_result, links)

    return search_result


def get_research_content(search_result, topic):
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

        return write_content(write_prompt)


content_summary = ""


def start_research(topic, links):
    s_result = get_research_results(topic, links)
    return get_research_content(s_result, topic)


def get_content_summary(content, topic):
    global content_summary
    sum_prompt = f"""
                                    The following content is about {topic}.
                                    ---------------------
                                    {content}
                                    ---------------------
                                    You are an expert copywriter and content creator. Please use your skills and the tools 
                                    at your disposal to complete the following tasks:
                                    Content Review: Examine this content to ensure that all information are accurate 
                                    and up-to-date.
                                    Content Summarization: Use your exceptional writing skills to summarize this content 
                                    to a 500 words long text. Make sure that it is easy to read and understand for 
                                    a non-technical audience.

                       """
    content = retrieve_content(topic)
    if content and topic:
        try:
            content_summary = summarize_content(sum_prompt)
            if content_summary:
                store_the_content(content_summary, topic, "doc/summary/")
                if st.session_state['is_show_summary']:
                    display_button(content_summary)
                    st.session_state['is_show_summary'] = False
                    st.write(content_summary)
        except Exception as ex:
            print("Error while getting the summary", ex)


def retrieve_content(topic):
    content = ""
    today = str(date.today())
    file = open("doc/content/" + today + "_" + topic + ".txt", "r")
    for line in file:
        content += line
    return content


def display_button(content_summary):
    content = ""
    topic = st.text_input(":blue[Research Topic]")
    links = st.text_area(":blue[Additional sources to consider]", placeholder="Paste your links here")

    left, middle, right = st.columns(3)
    if left.button("Start Research", key="leftbt"):
        if topic:
            content = start_research(topic,links)
            content += references
            if content:
                middle.button("Show summary", key="middlebt", on_click=get_content_summary, args=[content, topic])
                right.button("Export as pdf", key="rightbt", on_click=pdf.generate_pdf, args=[topic])
                store_the_content(search_result, topic, "doc/content/")  # Here we store the written content
                st.write(content)
            if content_summary:
                st.write(content_summary)
        else:
            st.write(":red[Please, enter a research topic]")


if __name__ == "__main__":
    if 'is_show_summary' not in st.session_state:
        st.session_state['is_show_summary'] = True
        display_button("")
    elif st.session_state['is_show_summary']:
        display_button("")
