import streamlit as st
from composio_agno import Action, ComposioToolSet
import os
# from agno.tools.arxiv import ArxivTools
from agno.utils.pprint import pprint_run_response
from agno.tools.serpapi import SerpApiTools
from agno.models.google.gemini import Gemini
from agno.agent import Agent, RunResponse
from agno.tools.duckduckgo import DuckDuckGoTools
from pyngrok import ngrok
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2 import service_account
import io
from dotenv import load_dotenv

load_dotenv()  # Load các biến từ file .env

SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/documents"]
SERVICE_ACCOUNT_FILE = "credentials.json"

def configure_authorization():
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")
    ngrok.set_auth_token(os.getenv("NGROK_AUTH_TOKEN", ""))

    if 'composio_api_key' not in st.session_state:
        st.session_state['composio_api_key'] = os.getenv("COMPOSIO_API_KEY", "")
    if 'serpapi_api_key' not in st.session_state:
        st.session_state['serpapi_api_key'] = os.getenv("SERPAPI_API_KEY", "")

def configure_tools():
    composio_toolset = None

    try:
        composio_toolset = ComposioToolSet(api_key=st.session_state['composio_api_key'])
    except Exception as e:
        st.error(f"Error initializing ComposioToolSet: {e}")
        st.stop()

    serpApi_toolset = None
    try:
        serpApi_toolset = SerpApiTools(api_key = st.session_state['serpapi_api_key'])
    except Exception as e:
        st.error(f"Error initializing setApi_toolset: {e}")
        st.stop()

    google_docs_tool = composio_toolset.get_tools(
        actions=[Action.GOOGLEDOCS_CREATE_DOCUMENT]
    )[0]
    google_docs_tool_update = composio_toolset.get_tools(
        actions=[Action.GOOGLEDOCS_UPDATE_EXISTING_DOCUMENT]
    )[0]
    return google_docs_tool, serpApi_toolset

def configure_agent(google_docs_tool, serapi_tool):
    professor_agent = Agent(
        name="Professor",
        role="Research and Knowledge Specialist", 
        model=Gemini(id="gemini-2.0-flash"), 
        tools=[google_docs_tool],
        instructions=[
            "Create a comprehensive knowledge base that covers fundamental concepts, advanced topics, and current developments of the given topic.",
            "Exlain the topic from first principles first. Include key terminology, core principles, and practical applications and make it as a detailed report that anyone who's starting out can read and get maximum value out of it.",
            "Make sure it is formatted in a way that is easy to read and understand. DONT FORGET TO CREATE THE GOOGLE DOCUMENT.",
            "Open a new Google Doc and write down the response of the agent neatly with great formatting and structure in it. **Include the Google Doc link in your response.**",
        ],
        # show_tool_calls=True,
        markdown=True,
    )

    # Create the Academic Advisor agent (formerly RoadmapArchitect)
    academic_advisor_agent = Agent(
        name="Academic Advisor",
        role="Learning Path Designer",
        model=Gemini(id="gemini-2.0-flash"),
        tools=[google_docs_tool],
        instructions=[
            "Using the knowledge base for the given topic, create a detailed learning roadmap.",
            "Break down the topic into logical subtopics and arrange them in order of progression, a detailed report of roadmap that includes all the subtopics in order to be an expert in this topic.",
            "Include estimated time commitments for each section.",
            "Present the roadmap in a clear, structured format. DONT FORGET TO CREATE THE GOOGLE DOCUMENT.",
            "Open a new Google Doc and write down the response of the agent neatly with great formatting and structure in it. **Include the Google Doc link in your response.**",

        ],
        # show_tool_calls=True,
        markdown=True
    )

    # Create the Research Librarian agent (formerly ResourceCurator)
    research_librarian_agent = Agent(
        name="Research Librarian",
        role="Learning Resource Specialist",
        model=Gemini(id="gemini-2.0-flash"),
        tools=[google_docs_tool, serapi_tool ],
        # tools = [SerpApiTools(api_key=st.session_state['serpapi_api_key'])],
        instructions=[
            "Make a list of high-quality learning resources for the given topic.",
            "Use the SerpApi search tool to find current and relevant learning materials.",
            "Using SerpApi search tool, Include technical blogs, GitHub repositories, official documentation, video tutorials, and courses.",
            "Present the resources in a curated list with descriptions and quality assessments. DONT FORGET TO CREATE THE GOOGLE DOCUMENT.",
            "Open a new Google Doc and write down the response of the agent neatly with great formatting and structure in it. **Include the Google Doc link in your response.**",
        ],
        # show_tool_calls=True,
        markdown=True,
    )

    # Create the Teaching Assistant agent (formerly PracticeDesigner)
    teaching_assistant_agent = Agent(
        name="Teaching Assistant",
        role="Exercise Creator",
        model=Gemini(id="gemini-1.5-flash"),
        tools=[google_docs_tool, serapi_tool ],
        instructions=[
            "Create comprehensive practice materials for the given topic.",
            "Use the SerpApi search tool to find example problems and real-world applications.",
            "Include progressive exercises, quizzes, hands-on projects, and real-world application scenarios.",
            "Ensure the materials align with the roadmap progression.",
            "Provide detailed solutions and explanations for all practice materials.DONT FORGET TO CREATE THE GOOGLE DOCUMENT.",
            "Open a new Google Doc and write down the response of the agent neatly with great formatting and structure in it. **Include the Google Doc link in your response.**",
        ],
        # show_tool_calls=True,
        markdown=True,
    )

    return professor_agent, academic_advisor_agent, research_librarian_agent, teaching_assistant_agent

def configure_streamlit_page():
    st.set_page_config(page_title="👨‍🏫 AI Teaching Agent Team")
    # Streamlit main UI
    st.title("👨‍🏫 AI Teaching Agent Team")
    st.markdown("Enter a topic to generate a detailed learning path and resources")

    # Add info message about Google Docs
    st.info("📝 The agents will create detailed Google Docs for each section (Professor, Academic Advisor, Research Librarian, and Teaching Assistant). The links to these documents will be displayed below after processing.")

    # Query bar for topic input
    st.session_state['topic'] = st.text_input("Enter the topic you want to learn about:", placeholder="e.g., Machine Learning, LoRA, etc.")

def get_google_services():
    """Xác thực Google Docs & Google Drive API"""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    
    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)
    
    return docs_service, drive_service

def create_google_doc(docs_service, text):
    """Tạo Google Docs mới và chèn văn bản"""
    document = docs_service.documents().create(body={"title": "Generated Document"}).execute()
    document_id = document["documentId"]

    # Chèn văn bản vào tài liệu
    requests = [{"insertText": {"location": {"index": 1}, "text": text}}]
    docs_service.documents().batchUpdate(documentId=document_id, body={"requests": requests}).execute()
    
    return document_id

def export_doc_to_pdf(drive_service, document_id):
    """Xuất Google Docs thành PDF và lấy link tải"""
    request = drive_service.files().export_media(fileId=document_id, mimeType="application/pdf")
    
    pdf_filename = f"{document_id}.pdf"
    with open(pdf_filename, "wb") as pdf_file:
        pdf_file.write(request.execute())

    return pdf_filename

def upload_pdf_to_drive(drive_service, pdf_filename):
    """Upload file PDF lên Google Drive và lấy link chia sẻ"""
    file_metadata = {"name": pdf_filename, "mimeType": "application/pdf"}
    media = MediaFileUpload(pdf_filename, mimetype="application/pdf")

    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    file_id = uploaded_file.get("id")

    # Cấp quyền xem file cho mọi người
    permission = {"role": "reader", "type": "anyone"}
    drive_service.permissions().create(fileId=file_id, body=permission).execute()

    # Lấy link truy cập file
    file_link = f"https://drive.google.com/file/d/{file_id}/view"
    return file_link

def get_pdf_link(text_content):
    if (text_content is None or text_content == ""):
        text_content = "None"
    docs_service, drive_service = get_google_services()
    
    # Bước 1: Tạo Google Docs
    document_id = create_google_doc(docs_service, text_content)

    # Bước 2: Xuất file PDF
    pdf_file = export_doc_to_pdf(drive_service, document_id)

    # Bước 3: Upload lên Google Drive & Lấy link
    pdf_link = upload_pdf_to_drive(drive_service, pdf_file) 

    return pdf_link

def runner(professor_agent, academic_advisor_agent, research_librarian_agent, teaching_assistant_agent):
    # Start button
    if st.button("Start"):
        if not st.session_state['topic']:
            st.error("Please enter a topic.")
        else:
            # Display loading animations while generating responses
            with st.spinner("Generating Knowledge Base..."):
                professor_response: RunResponse = professor_agent.run(
                    f"the topic is: {st.session_state['topic']},Don't forget to add the Google Doc link in your response.",
                    stream=False
                )
                professor_pdf_link = get_pdf_link(professor_response.content)

            with st.spinner("Generating Learning Roadmap..."):
                academic_advisor_response: RunResponse = academic_advisor_agent.run(
                    f"the topic is: {st.session_state['topic']},Don't forget to add the Google Doc link in your response.",
                    stream=False
                )
                academic_advisor_pdf_link = get_pdf_link(academic_advisor_response.content)
                
            with st.spinner("Finding Learning Resources..."):
                research_librarian_response: RunResponse = research_librarian_agent.run(
                    f"the topic is: {st.session_state['topic']},Don't forget to add the Google Doc link in your response.",
                    stream=False
                )
                research_librarian_pdf_link = get_pdf_link(research_librarian_response.content)
                
            with st.spinner("Creating Practice Materials..."):
                teaching_assistant_response: RunResponse = teaching_assistant_agent.run(
                    f"the topic is: {st.session_state['topic']},Don't forget to add the Google Doc link in your response.",
                    stream=False
                )
                teaching_assistant_pdf_link = get_pdf_link(teaching_assistant_response.content)


            
            def extract_google_doc_link(response_content):
                if response_content is None: 
                    return None
                if "https://docs.google.com" in response_content:
                    return response_content.split("https://docs.google.com")[1].split()[0].split("/edit")[0].split(")")[0].split("]")[0] + "/edit"
                return None

            professor_doc_link = extract_google_doc_link(professor_response.content)
            academic_advisor_doc_link = extract_google_doc_link(academic_advisor_response.content)
            research_librarian_doc_link = extract_google_doc_link(research_librarian_response.content)
            teaching_assistant_doc_link = extract_google_doc_link(teaching_assistant_response.content)

            # Display Google Doc links at the top of the Streamlit UI
            st.markdown("### Google Doc Links:")
            if professor_doc_link:
                st.markdown(f"- **Professor Document:** [View Document](https://docs.google.com{professor_doc_link})")
            if academic_advisor_doc_link:
                st.markdown(f"- **Academic Advisor Document:** [View Document](https://docs.google.com{academic_advisor_doc_link})")
            if research_librarian_doc_link:
                st.markdown(f"- **Research Librarian Document:** [View Document](https://docs.google.com{research_librarian_doc_link})")
            if teaching_assistant_doc_link:
                st.markdown(f"- **Teaching Assistant Document:** [View Document](https://docs.google.com{teaching_assistant_doc_link})")

            st.markdown("### PDF File Link:")
            st.markdown(f"- **Professor PDF:** [View Document]({professor_pdf_link})")
            st.markdown(f"- **Academic Advisor PDF:** [View Document]({academic_advisor_pdf_link})")
            st.markdown(f"- **Research Librarian PDF:** [View Document]({research_librarian_pdf_link})")
            st.markdown(f"- **Teaching Assistant PDF:** [View Document]({teaching_assistant_pdf_link})")
        

            # Display responses in the Streamlit UI using pprint_run_response
            st.markdown("### Professor Response:")
            st.markdown(professor_response.content)
            str = professor_response.content
            pprint_run_response(professor_response, markdown=True)
            st.divider()
            
            st.markdown("### Academic Advisor Response:")
            st.markdown(academic_advisor_response.content)
            pprint_run_response(academic_advisor_response, markdown=True)
            st.divider()

            st.markdown("### Research Librarian Response:")
            st.markdown(research_librarian_response.content)
            pprint_run_response(research_librarian_response, markdown=True)
            st.divider()

            st.markdown("### Teaching Assistant Response:")
            st.markdown(teaching_assistant_response.content)
            pprint_run_response(teaching_assistant_response, markdown=True)
            st.divider()
    # Information about the agents
    st.markdown("---")
    st.markdown("### About the Agents:")
    st.markdown("""
    - **Professor**: Researches the topic and creates a detailed knowledge base.
    - **Academic Advisor**: Designs a structured learning roadmap for the topic.
    - **Research Librarian**: Curates high-quality learning resources.
    - **Teaching Assistant**: Creates practice materials, exercises, and projects.
    """)



def create_ngrok_link():
    public_url = ngrok.connect(8501)
    print(f"Public URL: {public_url}")
    return public_url

if __name__ == "__main__":
    # create_ngrok_link()

    configure_authorization()

    google_doc_tool, serapi_tool = configure_tools()

    configure_streamlit_page()

    professor, advisor, librarian, ta = configure_agent(google_doc_tool, serapi_tool)

    runner(professor_agent=professor, academic_advisor_agent= advisor, research_librarian_agent=librarian, teaching_assistant_agent=ta)

    # print(str)



