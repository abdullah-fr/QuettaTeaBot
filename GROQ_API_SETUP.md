# Groq API Setup for TLDR Command

The `/tldr` command now uses AI (Groq's Llama 3.1 70B model) to generate ChatGPT-level narrative summaries!

## Get Free API Key (No Credit Card Required)

1. Go to https://console.groq.com/keys
2. Sign up with Google/GitHub (free, no credit card)
3. Click "Create API Key"
4. Copy your API key

## Add to Your Bot

### Option 1: Add to .env file (Local Testing)

Edit your `.env` file and add:
```
GROQ_API_KEY=gsk_your_api_key_here
```

### Option 2: Add to Wispbyte (Production)

1. Go to your Wispbyte dashboard
2. Click on "Files" tab
3. Edit the `.env` file
4. Add this line:
```
GROQ_API_KEY=gsk_your_api_key_here
```
5. Save and restart the bot

## How It Works

- **With API Key**: Uses Groq's Llama 3.1 70B model to generate natural, story-like summaries
- **Without API Key**: Falls back to basic message sampling

## Example Output (With AI)

```
Summary of the Conversation 💬

This Discord chat is mostly friendly roasting and casual banter between you and a few others.

Main flow of the conversation:

Joke about surgery and high ping
You joked that if a surgeon has high ping during surgery, they might accidentally
remove a kidney instead of the heart. Others responded by teasing that heart and
kidney are far apart so that mistake is unlikely.

Light roasting
People started making fun of your knowledge of biology. You replied that you are
not from a medical background and that you studied biology only in matric.

Age discussion
Someone said matric was long ago. Ages were revealed: You said you are 21.
Another person said they are 20. More joking followed about being old or young.

Ending
Someone said they are going to university and jokingly said they will burn the
uni with black market kerosene, clearly sarcastic humor.
```

## API Limits

- **Free Tier**: 30 requests/minute, 14,400 requests/day
- **More than enough** for a Discord bot!

## Troubleshooting

If you see "⚠️ Set GROQ_API_KEY environment variable":
1. Make sure you added the key to `.env`
2. Restart the bot
3. Check the key starts with `gsk_`

## Alternative: Without API Key

The bot will still work without the API key, but summaries will be basic message samples instead of AI-generated narratives.
