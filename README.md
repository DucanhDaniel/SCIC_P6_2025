# SCIC P6 2025

This repository is a demo for the product used to participate in the SCIC 2025 - Student Creative Ideas Challenge 2025 of Hanoi University of Science and Technology.

## How to Use

### 1. Clone the Repository
```sh
git clone https://github.com/DucanhDaniel/SCIC_P6_2025.git
cd SCIC_P6_2025
```

### 2. Install Dependencies
Replace `<your_path_to_requirements.txt>` with the actual path to `requirements.txt`:
```sh
pip install -r <your_path_to_requirements.txt>
```

### 3. Create Your API Keys
You need the following API keys:

#### Google API Key
- Get your `GOOGLE_API_KEY` from [Google AI Studio](https://ai.google.dev/aistudio).

#### Composio API Key
1. Create an account on [Composio Platform](https://composio.io).
2. To use the app, you need to create a new connection ID with Google Docs and Composio. Follow these steps:
   ```sh
   composio add googledocs
   ```
3. Create a new connection:
   - Select **OAUTH2**.
   - Choose your **Google Account** and confirm.
4. On the Composio website:
   - Navigate to **Apps**.
   - Select **Google Docs Tool**.
   - Click **Create Integration** (violet button).
   - Click **Try Connecting Default’s Googledocs**.

#### Ngrok API Key
- Get your `NGROK_API_KEY` from [Ngrok Dashboard](https://dashboard.ngrok.com/get-started/your-authtoken).

#### SerpAPI Key
- Get your `SERAPI_API_KEY` from [SerpAPI](https://serpapi.com/).

### 4. Configure API Keys
- Put your API key into file .env 
- Get credentials.json from Google Cloud Platform: [Tutorial](https://blog.cloud-ace.vn/huong-dan-su-dung-service-account-cua-google-cloud-platform-trong-ung-dung/)
 
### 5. Run the Application
```sh
python teaching_team.py
```

### 6. Start the Streamlit App
```sh
streamlit run teaching_team.py
```

### 7. Share the App Using Ngrok
After running the app, you will get an `ngrok` link. Share this link with others to allow them to access the application remotely.



