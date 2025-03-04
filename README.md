### HOW TO USE
1. clone this repository: https://github.com/DucanhDaniel/SCIC_P6_2025.git
2. pip install -r ...your path to requirement.txt...
3. Create your API_KEY:
  - GOOGLE_API_KEY at https://ai.google.dev/aistudio
  - COMPOSIO_API_KEY :
        1. Create an account on Composio Platform
        2. For you to use the app, you need to make new connection ID with google docs and composio. Follow the below two steps to do so:
        3. composio add googledocs (IN THE TERMINAL) (You can also create a connection when configure google docs tools in Composio Platform).
        4. Create a new connection
        5. Select OAUTH2
        6. Select Google Account and Done.
        7. On the composio account website, go to apps, select google docs tool, and click create integration (violet button) and click Try connecting default’s googldocs button and we are done.
  - NGROK_API_KEY at https://dashboard.ngrok.com/get-started/your-authtoken
  - SERAPI_API_KEY at https://serpapi.com/
4. Replace API_KEY with your API key
5. Run teaching_team.py
6. Run streamlit command in terminal
7. You can use ngrok link provided after running the application in your terminal to other people 
