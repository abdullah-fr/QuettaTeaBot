# 🌙 Ramadan Commands Quick Reference

## Commands

- `!ramadan-times` - Show today's Sehri and Iftar timings (12-hour format)
- `!ramadan-city [city]` - Change city (Islamabad, Lahore, Karachi, Faisalabad, Rawalpindi, Multan, Peshawar, Quetta)
- `!hadith` - Get random Ramadan hadith
- `!ayat` - Get random Quranic verse
- `!iftar-countdown` - Countdown to Iftar (12-hour format)
- `!sehri-countdown` - Countdown to Sehri closing time (12-hour format)

## Automated Features

- **Sehri Reminder**: 15 minutes before Fajr (posts in #general, no @everyone)
- **Iftar Reminder**: At Maghrib time with authentic dua (posts in #general, no @everyone)
- **Daily Hadith**: 8:00 PM PKT (posts in #ramadan-special or #general)
- **Daily Ayat**: 9:00 AM PKT (posts in #ramadan-special or #general)

## Supported Cities

Islamabad (default), Lahore, Karachi, Faisalabad, Rawalpindi, Multan, Peshawar, Quetta

## Time Format

All times are displayed in 12-hour format (e.g., 5:24 AM, 5:56 PM) for easy reading.

## Configuration

Edit `ramadan_features.py` to change:
- Default city
- Channel names
- Posting times
- Reminder timing
