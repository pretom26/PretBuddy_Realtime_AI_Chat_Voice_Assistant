# PretBuddy_Realtime_AI_Chat_Voice_Assistant
A real-time Python- AI oriented voice assistant using AssemblyAI, Groq web search, and ElevenLabs. 

#Developed by: Pretom Areefin Pranto
#version 1.0.1

# Real-Time AI Voice Assistant

A simple real-time voice assistant built with Python.

You speak into your microphone, the assistant converts your speech to text, generates an AI response, checks the web when fresh information is needed, and speaks the answer back to you.

The project is currently designed mainly for **Windows 10/11** and works well from **VS Code**.

---

## What It Does

The assistant combines three main AI services:

* **AssemblyAI** — converts microphone audio into text
* **Groq** — generates the AI response
* **Groq Browser Search** — retrieves current information when a question needs fresh data
* **ElevenLabs** — converts the AI response back into speech

The overall flow is:

```text
Your Microphone
      ↓
   PyAudio
      ↓
  AssemblyAI
 Speech-to-Text
      ↓
     Groq
      ↓
Normal Question ──────────────→ GPT-OSS
Current / Latest Question ────→ GPT-OSS + Browser Search
      ↓
 AI Response
      ↓
 ElevenLabs
 Text-to-Speech
      ↓
 Your Speakers
```

For example:

```text
You:
What is photosynthesis?

Assistant:
Photosynthesis is the process plants use to convert light energy into chemical energy.
```

For something that may have changed recently:

```text
You:
Who is the current Prime Minister of India?

Assistant:
[Searching the web...]

Assistant:
The current Prime Minister of India is Narendra Modi.
```

The assistant automatically decides when a question appears to require current information.

---

# Features

* Real-time microphone input
* Streaming speech recognition
* AI-powered conversation
* Short conversational memory
* Current-information detection
* Live browser search
* Spoken AI responses
* Automatic return to listening after each response
* Basic error handling
* API keys stored securely outside the Python source code
* Designed for Windows and VS Code
* Responses optimized to sound natural when spoken

---

# Technologies Used

| Component             | Technology          |
| --------------------- | ------------------- |
| Language              | Python              |
| Microphone capture    | PyAudio             |
| Speech-to-text        | AssemblyAI          |
| AI model              | Groq / GPT-OSS 20B  |
| Current information   | Groq Browser Search |
| Text-to-speech        | ElevenLabs          |
| Audio playback        | FFmpeg / ffplay     |
| Environment variables | python-dotenv       |

---

# Project Structure

Your project should look approximately like this:

```text
realtime-ai-voice-assistant/
│
├── main.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── .env
├── venv/
└── __pycache__/
```

Only these files should normally appear on GitHub:

```text
main.py
requirements.txt
README.md
.env.example
.gitignore
```

The following files should stay on your computer:

```text
.env
venv/
__pycache__/
```

---

# Before You Start

You will need:

* Windows 10 or Windows 11
* Python
* VS Code
* Git if you are cloning the project from GitHub
* A working microphone
* Speakers or headphones
* Internet access
* AssemblyAI account
* Groq account
* ElevenLabs account
* FFmpeg / ffplay

Python 3.11 or 3.12 is recommended for a smooth Windows setup.

---

# 1. Clone the Repository

If you are downloading this project from GitHub, open PowerShell, Git Bash, or the VS Code terminal and run:

```bash
git clone YOUR_REPOSITORY_URL
```

Move into the project folder:

```bash
cd realtime-ai-voice-assistant
```

If you downloaded the project manually as a ZIP, extract it and open the extracted folder in VS Code instead.

---

# 2. Open the Project in VS Code

Open VS Code and select:

```text
File → Open Folder
```

Choose the project folder.

Then open the integrated terminal:

```text
Terminal → New Terminal
```

Make sure the terminal is currently inside the project directory.

You can check using:

```powershell
pwd
```

---

# 3. Create a Python Virtual Environment

It is strongly recommended to use a virtual environment.

This keeps this project's Python packages separate from the rest of your computer.

Run:

```powershell
python -m venv venv
```

If your computer uses the Python launcher, you can also use:

```powershell
py -m venv venv
```

---

# 4. Activate the Virtual Environment

### PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

When activated successfully, your terminal should look similar to:

```text
(venv) PS C:\...\realtime-ai-voice-assistant>
```

### Git Bash

Use:

```bash
source venv/Scripts/activate
```

When you see:

```text
(venv)
```

at the beginning of your terminal line, the environment is active.

---

## PowerShell Execution Policy Error

If PowerShell refuses to activate the environment with an execution-policy error, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again:

```powershell
.\venv\Scripts\Activate.ps1
```

This only changes the execution policy for the current PowerShell session.

---

# 5. Install the Python Packages

Make sure the virtual environment is active.

Then run:

```powershell
python -m pip install --upgrade pip
```

Install the project dependencies:

```powershell
pip install -r requirements.txt
```

The project currently uses:

```text
assemblyai
pyaudio
elevenlabs
openai
python-dotenv
```

You can verify the installation with:

```powershell
pip list
```

---

# 6. Check the Python Imports

Before configuring the APIs, it is useful to make sure the packages installed correctly.

Run:

```powershell
python -c "import pyaudio; import assemblyai; import elevenlabs; import openai; import dotenv; print('All imports OK')"
```

Expected output:

```text
All imports OK
```

If you get this message, the Python environment is ready.

---

# 7. Install FFmpeg

ElevenLabs generates the assistant's speech, but an audio player is still needed to play that sound.

This project uses `ffplay`, which comes with FFmpeg.

On Windows, FFmpeg can be installed using Winget.

Run:

```powershell
winget install --id Gyan.FFmpeg -e
```

After installation, completely close VS Code and reopen it.

Then open a new terminal and test:

```powershell
ffplay -version
```

If FFmpeg is available correctly, version information should appear.

You can also check its location with:

```powershell
where.exe ffplay
```

---

## If `ffplay` Is Not Recognized

You may see:

```text
ffplay is not recognized as the name of a cmdlet...
```

First completely close VS Code instead of only closing the terminal.

Reopen VS Code and try:

```powershell
ffplay -version
```

If necessary, check whether Windows can locate it:

```powershell
where.exe ffplay
```

You may also need to verify that the Winget links folder has been added to your Windows PATH.

---

# 8. Get the API Keys

The assistant uses three different services.

Each service has a different job.

```text
AssemblyAI
Your voice → text

Groq
Text → intelligent response
Current questions → web-assisted response

ElevenLabs
AI response → spoken voice
```

You need an API key from each provider.

Do not put these keys directly inside `main.py`.

---

# AssemblyAI API Key

AssemblyAI handles real-time speech recognition.

Create an AssemblyAI account or log into your existing account.

Once you are logged in:

```text
Dashboard → API Keys
```

Create or copy your API key.

You will eventually put it in `.env` like this:

```env
ASSEMBLYAI_API_KEY=your_actual_key_here
```

Do not share this key publicly.

---

# Groq API Key

Groq runs the AI model used by the assistant.

Create a GroqCloud account or sign into your existing account.

Open:

```text
GroqCloud Console → API Keys
```

Choose:

```text
Create API Key
```

Give the key a recognizable name, such as:

```text
Voice Assistant
```

Copy it when it is created.

It will be placed in `.env`:

```env
GROQ_API_KEY=your_actual_key_here
```

The current project uses:

```text
openai/gpt-oss-20b
```

for normal conversation.

For questions that require current information, the same model can use Groq's built-in browser search.

Examples include:

```text
Who is the current president of Bangladesh?

What is the latest AI news?

What is the weather today?

Who is the current CEO of a company?
```

---

# ElevenLabs API Key

ElevenLabs gives the assistant its voice.

Create an ElevenLabs account or sign into your existing account.

Navigate to:

```text
Developers → API Keys
```

Create an API key.

You can name it something like:

```text
Voice Assistant
```

Copy the key when it is shown.

Put it in `.env`:

```env
ELEVENLABS_API_KEY=your_actual_key_here
```

For extra safety, ElevenLabs allows API keys to have restrictions and usage limits.

For a personal project, setting a reasonable credit limit on the key is a good idea.

---

# 9. Create Your `.env` File

The GitHub repository contains:

```text
.env.example
```

This is only a template.

It should look like:

```env
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
GROQ_API_KEY=your_groq_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

Create your real `.env` file.

### PowerShell

```powershell
Copy-Item .env.example .env
```

### Git Bash

```bash
cp .env.example .env
```

Now open `.env` in VS Code and replace the placeholders with your real keys:

```env
ASSEMBLYAI_API_KEY=YOUR_REAL_ASSEMBLYAI_KEY
GROQ_API_KEY=YOUR_REAL_GROQ_KEY
ELEVENLABS_API_KEY=YOUR_REAL_ELEVENLABS_KEY
```

Do not add quotation marks unless your key specifically requires them.

---

# 10. Keep `.env` Private

Your `.env` file contains credentials.

Never upload it to GitHub.

The project's `.gitignore` should contain rules similar to:

```gitignore
.env
.env.*
!.env.example

venv/
.venv/
env/

__pycache__/
*.py[cod]

.vscode/
.idea/

*.log

.DS_Store
Thumbs.db
desktop.ini
```

This keeps private and unnecessary files out of Git.

You can confirm that Git is ignoring `.env` by running:

```bash
git check-ignore -v .env
```

You can also check the virtual environment:

```bash
git check-ignore -v venv
```

If `.env` appears in:

```bash
git status
```

do not commit anything until the problem is fixed.

---

# 11. Check Microphone Permissions

The program listens through the default Windows microphone.

On Windows 10, check:

```text
Settings
→ Privacy
→ Microphone
```

Make sure microphone access is enabled for desktop applications.

On Windows 11, check:

```text
Settings
→ Privacy & security
→ Microphone
```

Make sure your microphone works normally before troubleshooting Python.

---

# 12. Test PyAudio

You can check whether PyAudio can see your computer's audio devices:

```powershell
python -c "import pyaudio; p=pyaudio.PyAudio(); print('Audio devices found:', p.get_device_count()); p.terminate()"
```

For example:

```text
Audio devices found: 25
```

A value greater than zero means PyAudio can detect audio hardware.

---

# 13. Test the API Variables

You can check whether Python sees your `.env` values without printing the actual keys.

Run:

```powershell
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('AssemblyAI:', bool(os.getenv('ASSEMBLYAI_API_KEY')), 'Groq:', bool(os.getenv('GROQ_API_KEY')), 'ElevenLabs:', bool(os.getenv('ELEVENLABS_API_KEY')))"
```

Expected result:

```text
AssemblyAI: True Groq: True ElevenLabs: True
```

This is much safer than printing the keys themselves.

---

# 14. Run the Assistant

With the virtual environment active:

```powershell
python main.py
```

You should see:

```text
Assistant: Ready. What do you need?

[Listening... Start speaking]
```

The greeting should also play through your speakers.

Now speak normally.

For example:

```text
What is the capital of Japan?
```

The terminal should show something similar to:

```text
You: What is the capital of Japan?

Assistant: The capital of Japan is Tokyo.
```

The answer should also be spoken aloud.

---

# Testing the Assistant

Before changing the code, it is useful to test the basic system properly.

### Normal knowledge

Try:

```text
What is photosynthesis?
```

```text
Explain black holes in two sentences.
```

```text
What is 25 multiplied by 12?
```

These should use the normal AI path.

---

### Conversation Memory

Try:

```text
My favorite programming language is Python.
```

Then:

```text
What programming language did I just say I like?
```

The assistant keeps a short amount of recent conversation history so that simple follow-up questions are possible.

---

### Current Information

Try:

```text
Who is the current Prime Minister of India?
```

or:

```text
Who is the current president of Bangladesh?
```

The assistant should display:

```text
Assistant: [Searching the web...]
```

before answering.

This means the live-information path was activated.

---

### Other Fresh-Information Tests

You can also try questions containing concepts such as:

```text
latest
current
today
recent
news
weather
forecast
price
president
prime minister
CEO
election
score
```

The assistant uses these types of signals to decide when an internet search may be needed.

---

# How Current Information Works

The assistant does not search the internet for every question.

That would unnecessarily increase latency and API usage.

Instead:

```text
"What is Python?"
        ↓
Normal Groq response

"Who is the current Prime Minister of India?"
        ↓
Browser search
        ↓
Current response
```

This gives normal questions faster responses while still allowing the assistant to answer time-sensitive questions.

---

# Stopping the Assistant

Press:

```text
Ctrl + C
```

to stop the program.

You should close the assistant when you are finished rather than leaving the microphone streaming unnecessarily.

---

# API Usage and Credits

AssemblyAI, Groq, and ElevenLabs are separate services.

That means they also have separate:

* usage limits
* free tiers
* billing systems
* dashboards
* API keys

Your Python program does not combine their quotas.

A simple conversation may involve:

```text
AssemblyAI
→ audio transcription usage

Groq
→ model/API usage

ElevenLabs
→ text-to-speech usage
```

A current-information question may additionally use Groq's browser-search capability.

Free tiers, prices, limits, and model availability can change over time, so check each provider's dashboard rather than relying on old quota numbers found in tutorials.

---

# API Key Expiry

An API key and an API usage quota are not the same thing.

The key is simply the credential your program uses to access the service.

A key may stop working because:

* you revoked it
* the provider disabled it
* it was configured with an expiry
* permissions were changed
* your account no longer has access
* your quota or credit was exhausted

If you generate a replacement key, update the matching value in `.env`.

You normally do not need to edit `main.py`.

---

# Security Notes

Never commit real API keys.

Never place keys directly inside:

```python
main.py
```

Never publish your real:

```text
.env
```

Never post screenshots that expose complete API keys.

Never send your API keys to someone who is helping debug the project.

If a real API key is accidentally pushed to GitHub, assume that key has been exposed.

Immediately:

1. Revoke the exposed key.
2. Create a replacement key.
3. Update your local `.env`.
4. Make sure `.env` is ignored by Git.

Simply deleting the visible key from the latest GitHub file may not remove it from previous Git history.

---

# Privacy Note

This project uses cloud APIs.

While the assistant is running:

* microphone audio is sent to AssemblyAI for transcription
* conversation text is sent to Groq for AI processing
* current-information questions may trigger web search through Groq
* response text is sent to ElevenLabs to create speech

Do not assume the assistant is completely local or offline.

Avoid speaking confidential information unless you are comfortable sending it through the services being used.

---

# Common Problems

## `ModuleNotFoundError`

Make sure the virtual environment is active:

```powershell
.\venv\Scripts\Activate.ps1
```

Then reinstall dependencies:

```powershell
pip install -r requirements.txt
```

---

## `ffplay` Is Not Recognized

Check:

```powershell
ffplay -version
```

If it fails after installation, completely close and reopen VS Code.

Then try:

```powershell
where.exe ffplay
```

This is generally a Windows PATH issue rather than a Python issue.

---

## The Assistant Cannot Hear Me

Check Windows microphone permissions.

Then test PyAudio:

```powershell
python -c "import pyaudio; p=pyaudio.PyAudio(); print(p.get_device_count()); p.terminate()"
```

Also make sure the correct microphone is selected as the Windows default input device.

---

## Missing Environment Variables

If the program reports that an API key is missing, make sure:

```text
.env
```

exists in the project directory.

The variable names must be exactly:

```env
ASSEMBLYAI_API_KEY=
GROQ_API_KEY=
ELEVENLABS_API_KEY=
```

---

## API Authentication Error

A `401` or similar authentication error usually means:

* the key is incorrect
* the key expired
* the key was revoked
* the key does not have the required permission

Generate or copy a valid key and update `.env`.

---

## Rate Limit Error

A `429` usually means an API usage or rate limit has been reached.

Check the relevant provider dashboard.

The assistant uses three different providers, so determine which API generated the error before troubleshooting.

---

## Current Question Takes Longer

This is expected.

A normal question can be answered directly by the model.

A current-information question may need to:

```text
detect that fresh information is needed
        ↓
search the web
        ↓
process search results
        ↓
generate the answer
        ↓
generate speech
```

That naturally takes longer.

---

# GitHub Workflow for Development

After the repository has already been created, your normal workflow is simple.

Check what changed:

```bash
git status
```

Review your changes:

```bash
git diff
```

Stage them:

```bash
git add .
```

Commit them:

```bash
git commit -m "Describe what changed"
```

Push them:

```bash
git push
```

For example:

```bash
git add .
git commit -m "Improve live information search"
git push
```

Before every push, make sure:

```bash
git status
```

does not show `.env`.

---

# First-Time GitHub Push

If this is a brand-new local repository:

```bash
git add .
git status
git commit -m "Initial working voice assistant"
git branch -M main
```

Create an empty repository on GitHub.

Do not create another README or `.gitignore` on GitHub if they already exist locally.

Connect the remote repository:

```bash
git remote add origin YOUR_GITHUB_REPOSITORY_URL
```

Check it:

```bash
git remote -v
```

Then push:

```bash
git push -u origin main
```

After uploading, check the GitHub repository manually.

You should see:

```text
.env.example
.gitignore
README.md
main.py
requirements.txt
```

You should not see:

```text
.env
venv/
__pycache__/
```

---

# Current Limitations

This is still a developing personal-assistant project.

Current limitations include:

* Some responses may take a few seconds.
* Web-assisted questions usually take longer than normal questions.
* Current-information detection is keyword and context based.
* AI-generated answers can still be incorrect.
* Browser search improves freshness but does not guarantee perfect factual accuracy.
* The assistant currently stops listening while generating and speaking its response.
* Full voice interruption or "barge-in" is not implemented.
* Windows application control is not yet implemented.
* The assistant does not currently operate as a background Windows service.
* Cloud APIs require an active internet connection.

---

# Possible Future Improvements

Some useful next steps for the project are:

* Lower-latency speech output
* Streaming ElevenLabs audio
* Voice interruption / barge-in
* Better conversational memory
* Wake-word detection
* Windows application control
* Commands such as:

  * "Open Microsoft Edge"
  * "Open Calculator"
  * "Open Notepad"
  * "Open VS Code"
* Volume controls
* Music controls
* Local file search
* Reminders
* Calendar integration
* Improved intent detection
* A graphical interface
* System tray support
* Better current-information source handling
* Optional fully local/offline speech components

---

# Important Reminder

Never upload this file:

```text
.env
```

Upload this instead:

```text
.env.example
```

The difference is simple:

```text
.env
→ your private credentials

.env.example
→ instructions showing what credentials are required
```

Keep the first one private.

Share the second one with the project.

---

# Final Setup Checklist

Before running:

```text
[ ] Python installed
[ ] Project opened in VS Code
[ ] Virtual environment created
[ ] Virtual environment activated
[ ] requirements.txt installed
[ ] FFmpeg installed
[ ] ffplay works
[ ] AssemblyAI API key created
[ ] Groq API key created
[ ] ElevenLabs API key created
[ ] .env created from .env.example
[ ] Three real API keys added to .env
[ ] Microphone permission enabled
[ ] .env ignored by Git
```

Then:

```powershell
python main.py
```

If everything is configured correctly, you should hear:

```text
Ready. What do you need?
```

and see:

```text
[Listening... Start speaking]
```

Your voice assistant is ready.
