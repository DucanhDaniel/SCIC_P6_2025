import streamlit as st
from phi.agent import Agent, RunResponse
from phi.model.openai import OpenAIChat
from composio_phidata import Action, ComposioToolSet
import os
from phi.tools.arxiv_toolkit import ArxivToolkit
from phi.utils.pprint import pprint_run_response
from phi.tools.serpapi_tools import SerpApiTools

base_llms_url = "https://20e0-34-169-80-190.ngrok-free.app/v1"
llm_api_key = "token-abc123"


st.set_page_config(page_title="👨‍🏫 AI Teaching Agent Team")

if 'composio_api_key' not in st.session_state:
    st.session_state['composio_api_key'] = 'y0c4nfpdf8c493740x8wru'
if 'serpapi_api_key' not in st.session_state:
    st.session_state['serpapi_api_key'] = 'a06f4a4d80f2bdb1e2f808e2bfe0cfe8e8c4bc50767498f1ffa34c91db9425d2'

# composio_toolset = None

# try:
#     composio_toolset = ComposioToolSet(api_key=st.session_state['composio_api_key'])
# except Exception as e:
#     st.error(f"Error initializing ComposioToolSet: {e}")
#     st.stop()

# serpApi_toolset = None
# try:
#     serpApi_toolset = SerpApiTools(apiket = st.session_state['serpapi_api_key'])
# except Exception as e:
#     st.error(f"Error initializing setApi_toolset: {e}")
#     st.stop()

# google_docs_tool = composio_toolset.get_tools(
#     actions=[Action.GOOGLEDOCS_CREATE_DOCUMENT]
# )[0]
# google_docs_tool_update = composio_toolset.get_tools(
#     actions=[Action.GOOGLEDOCS_UPDATE_EXISTING_DOCUMENT]
# )[0]


# Tạo agent
teaching_assistant_agent = Agent(
    name="Teaching Assistant",
    role="Exercise Creator",
    model=OpenAIChat(id = "hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4", base_url=base_llms_url, api_key=llm_api_key),
    # tools=[google_docs_tool, serpApi_toolset],
    instructions=[
        "Create practice materials",
        "Include progressive exercises",
        "Add real-world applications",
        "Create Google Doc with solutions"
    ]
)

professor_agent = Agent(
    name="Professor",
    role="Research and Knowledge Specialist", 
    model=OpenAIChat(id = "hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4", base_url=base_llms_url, api_key=llm_api_key),
    # tools=[google_docs_tool],
    instructions=[
        "Create comprehensive knowledge base",
        "Explain from first principles",
        "Include key terminology",
        "Create formatted Google Doc"
    ]
)

academic_advisor_agent = Agent(
    name="Academic Advisor",
    role="Learning Path Designer",
    model=OpenAIChat(id = "hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4", base_url=base_llms_url, api_key=llm_api_key),
    # tools=[google_docs_tool],
    instructions=[
        "Create detailed learning roadmap",
        "Break down into subtopics",
        "Include time estimates",
        "Create formatted Google Doc"
    ]
)

# Testing agent
# response = academic_advisor_agent.run("Hello?")
# print(response.content)

with st.sidebar:
    st.title("API Keys Configuration")
    st.session_state['composio_api_key'] = st.text_input(
        "Composio API Key",
        type="password"
    )
    st.session_state['serpapi_api_key'] = st.text_input(
        "SerpAPI Key",
        type="password"
    )

def extract_google_doc_link(response_content):
    if "https://docs.google.com" in response_content:
        return response_content.split("https://docs.google.com")[1].split()[0]
    return None

topic = st.text_input(
    "Enter topic:",
    placeholder="e.g., Machine Learning"
)

if st.button("Start"):
    with st.spinner("Generating Knowledge Base..."):
        professor_response = professor_agent.run(
            f"topic: {topic}"
        )

        teaching_assistant_response = teaching_assistant_agent.run(
            f"topic: {topic}"
        )

        academic_advisor_response = academic_advisor_agent.run(
            f"topic: {topic}"
        )

    st.markdown("### Google Doc Links:")
    professor_doc_link = extract_google_doc_link(professor_response)
    if professor_doc_link is not None:
        st.markdown(f"- **Professor Document:** [View](https://docs.google.com{professor_doc_link})")

    teaching_assistant_link = extract_google_doc_link(teaching_assistant_response)
    if teaching_assistant_link is not None:
        st.markdown(f"- **Teaching Assistant Document:** [View](https://docs.google.com{teaching_assistant_link})")

    academic_advisor_link = extract_google_doc_link(academic_advisor_response)
    if academic_advisor_link is not None:
        st.markdown(f"- **Teaching Assistant Document:** [View](https://docs.google.com{academic_advisor_link})")

        

    st.markdown("### Professor Response:")
    st.markdown(professor_response.content)
    pprint_run_response(professor_response, markdown=True)

