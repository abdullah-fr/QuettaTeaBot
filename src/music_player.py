import asyncio
import os
import shutil
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse

import discord
from discord import app_commands


MAX_QUEUE_SIZE = 50
SEARCH_LIMIT = 5
AUTOCOMPLETE_LIMIT = 10
FFMPEG_BEFORE_OPTIONS = (
    "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
)
FFMPEG_OPTIONS = "-vn"
YOUTUBE_AUTH_HINT = (
    "YouTube is asking for sign-in verification. Add "
    "`YTDLP_COOKIES_BROWSER=brave` to your `.env` for this computer, "
    "or set `YTDLP_COOKIES_FILE=/path/to/cookies.txt`, then restart the bot."
)


class MusicError(Exception):
    """User-facing error raised when music playback cannot continue."""


@dataclass
class Track:
    title: str
    webpage_url: str
    stream_url: Optional[str] = None
    duration: Optional[int] = None
    requested_by: str = "Unknown"
    requested_by_id: Optional[int] = None
    thumbnail: Optional[str] = None
    uploader: Optional[str] = None


@dataclass(frozen=True)
class SearchResult:
    title: str
    webpage_url: str
    duration: Optional[int] = None
    uploader: Optional[str] = None


@dataclass
class GuildMusicState:
    queue: list[Track] = field(default_factory=list)
    current: Optional[Track] = None
    text_channel: Optional[discord.abc.Messageable] = None
    volume: float = 0.5
    player_view: Optional["MusicPlayerView"] = None

    def enqueue(self, track: Track) -> int:
        if len(self.queue) >= MAX_QUEUE_SIZE:
            raise MusicError("The music queue is full. Try again after a few songs play.")

        self.queue.append(track)
        return len(self.queue)

    def clear(self) -> None:
        self.queue.clear()
        self.current = None


def format_duration(seconds: Optional[int]) -> str:
    if seconds is None:
        return "Unknown"

    seconds = int(seconds)
    if seconds <= 0:
        return "Live"

    hours, remainder = divmod(seconds, 3600)
    minutes, remaining_seconds = divmod(remainder, 60)

    if hours:
        return f"{hours}:{minutes:02d}:{remaining_seconds:02d}"

    return f"{minutes}:{remaining_seconds:02d}"


def is_probably_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def truncate_text(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value

    return value[: limit - 3].rstrip() + "..."


def _parse_browser_cookie_spec(spec: str) -> tuple[str, Optional[str], Optional[str], Optional[str]]:
    browser_spec, _, container = spec.strip().partition("::")
    browser_keyring, _, profile = browser_spec.partition(":")
    browser, _, keyring = browser_keyring.partition("+")

    browser = browser.strip().lower()
    profile = profile.strip() or None
    keyring = keyring.strip().upper() or None
    container = container.strip() or None

    if not browser:
        raise MusicError("YTDLP_COOKIES_BROWSER is set but does not include a browser name.")

    return browser, profile, keyring, container


def _cookie_options_from_env() -> dict:
    options = {}

    cookie_file = os.getenv("YTDLP_COOKIES_FILE") or os.getenv("YOUTUBE_COOKIES_FILE")
    if cookie_file:
        options["cookiefile"] = os.path.expanduser(cookie_file)

    browser_spec = os.getenv("YTDLP_COOKIES_BROWSER") or os.getenv(
        "YOUTUBE_COOKIES_BROWSER"
    )
    if browser_spec:
        options["cookiesfrombrowser"] = _parse_browser_cookie_spec(browser_spec)

    return options


def _js_runtime_options_from_env() -> dict:
    runtime_spec = os.getenv("YTDLP_JS_RUNTIME") or os.getenv("YOUTUBE_JS_RUNTIME")
    runtimes = runtime_spec or "node"
    enabled_runtimes = {
        runtime.strip().lower(): {}
        for runtime in runtimes.split(",")
        if runtime.strip()
    }

    return {"js_runtimes": enabled_runtimes} if enabled_runtimes else {}


def _music_error_from_exception(exc: Exception, action: str) -> MusicError:
    message = str(exc)
    if "Sign in to confirm" in message or "--cookies-from-browser" in message:
        return MusicError(YOUTUBE_AUTH_HINT)

    if "Signature solving failed" in message or "Requested format is not available" in message:
        return MusicError(
            f"Could not {action}. YouTube needs a JavaScript runtime for this video. "
            "Install Node.js or set `YTDLP_JS_RUNTIME=node`, then restart the bot."
        )

    return MusicError(f"Could not {action}: {message}")


def _load_ytdlp():
    try:
        import yt_dlp
    except ModuleNotFoundError as exc:
        raise MusicError(
            "yt-dlp is not installed. Run `pip install -r requirements.txt` and restart the bot."
        ) from exc

    return yt_dlp


def _normalize_webpage_url(info: dict) -> Optional[str]:
    webpage_url = info.get("webpage_url") or info.get("original_url")
    if webpage_url:
        return webpage_url

    raw_url = info.get("url")
    if raw_url and is_probably_url(raw_url):
        return raw_url

    video_id = info.get("id") or raw_url
    if video_id:
        return f"https://www.youtube.com/watch?v={video_id}"

    return None


def _first_entry(info: dict) -> dict:
    entries = info.get("entries")
    if not entries:
        return info

    for entry in entries:
        if entry:
            return entry

    raise MusicError("No playable YouTube result was found.")


def _base_ytdlp_options() -> dict:
    options = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "source_address": "0.0.0.0",
        "skip_download": True,
    }
    options.update(_cookie_options_from_env())
    options.update(_js_runtime_options_from_env())

    return options


def _track_from_info(info: dict, requested_by: str, requested_by_id: Optional[int]) -> Track:
    webpage_url = _normalize_webpage_url(info)
    stream_url = info.get("url")

    if not webpage_url:
        raise MusicError("Could not find a YouTube page URL for that song.")

    if not stream_url:
        raise MusicError("Could not find a playable audio stream for that song.")

    return Track(
        title=info.get("title") or "Unknown title",
        webpage_url=webpage_url,
        stream_url=stream_url,
        duration=info.get("duration"),
        requested_by=requested_by,
        requested_by_id=requested_by_id,
        thumbnail=info.get("thumbnail"),
        uploader=info.get("uploader") or info.get("channel"),
    )


def _search_result_from_info(info: dict) -> Optional[SearchResult]:
    webpage_url = _normalize_webpage_url(info)
    if not webpage_url:
        return None

    return SearchResult(
        title=info.get("title") or "Unknown title",
        webpage_url=webpage_url,
        duration=info.get("duration"),
        uploader=info.get("uploader") or info.get("channel"),
    )


def _resolve_track_sync(
    query: str, requested_by: str, requested_by_id: Optional[int] = None
) -> Track:
    if not query.strip():
        raise MusicError("Please provide a song name or YouTube link.")

    yt_dlp = _load_ytdlp()
    target = query.strip() if is_probably_url(query) else f"ytsearch1:{query.strip()}"

    try:
        with yt_dlp.YoutubeDL(_base_ytdlp_options()) as ydl:
            info = ydl.extract_info(target, download=False)
    except MusicError:
        raise
    except Exception as exc:
        raise _music_error_from_exception(exc, "load that song") from exc

    if not info:
        raise MusicError("No playable YouTube result was found.")

    return _track_from_info(_first_entry(info), requested_by, requested_by_id)


async def resolve_track(
    query: str, requested_by: str, requested_by_id: Optional[int] = None
) -> Track:
    return await asyncio.to_thread(
        _resolve_track_sync, query, requested_by, requested_by_id
    )


def _search_youtube_sync(query: str, limit: int = SEARCH_LIMIT) -> list[SearchResult]:
    if not query.strip():
        raise MusicError("Please provide a song name to search.")

    yt_dlp = _load_ytdlp()
    options = _base_ytdlp_options()
    options["extract_flat"] = True

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(f"ytsearch{limit}:{query.strip()}", download=False)
    except Exception as exc:
        raise _music_error_from_exception(exc, "search YouTube") from exc

    if not info:
        return []

    entries = info.get("entries") or []
    results = []
    for entry in entries:
        result = _search_result_from_info(entry)
        if result:
            results.append(result)

    return results


async def search_youtube(query: str, limit: int = SEARCH_LIMIT) -> list[SearchResult]:
    return await asyncio.to_thread(_search_youtube_sync, query, limit)


async def autocomplete_song_names(
    interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
    query = current.strip()
    if len(query) < 2 or is_probably_url(query):
        return []

    try:
        results = await asyncio.wait_for(
            search_youtube(query, AUTOCOMPLETE_LIMIT),
            timeout=2.5,
        )
    except Exception:
        return []

    choices = []
    seen_titles = set()
    for result in results:
        title = truncate_text(result.title, 100)
        title_key = title.casefold()
        if not title or title_key in seen_titles:
            continue

        choices.append(app_commands.Choice(name=title, value=title))
        seen_titles.add(title_key)

    return choices[:AUTOCOMPLETE_LIMIT]


class MusicPlayerView(discord.ui.View):
    """Persistent player controls attached to the Now Playing message."""

    def __init__(self, controller: "MusicController", guild: discord.Guild):
        super().__init__(timeout=None)
        self.controller = controller
        self.guild = guild
        self.message: Optional[discord.Message] = None

    def _vc(self) -> Optional[discord.VoiceClient]:
        return self.guild.voice_client  # type: ignore

    def _is_paused(self) -> bool:
        vc = self._vc()
        return vc is not None and vc.is_paused()

    def _is_playing(self) -> bool:
        vc = self._vc()
        return vc is not None and vc.is_playing()

    async def _update_buttons(self) -> None:
        """Update button labels to reflect current playback state."""
        pause_btn = discord.utils.get(self.children, custom_id="music_pause")
        if pause_btn:
            pause_btn.label = "▶️ Resume" if self._is_paused() else "⏸ Pause"
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass

    async def disable_all(self) -> None:
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass

    @discord.ui.button(label="⏸ Pause", style=discord.ButtonStyle.primary, custom_id="music_pause")
    async def pause_resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self._vc()
        if not vc:
            await interaction.response.send_message("Not connected to voice.", ephemeral=True)
            return
        if vc.is_paused():
            vc.resume()
            button.label = "⏸ Pause"
        elif vc.is_playing():
            vc.pause()
            button.label = "▶️ Resume"
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="⏭ Skip", style=discord.ButtonStyle.secondary, custom_id="music_skip")
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self._vc()
        if not vc or (not vc.is_playing() and not vc.is_paused()):
            await interaction.response.send_message("Nothing is playing.", ephemeral=True)
            return
        vc.stop()
        await interaction.response.send_message("⏭ Skipped.", ephemeral=True)

    @discord.ui.button(label="⏹ Stop", style=discord.ButtonStyle.danger, custom_id="music_stop")
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.guild is None:
            await interaction.response.send_message("Server only.", ephemeral=True)
            return
        state = self.controller.get_state(interaction.guild.id)
        state.clear()
        vc = self._vc()
        if vc and (vc.is_playing() or vc.is_paused()):
            vc.stop()
        await self.disable_all()
        await interaction.response.send_message("⏹ Stopped and queue cleared.", ephemeral=True)


class MusicSearchSelect(discord.ui.Select):
    def __init__(
        self,
        controller: "MusicController",
        results: list[SearchResult],
        requester_id: int,
    ):
        self.controller = controller
        self.results = results
        self.requester_id = requester_id

        options = []
        for index, result in enumerate(results):
            details = format_duration(result.duration)
            if result.uploader:
                details = f"{details} - {truncate_text(result.uploader, 70)}"

            options.append(
                discord.SelectOption(
                    label=truncate_text(result.title, 100),
                    description=truncate_text(details, 100),
                    value=str(index),
                )
            )

        super().__init__(
            placeholder="Choose a song to play",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.requester_id:
            await interaction.response.send_message(
                "Only the person who searched can choose from this menu.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(thinking=True, ephemeral=True)
        result = self.results[int(self.values[0])]
        await self.controller.play_query_from_interaction(
            interaction, result.webpage_url, ephemeral=True
        )

        if self.view:
            for item in self.view.children:
                item.disabled = True

            try:
                await interaction.message.edit(view=self.view)
            except discord.HTTPException:
                pass

            self.view.stop()


class MusicSearchView(discord.ui.View):
    def __init__(
        self,
        controller: "MusicController",
        results: list[SearchResult],
        requester_id: int,
    ):
        super().__init__(timeout=60)
        self.message: Optional[discord.Message] = None
        self.add_item(MusicSearchSelect(controller, results, requester_id))

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass


class MusicController:
    def __init__(self, bot):
        self.bot = bot
        self.states: dict[int, GuildMusicState] = {}

    def get_state(self, guild_id: int) -> GuildMusicState:
        if guild_id not in self.states:
            self.states[guild_id] = GuildMusicState()

        return self.states[guild_id]

    def _requester_name(self, interaction: discord.Interaction) -> str:
        return getattr(interaction.user, "display_name", interaction.user.name)

    def _user_voice_channel(self, interaction: discord.Interaction):
        voice_state = getattr(interaction.user, "voice", None)
        return getattr(voice_state, "channel", None)

    async def _send_voice_error(
        self, interaction: discord.Interaction, *, ephemeral: bool = False
    ) -> bool:
        if interaction.guild is None:
            await interaction.followup.send(
                "Music commands only work inside a server.", ephemeral=ephemeral
            )
            return True

        if not self._user_voice_channel(interaction):
            await interaction.followup.send(
                "Join a voice channel first, then try the music command again.",
                ephemeral=ephemeral,
            )
            return True

        return False

    async def ensure_voice_client(
        self,
        interaction: discord.Interaction,
        *,
        ephemeral: bool = False,
        require_ffmpeg: bool = True,
    ) -> Optional[discord.VoiceClient]:
        if await self._send_voice_error(interaction, ephemeral=ephemeral):
            return None

        if require_ffmpeg and shutil.which("ffmpeg") is None:
            await interaction.followup.send(
                "FFmpeg is not installed on this machine, so I cannot stream audio yet.",
                ephemeral=ephemeral,
            )
            return None

        voice_channel = self._user_voice_channel(interaction)
        voice_client = interaction.guild.voice_client

        try:
            if voice_client is None:
                return await voice_channel.connect()

            if voice_client.channel != voice_channel:
                await voice_client.move_to(voice_channel)

            return voice_client
        except discord.Forbidden:
            await interaction.followup.send(
                "I need permission to connect and speak in that voice channel.",
                ephemeral=ephemeral,
            )
        except RuntimeError as exc:
            await interaction.followup.send(
                f"Voice support is not ready: {exc}",
                ephemeral=ephemeral,
            )
        except discord.ClientException as exc:
            await interaction.followup.send(
                f"Could not join the voice channel: {exc}",
                ephemeral=ephemeral,
            )

        return None

    async def connect_from_interaction(
        self, interaction: discord.Interaction, *, ephemeral: bool = False
    ) -> None:
        voice_client = await self.ensure_voice_client(
            interaction, ephemeral=ephemeral, require_ffmpeg=False
        )
        if not voice_client:
            return

        await interaction.followup.send(
            f"Connected to **{voice_client.channel.name}**.", ephemeral=ephemeral
        )

    async def disconnect_from_interaction(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "Music commands only work inside a server.", ephemeral=True
            )
            return

        state = self.get_state(interaction.guild.id)
        state.clear()
        voice_client = interaction.guild.voice_client
        if not voice_client:
            await interaction.response.send_message("I am not connected to voice.")
            return

        await voice_client.disconnect()
        await interaction.response.send_message("Disconnected from voice.")

    async def play_query_from_interaction(
        self,
        interaction: discord.Interaction,
        query: str,
        *,
        ephemeral: bool = False,
    ) -> None:
        if await self._send_voice_error(interaction, ephemeral=ephemeral):
            return

        assert interaction.guild is not None
        state = self.get_state(interaction.guild.id)
        if len(state.queue) >= MAX_QUEUE_SIZE:
            await interaction.edit_original_response(
                content="The music queue is full. Try again after a few songs play."
            )
            return

        # Run voice connect and track resolution concurrently for faster response
        voice_task = asyncio.create_task(
            self.ensure_voice_client(interaction, ephemeral=ephemeral, require_ffmpeg=True)
        )
        track_task = asyncio.create_task(
            resolve_track(
                query,
                requested_by=self._requester_name(interaction),
                requested_by_id=interaction.user.id,
            )
        )

        try:
            voice_client, track = await asyncio.gather(voice_task, track_task)
        except MusicError as exc:
            voice_task.cancel()
            track_task.cancel()
            await interaction.edit_original_response(content=str(exc))
            return

        if not voice_client:
            track_task.cancel()
            return

        state.text_channel = interaction.channel
        position = state.enqueue(track)

        await interaction.edit_original_response(
            content=None,
            embed=self.build_added_embed(track, position),
        )
        await self.start_if_idle(interaction.guild)

    async def start_if_idle(self, guild: discord.Guild) -> None:
        voice_client = guild.voice_client
        if voice_client and not voice_client.is_playing() and not voice_client.is_paused():
            await self.start_next(guild)

    async def start_next(self, guild: discord.Guild) -> None:
        state = self.get_state(guild.id)
        voice_client = guild.voice_client

        if not voice_client or not voice_client.is_connected():
            state.current = None
            return

        if not state.queue:
            state.current = None
            return

        track = state.queue.pop(0)
        state.current = track

        try:
            if not track.stream_url:
                track = await resolve_track(
                    track.webpage_url,
                    requested_by=track.requested_by,
                    requested_by_id=track.requested_by_id,
                )
                state.current = track

            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(
                    track.stream_url,
                    before_options=FFMPEG_BEFORE_OPTIONS,
                    options=FFMPEG_OPTIONS,
                ),
                volume=state.volume,
            )
        except Exception as exc:
            if state.text_channel:
                await state.text_channel.send(f"Could not play `{track.title}`: {exc}")
            await self.start_next(guild)
            return

        def after_play(error):
            self.bot.loop.call_soon_threadsafe(
                asyncio.create_task, self.after_track(guild, error)
            )

        voice_client.play(source, after=after_play)

        if state.text_channel:
            # Disable previous player view if any
            if state.player_view:
                await state.player_view.disable_all()

            view = MusicPlayerView(self, guild)
            msg = await state.text_channel.send(
                embed=self.build_now_playing_embed(track), view=view
            )
            view.message = msg
            state.player_view = view

    async def after_track(self, guild: discord.Guild, error: Optional[Exception]) -> None:
        state = self.get_state(guild.id)
        if error and state.text_channel:
            await state.text_channel.send(f"Playback error: {error}")

        await self.start_next(guild)

    def build_added_embed(self, track: Track, position: int) -> discord.Embed:
        embed = discord.Embed(
            title="Added to Queue",
            description=f"[{track.title}]({track.webpage_url})",
            color=discord.Color.green(),
        )
        embed.add_field(name="Position", value=str(position), inline=True)
        embed.add_field(name="Duration", value=format_duration(track.duration), inline=True)
        if track.uploader:
            embed.add_field(name="Channel", value=track.uploader, inline=True)
        if track.thumbnail:
            embed.set_thumbnail(url=track.thumbnail)

        return embed

    def build_now_playing_embed(self, track: Track) -> discord.Embed:
        embed = discord.Embed(
            title="Now Playing",
            description=f"[{track.title}]({track.webpage_url})",
            color=discord.Color.blurple(),
        )
        embed.add_field(name="Duration", value=format_duration(track.duration), inline=True)
        embed.add_field(name="Requested by", value=track.requested_by, inline=True)
        if track.thumbnail:
            embed.set_thumbnail(url=track.thumbnail)

        return embed

    def build_queue_embed(self, guild: discord.Guild) -> discord.Embed:
        state = self.get_state(guild.id)
        embed = discord.Embed(title="Music Queue", color=discord.Color.blue())

        if state.current:
            embed.add_field(
                name="Now Playing",
                value=f"[{state.current.title}]({state.current.webpage_url})",
                inline=False,
            )
        else:
            embed.add_field(name="Now Playing", value="Nothing right now.", inline=False)

        if not state.queue:
            embed.add_field(name="Up Next", value="Queue is empty.", inline=False)
            return embed

        lines = []
        for index, track in enumerate(state.queue[:10], start=1):
            title = truncate_text(track.title, 60)
            lines.append(
                f"`{index}.` [{title}]({track.webpage_url}) - {format_duration(track.duration)}"
            )

        if len(state.queue) > 10:
            lines.append(f"...and {len(state.queue) - 10} more")

        embed.add_field(name="Up Next", value="\n".join(lines), inline=False)
        return embed


def setup_music_commands(bot) -> MusicController:
    controller = MusicController(bot)

    @bot.tree.command(name="play", description="Play a song from YouTube search or link")
    @app_commands.describe(song="Song name or YouTube URL")
    @app_commands.autocomplete(song=autocomplete_song_names)
    async def play(interaction: discord.Interaction, song: str):
        await interaction.response.send_message(
            f"🔍 Searching for **{truncate_text(song, 60)}**...", ephemeral=False
        )
        await controller.play_query_from_interaction(interaction, song)

    @bot.tree.command(name="search", description="Search YouTube songs and choose one")
    @app_commands.describe(song="Song title or artist to search")
    @app_commands.autocomplete(song=autocomplete_song_names)
    async def search(interaction: discord.Interaction, song: str):
        await interaction.response.defer(thinking=True, ephemeral=True)

        if await controller._send_voice_error(interaction, ephemeral=True):
            return

        try:
            results = await search_youtube(song, SEARCH_LIMIT)
        except MusicError as exc:
            await interaction.followup.send(str(exc), ephemeral=True)
            return

        if not results:
            await interaction.followup.send(
                "No YouTube results found for that search.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title="Song Search",
            description="Pick a result from the menu below.",
            color=discord.Color.blue(),
        )

        for index, result in enumerate(results, start=1):
            details = format_duration(result.duration)
            if result.uploader:
                details = f"{details} - {result.uploader}"

            embed.add_field(
                name=f"{index}. {truncate_text(result.title, 80)}",
                value=truncate_text(details, 100),
                inline=False,
            )

        view = MusicSearchView(controller, results, interaction.user.id)
        message = await interaction.followup.send(
            embed=embed, view=view, ephemeral=True, wait=True
        )
        view.message = message

    @bot.tree.command(name="connect", description="Connect the bot to your voice channel")
    async def connect(interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        await controller.connect_from_interaction(interaction)

    @bot.tree.command(name="queue", description="Show the current music queue")
    async def queue(interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "Music commands only work inside a server.", ephemeral=True
            )
            return

        await interaction.response.send_message(
            embed=controller.build_queue_embed(interaction.guild)
        )

    @bot.tree.command(name="skip", description="Skip the current song")
    async def skip(interaction: discord.Interaction):
        if interaction.guild is None or interaction.guild.voice_client is None:
            await interaction.response.send_message("Nothing is playing right now.")
            return

        voice_client = interaction.guild.voice_client
        if not voice_client.is_playing() and not voice_client.is_paused():
            await interaction.response.send_message("Nothing is playing right now.")
            return

        voice_client.stop()
        await interaction.response.send_message("Skipped the current song.")

    @bot.tree.command(name="pause", description="Pause the current song")
    async def pause(interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client if interaction.guild else None
        if not voice_client or not voice_client.is_playing():
            await interaction.response.send_message("Nothing is playing right now.")
            return

        voice_client.pause()
        await interaction.response.send_message("Paused the music.")

    @bot.tree.command(name="resume", description="Resume paused music")
    async def resume(interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client if interaction.guild else None
        if not voice_client or not voice_client.is_paused():
            await interaction.response.send_message("Nothing is paused right now.")
            return

        voice_client.resume()
        await interaction.response.send_message("Resumed the music.")

    @bot.tree.command(name="stop", description="Stop music and clear the queue")
    async def stop(interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "Music commands only work inside a server.", ephemeral=True
            )
            return

        state = controller.get_state(interaction.guild.id)
        state.clear()
        voice_client = interaction.guild.voice_client
        if voice_client and (voice_client.is_playing() or voice_client.is_paused()):
            voice_client.stop()

        await interaction.response.send_message("Stopped the music and cleared the queue.")

    @bot.tree.command(name="disconnect", description="Disconnect the bot from voice")
    async def disconnect(interaction: discord.Interaction):
        await controller.disconnect_from_interaction(interaction)

    @bot.tree.command(name="leave", description="Disconnect the bot from voice")
    async def leave(interaction: discord.Interaction):
        await controller.disconnect_from_interaction(interaction)

    bot.music_controller = controller
    return controller
