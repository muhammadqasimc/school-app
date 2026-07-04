# Ngrok Setup Guide

## Step 1: Download Ngrok

1. Go to https://ngrok.com/download
2. Download the Windows version (ZIP file)
3. Extract the `ngrok.exe` file to a folder (e.g., `C:\ngrok\`)

## Step 2: Get Your Auth Token

1. Sign up for a free account at https://dashboard.ngrok.com/signup
2. After signing up, go to https://dashboard.ngrok.com/get-started/your-authtoken
3. Copy your authtoken

## Step 3: Authenticate Ngrok

Open PowerShell or Command Prompt and run:
```
ngrok authtoken YOUR_AUTHTOKEN_HERE
```

Replace `YOUR_AUTHTOKEN_HERE` with the token you copied.

## Step 4: Run Ngrok

Once authenticated, you can start ngrok with:
```
ngrok http 5000
```

This will create a tunnel to your Flask app running on port 5000.

## Step 5: Access Your App

Ngrok will provide you with a public URL like:
- `https://xxxx-xx-xxx-xx-xx.ngrok.io`

You can share this URL to access your Flask application from anywhere on the internet.

## Note

- The free version of ngrok provides a random URL each time you restart it
- For a fixed URL, you'll need a paid plan
- Keep ngrok running while you want the tunnel active
- Make sure your Flask app is running on port 5000 before starting ngrok
