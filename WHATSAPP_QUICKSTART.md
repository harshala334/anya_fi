# 🚀 WhatsApp Quick Start

## Setup (10 minutes)

### 1. Create Meta Business App

1. Go to https://developers.facebook.com/
2. Create App → Business type
3. Add WhatsApp product

### 2. Get Credentials

From WhatsApp → API Setup, copy:
- **Access Token** (temporary, 24h)
- **Phone Number ID**
- **Business Account ID**

### 3. Setup ngrok (for local testing)

```bash
# Install and run
sudo snap install ngrok
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### 4. Configure Webhook

In Meta Dashboard → WhatsApp → Configuration:
- **Callback URL**: `https://your-ngrok-url.ngrok.io/webhook/whatsapp`
- **Verify Token**: `anya_verify_token_2024`
- Subscribe to: `messages`

### 5. Update .env

```bash
WHATSAPP_ACCESS_TOKEN=your_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_id_here
WHATSAPP_BUSINESS_ACCOUNT_ID=your_account_id_here
WHATSAPP_VERIFY_TOKEN=anya_verify_token_2024
```

### 6. Start Server

```bash
# Terminal 1: ngrok
ngrok http 8000

# Terminal 2: FastAPI
uvicorn app.main:app --reload
```

### 7. Test

1. In Meta Dashboard, add your phone as test recipient
2. Send message to test number
3. Bot should respond!

## Commands

- `/start` - Get started
- `/help` - Show help
- `/stats` - Budget status
- `/goals` - View goals

Or just chat naturally! 💬

## Troubleshooting

**Webhook verification failed?**
- Check ngrok is running
- Verify token matches in `.env`

**Bot not responding?**
- Check FastAPI logs
- Verify access token in `.env`

See `whatsapp_setup_guide.md` for detailed instructions.
