import discord
from discord.ext import commands, tasks
import aiohttp
import asyncio
from datetime import datetime, timedelta
import pytz
import random

# Pakistan timezone
PKT = pytz.timezone('Asia/Karachi')

# Ramadan configuration
RAMADAN_CONFIG = {
    "city": "Islamabad",
    "country": "Pakistan",
    "general_channel": "general",
    "ramadan_channel": "ramadan-special",
    "hadith_time": {"hour": 20, "minute": 0},  # 8:00 PM PKT
    "ayat_time": {"hour": 9, "minute": 0},     # 9:00 AM PKT
    "sehri_reminder_minutes": 15,  # Remind 15 minutes before Sehri ends
}

# Cities in Pakistan for prayer times
PAKISTAN_CITIES = {
    "islamabad": "Islamabad",
    "lahore": "Lahore",
    "karachi": "Karachi",
    "faisalabad": "Faisalabad",
    "rawalpindi": "Rawalpindi",
    "multan": "Multan",
    "peshawar": "Peshawar",
    "quetta": "Quetta",
}

class RamadanBot:
    def __init__(self, bot):
        self.bot = bot
        self.current_city = RAMADAN_CONFIG["city"]
        self.prayer_times_cache = {}
        self.last_sehri_reminder = None
        self.last_iftar_reminder = None

    async def fetch_prayer_times(self, city=None):
        """Fetch prayer times from Aladhan API"""
        if city is None:
            city = self.current_city

        today = datetime.now(PKT).strftime("%d-%m-%Y")

        # Check cache
        cache_key = f"{city}_{today}"
        if cache_key in self.prayer_times_cache:
            return self.prayer_times_cache[cache_key]

        try:
            url = f"http://api.aladhan.com/v1/timingsByCity/{today}"
            params = {
                "city": city,
                "country": "Pakistan",
                "method": 1  # University of Islamic Sciences, Karachi
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        timings = data['data']['timings']

                        # Cache the result
                        self.prayer_times_cache[cache_key] = timings
                        return timings
        except Exception as e:
            print(f"Error fetching prayer times: {e}")

        return None

    async def fetch_random_hadith(self):
        """Fetch random Ramadan-related hadith from Sunnah.com API"""
        try:
            # Sunnah.com API - Random hadith from Sahih Bukhari Book on Fasting
            book_number = 30  # Book of Fasting in Sahih Bukhari
            hadith_number = random.randint(1, 81)  # Approx 81 hadiths in fasting book

            url = f"https://api.sunnah.com/v1/hadiths/bukhari/{book_number}/{hadith_number}"
            headers = {"X-API-Key": "$2y$10$lkHuLM5qLvJGKGYdFdZJeOxnKLjqGPKdJLqJqLjqGPKdJLqJqLjqGP"}

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        hadith = data.get('hadith', [{}])[0]

                        return {
                            "arabic": hadith.get('body', 'N/A'),
                            "english": hadith.get('englishText', 'N/A'),
                            "reference": f"Sahih Bukhari {hadith.get('hadithNumber', 'N/A')}"
                        }
        except Exception as e:
            print(f"Error fetching hadith: {e}")

        # Fallback hadiths if API fails
        fallback_hadiths = [
            {
                "arabic": "مَنْ صَامَ رَمَضَانَ إِيمَانًا وَاحْتِسَابًا غُفِرَ لَهُ مَا تَقَدَّمَ مِنْ ذَنْبِهِ",
                "english": "Whoever fasts Ramadan out of faith and seeking reward, his previous sins will be forgiven.",
                "reference": "Sahih Bukhari 38"
            },
            {
                "arabic": "إِذَا دَخَلَ رَمَضَانُ فُتِّحَتْ أَبْوَابُ الْجَنَّةِ وَغُلِّقَتْ أَبْوَابُ جَهَنَّمَ وَسُلْسِلَتِ الشَّيَاطِينُ",
                "english": "When Ramadan enters, the gates of Paradise are opened, the gates of Hellfire are closed, and the devils are chained.",
                "reference": "Sahih Bukhari 1899"
            },
            {
                "arabic": "مَنْ قَامَ لَيْلَةَ الْقَدْرِ إِيمَانًا وَاحْتِسَابًا غُفِرَ لَهُ مَا تَقَدَّمَ مِنْ ذَنْبِهِ",
                "english": "Whoever stands (in prayer) on Laylatul Qadr out of faith and seeking reward, his previous sins will be forgiven.",
                "reference": "Sahih Bukhari 1901"
            }
        ]

        return random.choice(fallback_hadiths)

    async def fetch_random_ayat(self):
        """Fetch random Ramadan-related Quranic verse from AlQuran.cloud API"""
        try:
            # Ramadan-related Surahs and verses
            ramadan_verses = [
                {"surah": 2, "ayah": 183},  # O you who believe, fasting is prescribed
                {"surah": 2, "ayah": 184},  # Days numbered, whoever is ill or on journey
                {"surah": 2, "ayah": 185},  # Month of Ramadan in which Quran was revealed
                {"surah": 2, "ayah": 186},  # When My servants ask about Me
                {"surah": 2, "ayah": 187},  # Permitted to you on night of fasts
                {"surah": 97, "ayah": 1},   # Laylatul Qadr - We sent it down
                {"surah": 97, "ayah": 2},   # What will explain Laylatul Qadr
                {"surah": 97, "ayah": 3},   # Better than thousand months
                {"surah": 3, "ayah": 133},  # Race toward forgiveness
                {"surah": 39, "ayah": 53},  # Do not despair of Allah's mercy
            ]

            verse = random.choice(ramadan_verses)

            # Fetch Arabic
            url_arabic = f"http://api.alquran.cloud/v1/ayah/{verse['surah']}:{verse['ayah']}"
            # Fetch English
            url_english = f"http://api.alquran.cloud/v1/ayah/{verse['surah']}:{verse['ayah']}/en.sahih"

            async with aiohttp.ClientSession() as session:
                async with session.get(url_arabic) as resp_ar:
                    async with session.get(url_english) as resp_en:
                        if resp_ar.status == 200 and resp_en.status == 200:
                            data_ar = await resp_ar.json()
                            data_en = await resp_en.json()

                            return {
                                "arabic": data_ar['data']['text'],
                                "english": data_en['data']['text'],
                                "surah": data_ar['data']['surah']['englishName'],
                                "ayah": data_ar['data']['numberInSurah']
                            }
        except Exception as e:
            print(f"Error fetching ayat: {e}")

        # Fallback verses
        fallback_verses = [
            {
                "arabic": "يَا أَيُّهَا الَّذِينَ آمَنُوا كُتِبَ عَلَيْكُمُ الصِّيَامُ كَمَا كُتِبَ عَلَى الَّذِينَ مِن قَبْلِكُمْ لَعَلَّكُمْ تَتَّقُونَ",
                "english": "O you who have believed, decreed upon you is fasting as it was decreed upon those before you that you may become righteous.",
                "surah": "Al-Baqarah",
                "ayah": 183
            },
            {
                "arabic": "شَهْرُ رَمَضَانَ الَّذِي أُنزِلَ فِيهِ الْقُرْآنُ هُدًى لِّلنَّاسِ وَبَيِّنَاتٍ مِّنَ الْهُدَىٰ وَالْفُرْقَانِ",
                "english": "The month of Ramadan in which was revealed the Quran, a guidance for the people and clear proofs of guidance and criterion.",
                "surah": "Al-Baqarah",
                "ayah": 185
            }
        ]

        return random.choice(fallback_verses)

    async def get_iftar_countdown(self):
        """Get countdown to Iftar time"""
        timings = await self.fetch_prayer_times()
        if not timings:
            return None

        now = datetime.now(PKT)
        maghrib_time = timings['Maghrib']

        # Parse Maghrib time
        maghrib_hour, maghrib_minute = map(int, maghrib_time.split(':'))
        maghrib_dt = now.replace(hour=maghrib_hour, minute=maghrib_minute, second=0, microsecond=0)

        if now > maghrib_dt:
            # Iftar time has passed, show tomorrow's time
            maghrib_dt += timedelta(days=1)

        time_remaining = maghrib_dt - now
        hours = int(time_remaining.total_seconds() // 3600)
        minutes = int((time_remaining.total_seconds() % 3600) // 60)
        seconds = int(time_remaining.total_seconds() % 60)

        # Convert to 12-hour format
        maghrib_12hr = self.convert_to_12hr(maghrib_time)

        return {
            "iftar_time": maghrib_12hr,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "total_seconds": int(time_remaining.total_seconds())
        }

    async def get_sehri_countdown(self):
        """Get countdown to Sehri closing time (Fajr)"""
        timings = await self.fetch_prayer_times()
        if not timings:
            return None

        now = datetime.now(PKT)
        fajr_time = timings['Fajr']

        # Parse Fajr time
        fajr_hour, fajr_minute = map(int, fajr_time.split(':'))
        fajr_dt = now.replace(hour=fajr_hour, minute=fajr_minute, second=0, microsecond=0)

        if now > fajr_dt:
            # Fajr time has passed, show tomorrow's time
            fajr_dt += timedelta(days=1)

        time_remaining = fajr_dt - now
        hours = int(time_remaining.total_seconds() // 3600)
        minutes = int((time_remaining.total_seconds() % 3600) // 60)
        seconds = int(time_remaining.total_seconds() % 60)

        # Convert to 12-hour format
        fajr_12hr = self.convert_to_12hr(fajr_time)

        return {
            "sehri_time": fajr_12hr,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "total_seconds": int(time_remaining.total_seconds())
        }

    def convert_to_12hr(self, time_24hr):
        """Convert 24-hour time to 12-hour format"""
        hour, minute = map(int, time_24hr.split(':'))
        period = "AM" if hour < 12 else "PM"
        hour_12 = hour if hour <= 12 else hour - 12
        if hour_12 == 0:
            hour_12 = 12
        return f"{hour_12}:{minute:02d} {period}"

# Setup commands
def setup_ramadan_commands(bot, ramadan_bot):

    @bot.command(name='ramadan-times')
    async def ramadan_times(ctx):
        """Show today's Sehri and Iftar timings"""
        timings = await ramadan_bot.fetch_prayer_times()

        if not timings:
            await ctx.send("❌ Could not fetch prayer times. Please try again later.")
            return

        fajr = timings['Fajr']
        maghrib = timings['Maghrib']

        # Convert to 12-hour format
        fajr_12hr = ramadan_bot.convert_to_12hr(fajr)
        maghrib_12hr = ramadan_bot.convert_to_12hr(maghrib)

        embed = discord.Embed(
            title=f"🌙 Ramadan Timings - {ramadan_bot.current_city}",
            description=f"Prayer times for {datetime.now(PKT).strftime('%B %d, %Y')}",
            color=discord.Color.green()
        )

        embed.add_field(
            name="🌅 Sehri Ends (Fajr)",
            value=f"**{fajr_12hr}** PKT",
            inline=True
        )

        embed.add_field(
            name="🌆 Iftar Time (Maghrib)",
            value=f"**{maghrib_12hr}** PKT",
            inline=True
        )

        # Add countdown to Iftar
        countdown = await ramadan_bot.get_iftar_countdown()
        if countdown and countdown['total_seconds'] > 0:
            embed.add_field(
                name="⏰ Time Until Iftar",
                value=f"{countdown['hours']}h {countdown['minutes']}m {countdown['seconds']}s",
                inline=False
            )

        embed.set_footer(text=f"City: {ramadan_bot.current_city} | Use !ramadan-city to change")

        await ctx.send(embed=embed)

    @bot.command(name='ramadan-city')
    async def ramadan_city(ctx, *, city: str = None):
        """Change city for Ramadan timings"""
        if not city:
            cities_list = ", ".join(PAKISTAN_CITIES.values())
            await ctx.send(f"📍 Available cities: {cities_list}\n\nUsage: `!ramadan-city Lahore`")
            return

        city_lower = city.lower()
        if city_lower in PAKISTAN_CITIES:
            ramadan_bot.current_city = PAKISTAN_CITIES[city_lower]
            ramadan_bot.prayer_times_cache = {}  # Clear cache
            await ctx.send(f"✅ City changed to **{ramadan_bot.current_city}**")
        else:
            await ctx.send(f"❌ City not found. Available cities: {', '.join(PAKISTAN_CITIES.values())}")

    @bot.command(name='hadith')
    async def hadith_command(ctx):
        """Get a random Ramadan hadith"""
        hadith = await ramadan_bot.fetch_random_hadith()

        embed = discord.Embed(
            title="📿 Hadith about Ramadan",
            color=discord.Color.gold()
        )

        embed.add_field(
            name="Arabic",
            value=hadith['arabic'],
            inline=False
        )

        embed.add_field(
            name="English Translation",
            value=hadith['english'],
            inline=False
        )

        embed.set_footer(text=f"Reference: {hadith['reference']}")

        await ctx.send(embed=embed)

    @bot.command(name='ayat')
    async def ayat_command(ctx):
        """Get a random Ramadan-related Quranic verse"""
        ayat = await ramadan_bot.fetch_random_ayat()

        embed = discord.Embed(
            title="📖 Quranic Verse",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Arabic",
            value=ayat['arabic'],
            inline=False
        )

        embed.add_field(
            name="English Translation",
            value=ayat['english'],
            inline=False
        )

        embed.set_footer(text=f"Surah {ayat['surah']}, Ayah {ayat['ayah']}")

        await ctx.send(embed=embed)

    @bot.command(name='iftar-countdown')
    async def iftar_countdown_command(ctx):
        """Show countdown to Iftar time"""
        countdown = await ramadan_bot.get_iftar_countdown()

        if not countdown:
            await ctx.send("❌ Could not fetch Iftar time. Please try again later.")
            return

        if countdown['total_seconds'] <= 0:
            await ctx.send("🌆 It's Iftar time! Break your fast. Alhamdulillah!")
            return

        embed = discord.Embed(
            title="⏰ Iftar Countdown",
            description=f"Time remaining until Iftar in {ramadan_bot.current_city}",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="🕐 Countdown",
            value=f"**{countdown['hours']}** hours, **{countdown['minutes']}** minutes, **{countdown['seconds']}** seconds",
            inline=False
        )

        embed.add_field(
            name="🌆 Iftar Time",
            value=f"**{countdown['iftar_time']}** PKT",
            inline=False
        )

        await ctx.send(embed=embed)

    @bot.command(name='sehri-countdown')
    async def sehri_countdown_command(ctx):
        """Show countdown to Sehri closing time (Fajr)"""
        countdown = await ramadan_bot.get_sehri_countdown()

        if not countdown:
            await ctx.send("❌ Could not fetch Sehri time. Please try again later.")
            return

        if countdown['total_seconds'] <= 0:
            await ctx.send("🌅 Sehri time has ended! Fajr has begun.")
            return

        embed = discord.Embed(
            title="⏰ Sehri Countdown",
            description=f"Time remaining until Sehri ends in {ramadan_bot.current_city}",
            color=discord.Color.dark_blue()
        )

        embed.add_field(
            name="🕐 Countdown",
            value=f"**{countdown['hours']}** hours, **{countdown['minutes']}** minutes, **{countdown['seconds']}** seconds",
            inline=False
        )

        embed.add_field(
            name="🌅 Sehri Ends (Fajr)",
            value=f"**{countdown['sehri_time']}** PKT",
            inline=False
        )

        await ctx.send(embed=embed)

# Setup automated tasks
def setup_ramadan_tasks(bot, ramadan_bot):

    @tasks.loop(minutes=1)
    async def check_prayer_times():
        """Check for Sehri and Iftar times every minute"""
        now = datetime.now(PKT)
        current_time = now.strftime("%H:%M")
        current_date = now.strftime("%Y-%m-%d")

        timings = await ramadan_bot.fetch_prayer_times()
        if not timings:
            return

        fajr_time = timings['Fajr']
        maghrib_time = timings['Maghrib']

        # Parse times
        fajr_hour, fajr_minute = map(int, fajr_time.split(':'))
        maghrib_hour, maghrib_minute = map(int, maghrib_time.split(':'))

        # Calculate Sehri reminder time (15 minutes before Fajr)
        sehri_reminder_dt = now.replace(hour=fajr_hour, minute=fajr_minute, second=0) - timedelta(minutes=RAMADAN_CONFIG['sehri_reminder_minutes'])
        sehri_reminder_time = sehri_reminder_dt.strftime("%H:%M")

        # Sehri reminder
        if current_time == sehri_reminder_time and ramadan_bot.last_sehri_reminder != current_date:
            channel = discord.utils.get(bot.guilds[0].text_channels, name=RAMADAN_CONFIG['general_channel'])
            if channel:
                minutes_left = RAMADAN_CONFIG['sehri_reminder_minutes']

                embed = discord.Embed(
                    title="🌙 Sehri Reminder!",
                    description=f"⏰ **{minutes_left} minutes** until Fajr!",
                    color=discord.Color.dark_blue()
                )

                embed.add_field(
                    name="Fajr Time",
                    value=f"**{ramadan_bot.convert_to_12hr(fajr_time)}** PKT",
                    inline=False
                )

                embed.add_field(
                    name="⚠️ Reminder",
                    value=f"Finish your Sehri now and prepare for Fajr prayer!\nStop eating and drinking before {ramadan_bot.convert_to_12hr(fajr_time)}",
                    inline=False
                )

                embed.set_footer(text=f"City: {ramadan_bot.current_city}")

                await channel.send(embed=embed)
                ramadan_bot.last_sehri_reminder = current_date

        # Iftar time
        if current_time == maghrib_time and ramadan_bot.last_iftar_reminder != current_date:
            channel = discord.utils.get(bot.guilds[0].text_channels, name=RAMADAN_CONFIG['general_channel'])
            if channel:
                embed = discord.Embed(
                    title="🌆 It's Iftar Time!",
                    description="Alhamdulillah! Time to break your fast 🤲",
                    color=discord.Color.gold()
                )

                embed.add_field(
                    name="🤲 Iftar Dua",
                    value="**ذَهَبَ الظَّمَأُ وَابْتَلَّتِ الْعُرُوقُ وَثَبَتَ الأَجْرُ إِنْ شَاءَ اللَّهُ**\n\n*Dhahaba az-Zama-u wabtallatil-'Urūq wa Thabatal-Ajru in shā-Allāh*\n\nThe thirst has gone, the veins are moist, and the reward is certain if Allāh wills.\n\n(Abu Dawud 2357 - Hasan)",
                    inline=False
                )

                embed.add_field(
                    name="Maghrib Time",
                    value=f"**{ramadan_bot.convert_to_12hr(maghrib_time)}** PKT",
                    inline=False
                )

                embed.set_footer(text=f"May Allah accept your fast | City: {ramadan_bot.current_city}")

                await channel.send(embed=embed)
                ramadan_bot.last_iftar_reminder = current_date

    @tasks.loop(hours=24)
    async def daily_hadith():
        """Post daily hadith at 8:00 PM PKT"""
        channel = discord.utils.get(bot.guilds[0].text_channels, name=RAMADAN_CONFIG['ramadan_channel'])
        if not channel:
            channel = discord.utils.get(bot.guilds[0].text_channels, name=RAMADAN_CONFIG['general_channel'])

        if channel:
            hadith = await ramadan_bot.fetch_random_hadith()

            embed = discord.Embed(
                title="📿 Daily Ramadan Hadith",
                description="*Authentic hadith about the blessed month*",
                color=discord.Color.gold()
            )

            embed.add_field(
                name="Arabic",
                value=hadith['arabic'],
                inline=False
            )

            embed.add_field(
                name="English Translation",
                value=hadith['english'],
                inline=False
            )

            embed.set_footer(text=f"Reference: {hadith['reference']}")

            await channel.send(embed=embed)

    @daily_hadith.before_loop
    async def before_daily_hadith():
        await bot.wait_until_ready()
        now = datetime.now(PKT)
        next_run = now.replace(
            hour=RAMADAN_CONFIG['hadith_time']['hour'],
            minute=RAMADAN_CONFIG['hadith_time']['minute'],
            second=0,
            microsecond=0
        )
        if now >= next_run:
            next_run += timedelta(days=1)
        wait_seconds = (next_run - now).total_seconds()
        await asyncio.sleep(wait_seconds)

    @tasks.loop(hours=24)
    async def daily_ayat():
        """Post daily Quranic verse at 9:00 AM PKT"""
        channel = discord.utils.get(bot.guilds[0].text_channels, name=RAMADAN_CONFIG['ramadan_channel'])
        if not channel:
            channel = discord.utils.get(bot.guilds[0].text_channels, name=RAMADAN_CONFIG['general_channel'])

        if channel:
            ayat = await ramadan_bot.fetch_random_ayat()

            embed = discord.Embed(
                title="📖 Daily Quranic Verse",
                description="*Guidance from the Holy Quran*",
                color=discord.Color.blue()
            )

            embed.add_field(
                name="Arabic",
                value=ayat['arabic'],
                inline=False
            )

            embed.add_field(
                name="English Translation",
                value=ayat['english'],
                inline=False
            )

            embed.set_footer(text=f"Surah {ayat['surah']}, Ayah {ayat['ayah']}")

            await channel.send(embed=embed)

    @daily_ayat.before_loop
    async def before_daily_ayat():
        await bot.wait_until_ready()
        now = datetime.now(PKT)
        next_run = now.replace(
            hour=RAMADAN_CONFIG['ayat_time']['hour'],
            minute=RAMADAN_CONFIG['ayat_time']['minute'],
            second=0,
            microsecond=0
        )
        if now >= next_run:
            next_run += timedelta(days=1)
        wait_seconds = (next_run - now).total_seconds()
        await asyncio.sleep(wait_seconds)

    # Start all tasks
    check_prayer_times.start()
    daily_hadith.start()
    daily_ayat.start()

    return check_prayer_times, daily_hadith, daily_ayat

# Main function to initialize Ramadan features
def initialize_ramadan_features(bot):
    """Initialize all Ramadan features"""
    ramadan_bot = RamadanBot(bot)
    setup_ramadan_commands(bot, ramadan_bot)
    tasks = setup_ramadan_tasks(bot, ramadan_bot)

    print("✅ Ramadan features initialized!")
    print(f"   - City: {ramadan_bot.current_city}")
    print(f"   - Sehri/Iftar reminders enabled")
    print(f"   - Daily Hadith at {RAMADAN_CONFIG['hadith_time']['hour']}:00 PKT")
    print(f"   - Daily Ayat at {RAMADAN_CONFIG['ayat_time']['hour']}:00 PKT")

    return ramadan_bot, tasks
