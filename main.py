import os
import re
import queue
import logging
import threading
from datetime import datetime

import pyaudio
from dotenv import load_dotenv
from openai import OpenAI
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
from assemblyai.streaming.v3 import (
    BeginEvent,
    RealTimeError,
    RealTimeEvents,
    RealTimeParameters,
    RealTimeTranscriber,
    RealTimeTranscriberOptions,
    TerminationEvent,
    TurnEvent,
)

load_dotenv()

DEBUG_MODE = False
FRAMES_PER_BUFFER = 800
SAMPLE_RATE = 16000
MAX_HISTORY_MESSAGES = 12
LIVE_CONTEXT_MESSAGES = 6

if DEBUG_MODE:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.CRITICAL)
    for noisy in ("httpx", "httpcore", "openai", "elevenlabs"):
        logging.getLogger(noisy).setLevel(logging.CRITICAL)

logger = logging.getLogger(__name__)

LIVE_PATTERNS = (
    r"\b(latest|newest|current|currently|today|tonight|yesterday|tomorrow|now|recent|recently|live|breaking)\b",
    r"\b(news|weather|temperature|forecast|price|prices|stock|stocks|exchange rate|exchange rates|score|scores|standings|schedule|election|elections)\b",
    r"\b(president|prime minister|chief minister|ceo|governor|mayor)\b",
    r"\b(who won|what happened|most recent|this week|this month|this year|right now|open now)\b",
)

LIVE_FOLLOWUP_PATTERNS = (
    r"^\s*(what about|how about|and what about|and how about)\b",
    r"^\s*(tell me more|more about|what else|anything else)\b",
    r"^\s*(what|who|when|where|why|how)\s+(did|does|do|is|are|was|were|has|have|will|would|can|could)\b",
)


def needs_live_info(text, previous_turn_used_live=False):
    normalized = text.lower().strip()

    if any(re.search(pattern, normalized) for pattern in LIVE_PATTERNS):
        return True

    if previous_turn_used_live and any(
        re.search(pattern, normalized)
        for pattern in LIVE_FOLLOWUP_PATTERNS
    ):
        return True

    return False


def clean_response_text(text):
    text = re.sub(r"【[^】]*】", "", text)
    text = re.sub(r"〖[^〗]*〗", "", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"(?m)^\s*#+\s*", "", text)
    text = text.replace("**", "")
    text = text.replace("__", "")
    text = text.replace("`", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


class AI_Assistant:
    def __init__(self):
        self.assemblyai_api_key = os.getenv("ASSEMBLYAI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")

        missing = [
            name
            for name, value in (
                ("ASSEMBLYAI_API_KEY", self.assemblyai_api_key),
                ("GROQ_API_KEY", self.groq_api_key),
                ("ELEVENLABS_API_KEY", self.elevenlabs_api_key),
            )
            if not value
        ]

        if missing:
            raise RuntimeError(
                "Missing environment variable(s): "
                + ", ".join(missing)
            )

        self.groq_client = OpenAI(
            api_key=self.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
            timeout=45.0,
            max_retries=1,
        )

        self.elevenlabs_client = ElevenLabs(
            api_key=self.elevenlabs_api_key
        )

        self.system_prompt = (
            "You are Prets' personal AI assistant. "
            "Give direct, concise, conversational answers suitable for speech. "
            "Avoid markdown, long lists, tables, URLs, citations, and unnecessary formatting. "
            "Keep most answers under four sentences unless the user asks for more detail. "
            "Use the recent conversation when needed for follow-up questions. "
            "If you are unsure about something, say so rather than inventing information. "
            "Ask a clarifying question only when genuinely necessary."
        )

        self.conversation = []
        self.last_turn_used_live_search = False

        self.client = None
        self.microphone_stream = None
        self.pyaudio_instance = None
        self.audio_thread = None

        self.is_streaming = False
        self.is_processing = False

        self.event_queue = queue.Queue()

    def build_normal_messages(self):
        recent = self.conversation[-MAX_HISTORY_MESSAGES:]

        return [
            {
                "role": "system",
                "content": self.system_prompt,
            },
            *recent,
        ]

    def build_live_messages(self):
        current_local_time = (
            datetime.now()
            .astimezone()
            .strftime("%A, %B %d, %Y at %I:%M %p %Z")
        )

        live_prompt = (
            "You are Prets' personal AI assistant. "
            f"The user's current local date and time is {current_local_time}. "
            "Use browser search to verify the latest available information before answering. "
            "Base the answer on current search results instead of relying on memory when freshness matters. "
            "Prefer reliable and recent sources. "
            "If sources conflict, use the most authoritative and recent information available. "
            "If reliable current information cannot be confirmed, clearly say that you could not verify it instead of guessing. "
            "Use the recent conversation context to understand pronouns and follow-up questions. "
            "Give a direct, concise, conversational answer suitable for speech. "
            "Do not include URLs, citations, citation markers, markdown, or a sources section. "
            "Keep most answers under four sentences unless the user asks for more detail."
        )

        recent = self.conversation[-LIVE_CONTEXT_MESSAGES:]

        return [
            {
                "role": "system",
                "content": live_prompt,
            },
            *recent,
        ]

    def start_transcription(self):
        if self.is_streaming:
            return

        self.client = RealTimeTranscriber(
            RealTimeTranscriberOptions(),
            api_key=self.assemblyai_api_key,
        )

        self.client.on(
            RealTimeEvents.Begin,
            self.on_begin,
        )

        self.client.on(
            RealTimeEvents.Turn,
            self.on_turn,
        )

        self.client.on(
            RealTimeEvents.Termination,
            self.on_terminated,
        )

        self.client.on(
            RealTimeEvents.Error,
            self.on_error,
        )

        self.client.connect(
            RealTimeParameters(
                sample_rate=SAMPLE_RATE,
                speech_model="universal-3-5-pro",
                min_turn_silence=150,
                max_turn_silence=1200,
            )
        )

        self.pyaudio_instance = pyaudio.PyAudio()

        self.microphone_stream = self.pyaudio_instance.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=FRAMES_PER_BUFFER,
        )

        self.is_streaming = True

        self.audio_thread = threading.Thread(
            target=self.stream_microphone,
            daemon=True,
        )

        self.audio_thread.start()

    def stream_microphone(self):
        try:
            while self.is_streaming:
                stream = self.microphone_stream
                client = self.client

                if stream is None or client is None:
                    break

                audio_data = stream.read(
                    FRAMES_PER_BUFFER,
                    exception_on_overflow=False,
                )

                client.stream(audio_data)

        except OSError:
            pass

        except Exception as error:
            if self.is_streaming:
                self.is_streaming = False

                self.event_queue.put(
                    (
                        "error",
                        f"Audio streaming error: {error}",
                    )
                )

    def stop_transcription(self):
        self.is_streaming = False

        stream = self.microphone_stream
        self.microphone_stream = None

        if stream is not None:
            try:
                if stream.is_active():
                    stream.stop_stream()
            except Exception:
                pass

            try:
                stream.close()
            except Exception:
                pass

        thread = self.audio_thread
        self.audio_thread = None

        if (
            thread is not None
            and thread.is_alive()
            and thread is not threading.current_thread()
        ):
            thread.join(timeout=1.0)

        client = self.client
        self.client = None

        if client is not None:
            try:
                client.disconnect(terminate=True)
            except Exception:
                pass

        pyaudio_instance = self.pyaudio_instance
        self.pyaudio_instance = None

        if pyaudio_instance is not None:
            try:
                pyaudio_instance.terminate()
            except Exception:
                pass

    def wait_for_event(self):
        while True:
            try:
                return self.event_queue.get(
                    timeout=0.25
                )
            except queue.Empty:
                continue

    def generate_ai_response(self, transcript_text):
        self.conversation.append(
            {
                "role": "user",
                "content": transcript_text,
            }
        )

        print(
            f"\nYou: {transcript_text}\n"
        )

        use_live_search = needs_live_info(
            transcript_text,
            self.last_turn_used_live_search,
        )

        ai_response = ""

        try:
            if use_live_search:
                print(
                    "Assistant: [Searching the web...]",
                    flush=True,
                )

                response = (
                    self.groq_client
                    .chat
                    .completions
                    .create(
                        model="openai/gpt-oss-20b",
                        messages=self.build_live_messages(),
                        temperature=0.2,
                        max_completion_tokens=512,
                        top_p=1,
                        stream=False,
                        tool_choice="required",
                        tools=[
                            {
                                "type": "browser_search",
                            }
                        ],
                    )
                )

                ai_response = (
                    response
                    .choices[0]
                    .message
                    .content
                    or ""
                )

                ai_response = clean_response_text(
                    ai_response
                )

                if ai_response:
                    print(
                        f"Assistant: {ai_response}"
                    )

            else:
                stream = (
                    self.groq_client
                    .chat
                    .completions
                    .create(
                        model="openai/gpt-oss-20b",
                        messages=self.build_normal_messages(),
                        temperature=0.6,
                        max_completion_tokens=512,
                        stream=True,
                    )
                )

                print(
                    "Assistant: ",
                    end="",
                    flush=True,
                )

                for chunk in stream:
                    content = (
                        chunk
                        .choices[0]
                        .delta
                        .content
                    )

                    if content:
                        ai_response += content

                        print(
                            content,
                            end="",
                            flush=True,
                        )

                print()

                ai_response = clean_response_text(
                    ai_response
                )

            if not ai_response:
                ai_response = (
                    "I couldn't generate a response. "
                    "Please try again."
                )

                print(
                    f"Assistant: {ai_response}"
                )

            self.conversation.append(
                {
                    "role": "assistant",
                    "content": ai_response,
                }
            )

            self.conversation = (
                self.conversation[
                    -MAX_HISTORY_MESSAGES:
                ]
            )

            self.last_turn_used_live_search = (
                use_live_search
            )

            self.generate_audio(
                ai_response
            )

        except Exception as error:
            self.last_turn_used_live_search = False

            print(
                f"\n[AI ERROR] {error}"
            )

    def generate_audio(self, text):
        audio = (
            self.elevenlabs_client
            .text_to_speech
            .convert(
                text=text,
                voice_id="pNInz6obpgDQGcFmaJgB",
                output_format="mp3_22050_32",
                model_id="eleven_turbo_v2_5",
                voice_settings=VoiceSettings(
                    stability=0.0,
                    similarity_boost=1.0,
                    style=0.0,
                    use_speaker_boost=True,
                    speed=1.0,
                ),
            )
        )

        play(audio)

    def on_begin(
        self,
        client,
        event: BeginEvent,
    ):
        if DEBUG_MODE:
            logger.info(
                f"Session started: {event.id}"
            )

        print(
            "\n[Listening... Start speaking]"
        )

    def on_turn(
        self,
        client,
        event: TurnEvent,
    ):
        if self.is_processing:
            return

        if not event.transcript:
            return

        if event.end_of_turn:
            transcript = (
                event.transcript.strip()
            )

            if not transcript:
                return

            self.is_processing = True

            print(
                "\r"
                + (" " * 140)
                + "\r",
                end="",
                flush=True,
            )

            self.event_queue.put(
                (
                    "turn",
                    transcript,
                )
            )

        else:
            print(
                f"\r{event.transcript}",
                end="",
                flush=True,
            )

    def on_terminated(
        self,
        client,
        event: TerminationEvent,
    ):
        if DEBUG_MODE:
            logger.info(
                "Session terminated: "
                f"{event.audio_duration_seconds}s processed"
            )

    def on_error(
        self,
        client,
        error: RealTimeError,
    ):
        if DEBUG_MODE:
            logger.error(
                f"Streaming error: {error}"
            )

        if not self.is_processing:
            self.is_processing = True

            self.event_queue.put(
                (
                    "error",
                    f"Transcription error: {error}",
                )
            )

    def run(self):
        greeting = (
            "Ready. What do you need?"
        )

        try:
            print(
                f"Assistant: {greeting}"
            )

            self.generate_audio(
                greeting
            )

            while True:
                self.is_processing = False

                try:
                    self.start_transcription()

                except Exception as error:
                    print(
                        "\n[TRANSCRIPTION START ERROR] "
                        f"{error}"
                    )

                    break

                event_type, payload = (
                    self.wait_for_event()
                )

                self.stop_transcription()

                if event_type == "error":
                    print(
                        f"\n[{payload}]"
                    )

                    break

                if event_type == "turn":
                    self.generate_ai_response(
                        payload
                    )

        except KeyboardInterrupt:
            print(
                "\nStopping..."
            )

        finally:
            self.stop_transcription()


if __name__ == "__main__":
    try:
        assistant = AI_Assistant()
        assistant.run()

    except KeyboardInterrupt:
        print(
            "\nStopping..."
        )

    except Exception as error:
        print(
            f"\n[STARTUP ERROR] {error}"
        )