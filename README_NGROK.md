# Quick Ngrok Setup

## Quick Start

1. **Download ngrok**: https://ngrok.com/download (Windows version)
2. **Extract** `ngrok.exe` to this project folder or add it to your PATH
3. **Get your auth token**: Sign up at https://dashboard.ngrok.com and get your token
4. **Authenticate**: Run `ngrok authtoken YOUR_TOKEN` in PowerShell/CMD
5. **Start ngrok**: Run `ngrok http 5000` (make sure Flask is running first!)

## Using the Helper Scripts

### Option 1: PowerShell Script
```powershell
.\start_ngrok.ps1
```

### Option 2: Batch File
```cmd
start_ngrok.bat
```

### Option 3: Manual
```bash
ngrok http 5000
```

## Important Notes

- **Start Flask first**: Make sure `python app.py` is running before starting ngrok
- **Free tier**: URLs change each time you restart ngrok
- **Keep it running**: Don't close the ngrok window while you need the tunnel
- **Public URL**: Ngrok will show you a URL like `https://xxxx.ngrok.io` - share this to access your app

## Troubleshooting

- **"ngrok not found"**: Either add ngrok.exe to your PATH or place it in this folder
- **"Connection refused"**: Make sure Flask is running on port 5000
- **"Auth token required"**: Run `ngrok authtoken YOUR_TOKEN` first
