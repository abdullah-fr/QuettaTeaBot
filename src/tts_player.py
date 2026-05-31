"""Text-to-Speech and voice conversation commands for Discord VC."""
import asyncio
import io as _io
import os
import re as _re
import ssl
import tempfile
import threading
import time as _time
import wave as _wave
from dataclasses import dataclass, field as _field
from typing import Optional

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

try:
    import discord.ext.voice_recv as voice_recv
    _VOICE_RECV_AVAILABLE = True
except ImportError:
    _VOICE_RECV_AVAILABLE = False

# ---------------------------------------------------------------------------
# SSL patch for Discord regional voice servers
# ---------------------------------------------------------------------------
def _patch_discord_voice_ssl() -> None:
    _orig = aiohttp.ClientSession.ws_connect

    def _patched(self, url, *args, **kwargs):  # type: ignore[override]
        if "discord.media" in str(url) and "ssl" not in kwargs:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            kwargs["ssl"] = ctx
        return _orig(self, url, *args, **kwargs)

    aiohttp.ClientSession.ws_connect = _patched  # type: ignore[method-assign]


_patch_discord_voice_ssl()

try:
    from logging_config import get_logger
    from api_helpers import (
        fetch_ai_dead_chat_starter,
        _get_gemini_keys,
        _gemini_request,
        _pcm_to_wav_bytes,
    )
    from config import settings as _settings
except ImportError:
    from .logging_config import get_logger
    from .api_helpers import (
        fetch_ai_dead_chat_starter,
        _get_gemini_keys,
        _gemini_request,
        _pcm_to_wav_bytes,
    )
    from .config import settings as _settings

logger = get_logger(__name__)

_VOICES: dict[str, str] = {
    "en-US-AriaNeural": "English — Aria (Female)",
    "en-US-GuyNeural": "English — Guy (Male)",
    "ur-PK-AsadNeural": "Urdu — Asad (Male)",
    "ur-PK-UzmaNeural": "Urdu — Uzma (Female)",
}
DEFAULT_VOICE = "en-US-AriaNeural"

_NOISE_TRANSCRIPTS = {
    "", ".", "..", "...", "you", "thank you", "thank you.", "thanks", "thanks.",
    "hmm", "hmm.", "um", "uh", "okay", "ok", "bye", "bye.", "yes", "no",
}

# ---------------------------------------------------------------------------
# Text preprocessing
# ---------------------------------------------------------------------------
_ABBREV_MAP = [
    (_re.compile(r'\blol\b', _re.I), 'haha'),
    (_re.compile(r'\bomg\b', _re.I), 'oh my god'),
    (_re.compile(r'\btbh\b', _re.I), 'to be honest'),
    (_re.compile(r'\bngl\b', _re.I), 'not gonna lie'),
    (_re.compile(r'\bimo\b', _re.I), 'in my opinion'),
    (_re.compile(r'\bbtw\b', _re.I), 'by the way'),
    (_re.compile(r'\bidk\b', _re.I), "I don't know"),
    (_re.compile(r'\bidc\b', _re.I), "I don't care"),
    (_re.compile(r'\bsmh\b', _re.I), 'shaking my head'),
    (_re.compile(r'\bfr\b', _re.I), 'for real'),
    (_re.compile(r'\bnvm\b', _re.I), 'never mind'),
    (_re.compile(r'\bbrb\b', _re.I), 'be right back'),
    (_re.compile(r'\bwtf\b', _re.I), 'what the heck'),
    (_re.compile(r'\*{1,3}(.+?)\*{1,3}', _re.S), r'\1'),
    (_re.compile(r'`+(.+?)`+', _re.S), r'\1'),
    (_re.compile(r'#+\s*'), ''),
    (_re.compile(r'\[(.+?)\]\(.+?\)'), r'\1'),
    (_re.compile(r'\n+'), ' '),
    (_re.compile(r'  +'), ' '),
]


def _prep_text_for_tts(text: str) -> str:
    for pattern, replacement in _ABBREV_MAP:
        text = pattern.sub(replacement, text)
    return text.strip()


# ---------------------------------------------------------------------------
# Core TTS helper
# ---------------------------------------------------------------------------
async def _tts_to_file(text: str, voice: str) -> str:
    try:
        import edge_tts
    except ImportError as exc:
        raise RuntimeError("edge-tts is not installed. Run: pip install edge-tts") from exc

    text = _prep_text_for_tts(text)
    if voice.startswith("ur-"):
        rate, pitch = "-3%", "-2Hz"
    else:
        rate, pitch = "-8%", "-3Hz"

    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    fd, path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    await communicate.save(path)
    return path


# ---------------------------------------------------------------------------
# Audio transcription using Gemini
# ---------------------------------------------------------------------------
async def _transcribe_audio(wav_bytes: bytes) -> str | None:
    """Transcribe WAV audio using Gemini."""
    import base64
    keys = _get_gemini_keys()
    if not keys:
        return None

    audio_b64 = base64.b64encode(wav_bytes).decode()
    result = await _gemini_request(
        system="Transcribe exactly what is spoken in this audio. Return only the words spoken, nothing else.",
        user=f"[Audio data provided as base64: {audio_b64[:100]}...]",
        max_tokens=120,
        temperature=0.0,
    )
    return result


# ---------------------------------------------------------------------------
# VC conversation reply
# ---------------------------------------------------------------------------
async def _fetch_ai_converse_reply(
    history: list[dict],
    speaker_name: str,
    text: str,
) -> str | None:
    """Short spoken reply for a live VC conversation."""
    _SYSTEM = (
        "You are a voice chat participant in Quetta Tea Corner, a Pakistani Discord server. "
        "You're having a casual spoken conversation with real people in a voice channel.\n\n"
        "Rules:\n"
        "- Reply in 1-2 short sentences, max 20 words total\n"
        "- Match the language of what they said: Roman Urdu mix or English\n"
        "- Be casual, reactive, occasionally funny — like a real friend in VC\n"
        "- NO emojis, NO asterisks, NO markdown — this will be spoken aloud by TTS\n"
        "- Use contractions (it's, don't, that's) — they sound natural when spoken\n"
        "- No filler openers like 'Well,' or 'Great question!' — dive straight in\n"
        "Reply with ONLY the spoken response, nothing else."
    )

    history_text = "\n".join(
        f"{'Bot' if m['role'] == 'assistant' else 'User'}: {m['content']}"
        for m in history[-10:]
    )

    return await _gemini_request(
        system=_SYSTEM,
        user=(
            f"Conversation so far:\n{history_text}\n\n"
            f"{speaker_name} just said: {text}\n\n"
            "Your spoken reply:"
        ),
        max_tokens=60,
        temperature=0.9,
    )


# ---------------------------------------------------------------------------
# VC join helper
# ---------------------------------------------------------------------------
async def _ensure_voice_client(
    interaction: discord.Interaction,
) -> Optional[discord.VoiceClient]:
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.followup.send(
            "❌ Join a voice channel first, then run `/speak`.", ephemeral=True
        )
        return None

    channel = interaction.user.voice.channel
    existing: Optional[discord.VoiceClient] = interaction.guild.voice_client  # type: ignore
    if existing:
        if existing.channel.id != channel.id:
            await existing.move_to(channel)
        return existing

    try:
        return await channel.connect()
    except Exception as exc:
        logger.exception("Failed to connect to VC")
        await interaction.followup.send(
            f"❌ Could not join the voice channel: {exc}", ephemeral=True
        )
        return None


# ---------------------------------------------------------------------------
# Conversation system
# ---------------------------------------------------------------------------
if _VOICE_RECV_AVAILABLE:
    class _ConversationSink(voice_recv.AudioSink):  # type: ignore[misc]
        SILENCE_THRESHOLD = 0.8
        MIN_PCM_BYTES = 76_800

        def __init__(self) -> None:
            super().__init__()
            self._lock = threading.Lock()
            self._buffers: dict[int, bytearray] = {}
            self._last_seen: dict[int, float] = {}

        def wants_opus(self) -> bool:
            return False

        def write(self, user, data) -> None:  # type: ignore[override]
            if user is None:
                return
            pcm = data.pcm if hasattr(data, "pcm") else data
            if not pcm:
                return
            uid = user.id if hasattr(user, "id") else int(user)
            now = _time.monotonic()
            with self._lock:
                self._last_seen[uid] = now
                self._buffers.setdefault(uid, bytearray()).extend(pcm)

        def cleanup(self) -> None:
            with self._lock:
                self._buffers.clear()
                self._last_seen.clear()

        def drain_user(self, user_id: int) -> Optional[bytes]:
            with self._lock:
                data = self._buffers.pop(user_id, None)
                self._last_seen.pop(user_id, None)
                if not data or len(data) < self.MIN_PCM_BYTES:
                    return None
                return bytes(data)

        def silent_users(self) -> list[int]:
            now = _time.monotonic()
            with self._lock:
                return [
                    uid
                    for uid, last in list(self._last_seen.items())
                    if now - last >= self.SILENCE_THRESHOLD and uid in self._buffers
                ]
else:
    _ConversationSink = None  # type: ignore


@dataclass
class _ConversationSession:
    vc: discord.VoiceClient
    sink: object
    text_channel: discord.abc.Messageable
    guild: discord.Guild
    voice: str = DEFAULT_VOICE
    history: list = _field(default_factory=list)
    is_responding: bool = False
    last_activity: float = _field(default_factory=_time.monotonic)
    monitor_task: Optional[asyncio.Task] = None


_active_sessions: dict[int, _ConversationSession] = {}
_INACTIVITY_TIMEOUT = 600
_MONITOR_INTERVAL = 0.4


async def _process_speech(
    session: _ConversationSession, user_id: int, pcm: bytes
) -> None:
    if session.is_responding:
        return
    session.is_responding = True
    session.last_activity = _time.monotonic()
    try:
        wav = _pcm_to_wav_bytes(pcm)
        text = await _transcribe_audio(wav)
        if not text or text.strip().lower() in _NOISE_TRANSCRIPTS:
            return
        if len(text.split()) < 2:
            return

        member = session.guild.get_member(user_id)
        speaker = member.display_name if member else "Someone"

        try:
            await session.text_channel.send(f"🎤 **{speaker}:** {text}", silent=True)
        except Exception:
            pass

        session.history.append({"role": "user", "content": f"{speaker} said: {text}"})
        reply = await _fetch_ai_converse_reply(session.history, speaker, text)
        if not reply:
            return

        session.history.append({"role": "assistant", "content": reply})
        if len(session.history) > 20:
            session.history = session.history[-20:]

        try:
            await session.text_channel.send(f"🤖 **Bot:** {reply}", silent=True)
        except Exception:
            pass

        while session.vc.is_playing():
            await asyncio.sleep(0.2)

        audio_path = await _tts_to_file(reply[:500], session.voice)
        done_event = asyncio.Event()
        loop = asyncio.get_event_loop()

        def _after(error: Optional[Exception]) -> None:
            try:
                os.unlink(audio_path)
            except OSError:
                pass
            loop.call_soon_threadsafe(done_event.set)

        source = discord.FFmpegPCMAudio(audio_path)
        session.vc.play(source, after=_after)
        await done_event.wait()
    except Exception:
        logger.exception("Speech processing failed")
    finally:
        session.is_responding = False


async def _silence_monitor(guild_id: int) -> None:
    while guild_id in _active_sessions:
        await asyncio.sleep(_MONITOR_INTERVAL)
        session = _active_sessions.get(guild_id)
        if not session:
            return
        if _time.monotonic() - session.last_activity > _INACTIVITY_TIMEOUT:
            try:
                await session.text_channel.send(
                    "💤 No activity for 10 minutes — ending conversation."
                )
            except Exception:
                pass
            await _end_conversation(guild_id)
            return
        if not session.vc.is_connected():
            await _end_conversation(guild_id)
            return
        for user_id in session.sink.silent_users():
            if session.is_responding:
                break
            pcm = session.sink.drain_user(user_id)
            if pcm:
                asyncio.create_task(_process_speech(session, user_id, pcm))


async def _end_conversation(guild_id: int) -> None:
    session = _active_sessions.pop(guild_id, None)
    if not session:
        return
    if session.monitor_task and not session.monitor_task.done():
        session.monitor_task.cancel()
    try:
        session.vc.stop_listening()
    except Exception:
        pass
    try:
        if session.vc.is_playing():
            session.vc.stop()
        if session.vc.is_connected():
            await session.vc.disconnect()
    except Exception:
        logger.exception("Error during conversation cleanup")


# ---------------------------------------------------------------------------
# Command registration
# ---------------------------------------------------------------------------
def setup_tts_commands(bot: commands.Bot, *, include_vcleave: bool = True) -> None:
    """Register /speak, /converse, /stopconversing (and optionally /vcleave)."""
    _VOICE_CHOICES = [
        app_commands.Choice(name="English — Aria (Female)", value="en-US-AriaNeural"),
        app_commands.Choice(name="English — Guy (Male)", value="en-US-GuyNeural"),
        app_commands.Choice(name="Urdu — Asad (Male)", value="ur-PK-AsadNeural"),
        app_commands.Choice(name="Urdu — Uzma (Female)", value="ur-PK-UzmaNeural"),
    ]

    # ------------------------------------------------------------------
    # /speak
    # ------------------------------------------------------------------
    @bot.tree.command(
        name="speak",
        description="Bot joins your VC and speaks aloud using Microsoft TTS",
    )
    @app_commands.describe(
        text="What to say (leave blank for an AI-generated line)",
        voice="Voice to use (default: English Aria)",
    )
    @app_commands.choices(voice=_VOICE_CHOICES)
    async def speak(
        interaction: discord.Interaction,
        text: Optional[str] = None,
        voice: str = DEFAULT_VOICE,
    ):
        try:
            await interaction.response.defer()
        except discord.NotFound:
            return

        if not text:
            text = await fetch_ai_dead_chat_starter()
            if not text:
                text = "Hey everyone, what's going on?"

        vc = await _ensure_voice_client(interaction)
        if not vc:
            return

        if vc.is_playing():
            vc.stop()

        try:
            audio_path = await _tts_to_file(text[:1000], voice)
        except RuntimeError as exc:
            await interaction.followup.send(f"❌ {exc}", ephemeral=True)
            return
        except Exception:
            logger.exception("TTS synthesis failed")
            await interaction.followup.send(
                "❌ TTS generation failed. Please try again.", ephemeral=True
            )
            return

        def _after(error: Optional[Exception]) -> None:
            try:
                os.unlink(audio_path)
            except OSError:
                pass
            if error:
                logger.error("TTS playback error", extra={"error": str(error)})

        try:
            source = discord.FFmpegPCMAudio(audio_path)
            vc.play(source, after=_after)
        except Exception as exc:
            logger.exception("VC playback failed")
            await interaction.followup.send(f"❌ Playback failed: {exc}", ephemeral=True)
            _after(None)
            return

        embed = discord.Embed(
            title="🔊 Speaking in VC",
            description=f'"{text[:500]}"',
            color=discord.Color.blue(),
        )
        embed.add_field(name="Voice", value=_VOICES.get(voice, voice), inline=True)
        embed.add_field(name="Channel", value=vc.channel.mention, inline=True)
        await interaction.followup.send(embed=embed)

    # ------------------------------------------------------------------
    # /converse
    # ------------------------------------------------------------------
    @bot.tree.command(
        name="converse",
        description="Bot joins your VC, listens, and has a real conversation with you",
    )
    @app_commands.describe(voice="Voice for TTS replies (default: English Aria)")
    @app_commands.choices(voice=_VOICE_CHOICES)
    async def converse(
        interaction: discord.Interaction,
        voice: str = DEFAULT_VOICE,
    ):
        try:
            await interaction.response.defer()
        except discord.NotFound:
            return

        if not _VOICE_RECV_AVAILABLE:
            await interaction.followup.send(
                "❌ `discord-ext-voice-recv` is not installed on this host. "
                "Add it to `requirements.txt` and redeploy.",
                ephemeral=True,
            )
            return

        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("❌ Join a voice channel first!", ephemeral=True)
            return

        guild_id = interaction.guild.id
        if guild_id in _active_sessions:
            await interaction.followup.send(
                "❌ Already in conversation mode. Use `/stopconversing` first.",
                ephemeral=True,
            )
            return

        if not _get_gemini_keys():
            await interaction.followup.send(
                "❌ No Gemini API keys configured. Set `GEMINI_API_KEY_1` in your environment.",
                ephemeral=True,
            )
            return

        channel = interaction.user.voice.channel
        existing: Optional[discord.VoiceClient] = interaction.guild.voice_client  # type: ignore
        if existing:
            if existing.is_playing():
                existing.stop()
            await existing.disconnect()

        try:
            vc = await channel.connect(cls=voice_recv.VoiceRecvClient)
        except Exception as exc:
            logger.exception("Failed to connect as VoiceRecvClient")
            await interaction.followup.send(f"❌ Could not join VC: {exc}", ephemeral=True)
            return

        sink = _ConversationSink()
        vc.listen(sink)

        session = _ConversationSession(
            vc=vc,
            sink=sink,
            text_channel=interaction.channel,
            guild=interaction.guild,
            voice=voice,
        )
        _active_sessions[guild_id] = session
        session.monitor_task = asyncio.create_task(_silence_monitor(guild_id))

        embed = discord.Embed(
            title="🎙️ Conversation Mode Active",
            description=(
                "I'm listening! Speak in VC and I'll transcribe and reply.\n\n"
                "Transcripts appear in this channel.\n"
                "Use `/stopconversing` to end the session."
            ),
            color=discord.Color.green(),
        )
        embed.add_field(name="Voice Channel", value=vc.channel.mention, inline=True)
        embed.add_field(name="TTS Voice", value=_VOICES.get(voice, voice), inline=True)
        await interaction.followup.send(embed=embed)

    # ------------------------------------------------------------------
    # /stopconversing
    # ------------------------------------------------------------------
    @bot.tree.command(name="stopconversing", description="End the voice conversation session")
    async def stopconversing(interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if guild_id not in _active_sessions:
            await interaction.response.send_message(
                "❌ No active conversation.", ephemeral=True
            )
            return
        try:
            await interaction.response.defer()
        except discord.NotFound:
            return
        await _end_conversation(guild_id)
        await interaction.followup.send("✅ Conversation ended.")

    # ------------------------------------------------------------------
    # /vcleave (optional)
    # ------------------------------------------------------------------
    if include_vcleave:
        @bot.tree.command(name="vcleave", description="Bot leaves the voice channel")
        async def vcleave(interaction: discord.Interaction):
            guild_id = interaction.guild.id
            if guild_id in _active_sessions:
                await _end_conversation(guild_id)
            vc: Optional[discord.VoiceClient] = interaction.guild.voice_client  # type: ignore
            if not vc:
                await interaction.response.send_message(
                    "❌ I'm not in a voice channel.", ephemeral=True
                )
                return
            if vc.is_playing():
                vc.stop()
            await vc.disconnect()
            await interaction.response.send_message("👋 Left the voice channel.", ephemeral=True)
