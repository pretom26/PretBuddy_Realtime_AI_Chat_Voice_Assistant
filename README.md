# Real-Time AI Voice Bot (Windows 10 / VS Code)

Dental-clinic receptionist bot: AssemblyAI (streaming STT) → OpenAI (LLM) → ElevenLabs (TTS).
Adapted from AssemblyAI's tutorial — the original uses `brew`, which doesn't exist on Windows. Steps below replace it.

## 1. Python env (in VS Code's integrated terminal)

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 2. PyAudio (the one package that can fail on Windows)

Try the normal install first — recent PyAudio ships prebuilt Windows wheels:

```powershell
pip install pyaudio
```

If that errors out with a build/wheel failure, install a precompiled wheel instead:

```powershell
pip install pipwin
pipwin install pyaudio
```

## 3. mpv (audio playback — replaces `brew install mpv`)

ElevenLabs' `play()` shells out to `mpv` (or `ffplay`) to play the returned audio. Pick one:

- **winget:** `winget install mpv`
- **Chocolatey:** `choco install mpv`
- **Manual:** download from https://mpv.io/installation/, unzip, add the folder containing `mpv.exe` to your PATH, then restart VS Code's terminal.

Verify it's on PATH: `mpv --version`

## 4. API keys

Copy `.env.example` to `.env` and fill in real keys:

```powershell
copy .env.example .env
```

- AssemblyAI: https://www.assemblyai.com/dashboard/signup (free $50 credit, covers real-time)
- Groq: https://console.groq.com/keys (free, no card required — 30 req/min, 14,400 req/day on `llama-3.3-70b-versatile`)
- ElevenLabs: https://elevenlabs.io (free tier ~10 min/month, non-commercial)

The LLM step uses **Groq** instead of OpenAI — Groq's API is OpenAI-compatible, so the code just points the `openai` Python client at Groq's `base_url` with a Groq key. This whole project runs on $0.

## 5. Run it

```powershell
python main.py
```

Speak into your default mic after the greeting plays. Ctrl+C to stop.

## Windows gotchas to know about

- **Mic permissions:** Settings → Privacy & security → Microphone → make sure desktop apps (and specifically your terminal / VS Code) are allowed to use it, or PyAudio will silently get no audio.
- **Multiple audio devices:** PyAudio grabs the *default* input device. If it's picking the wrong mic, run this to list devices and note the index, then pass `input_device_index=<n>` to `pyaudio_instance.open(...)` in `main.py`:
  ```python
  import pyaudio
  p = pyaudio.PyAudio()
  for i in range(p.get_device_count()):
      print(i, p.get_device_info_by_index(i)["name"])
  ```
- **`input()` blocking on Ctrl+C:** on some Windows terminals `input()` swallows the first Ctrl+C. If stopping doesn't work cleanly, close the terminal or press Ctrl+C twice.
- **Antivirus/firewall:** first run may prompt to allow Python network access (streaming WS connections to AssemblyAI/OpenAI/ElevenLabs) — allow it.

## Next steps once it's working

- **Voice**: default is ElevenLabs voice `pNInz6obpgDQGcFmaJgB` ("Adam" — deep, neutral). Browse https://elevenlabs.io/voice-library, grab a `voice_id`, and swap it into `generate_audio()` in `main.py`.
- **Personality**: the system prompt in `AI_Assistant.__init__` is set to "sharp & efficient personal assistant" — edit it directly to change tone or scope (e.g. restrict it to coding help, add context about your schedule/projects).
- Tune AssemblyAI's latency mode (`min` vs `balanced`) and add a `keyterms_prompt` for domain vocabulary.
- Add barge-in / interrupt handling — this version stops listening while it talks, which is simple but not natural.
