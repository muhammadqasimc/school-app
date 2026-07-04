# Cloudflare Tunnel – Why It Stopped & How to Fix

## Why it stopped working

Your tunnel was probably working when you ran it by hand. After you set the **Flask app** to run at Windows startup, only the app started on login—**the Cloudflare tunnel did not**. So:

- **Flask** was running on `http://localhost:5000`
- **cloudflared** was not running, so `https://kismetschool.co.za` had nothing to connect to

So the site stopped working after a reboot or when you closed the tunnel window.

---

## What was changed

1. **`start_cloudflare_tunnel.bat`**  
   Starts your existing tunnel (ID `5e10044d-2520-4c7d-8fef-c1bc69a1013c`) so `kismetschool.co.za` → `localhost:5000`.

2. **Startup setup**  
   Running `setup_startup.ps1` now adds **two** shortcuts to the Startup folder:
   - **ReportingApp** → starts the Flask app
   - **ReportingApp_Cloudflare** → starts the Cloudflare tunnel

   So after you log in, both the app and the tunnel start, and the site works again.

3. **This guide**  
   For quick checks and fixes.

---

## Quick fix (right now)

1. Make sure the **Flask app** is running (you should see its window or have started it with `start_app.bat`).
2. Double‑click **`start_cloudflare_tunnel.bat`** in your app folder.  
   A window will open and stay open while the tunnel is running.
3. Open **https://kismetschool.co.za** in your browser. It should load your app.

---

## Make it run on every login

Run the startup setup again so the **tunnel** is also added to startup:

```powershell
cd "C:\Users\User\Documents\Reporting_app"
powershell -ExecutionPolicy Bypass -File setup_startup.ps1
```

After that, when you log in to Windows:

- One window = Flask app  
- Second window = Cloudflare tunnel  

Both start automatically; you don’t need to run the batch files by hand.

---

## If `cloudflared` is not found

The batch file looks for `cloudflared` in:

- Your **PATH**
- **`cloudflared.exe`** in the app folder: `C:\Users\User\Documents\Reporting_app\`
- **`C:\Program Files (x86)\cloudflared\cloudflared.exe`**

If you see “cloudflared not found”:

1. Download **cloudflared** for Windows:  
   https://github.com/cloudflare/cloudflared/releases  
   Get the latest `cloudflared-windows-amd64.exe`, rename it to `cloudflared.exe`, and put it in:
   `C:\Users\User\Documents\Reporting_app\`
2. Or install via winget:
   ```bat
   winget install Cloudflare.cloudflared
   ```
   Then `start_cloudflare_tunnel.bat` will find it from PATH.

---

## Check that everything is correct

| Check | How |
|------|-----|
| Flask is listening | In a browser, open **http://localhost:5000** – you should see your app. |
| Tunnel config | Open **`C:\Users\User\.cloudflared\config.yml`** – should have `tunnel: 5e10044d-2520-4c7d-8fef-c1bc69a1013c` and `service: http://localhost:5000`. |
| Credentials file | File exists: **`C:\Users\User\.cloudflared\5e10044d-2520-4c7d-8fef-c1bc69a1013c.json`**. |
| DNS in Cloudflare | In Cloudflare Dashboard → DNS: **kismetschool.co.za** (or your subdomain) is a **CNAME** to **`5e10044d-2520-4c7d-8fef-c1bc69a1013c.cfargotunnel.com`**, proxy ON (orange cloud). |

---

## Still not working?

- **502 Bad Gateway**  
  Usually means the tunnel is running but Flask is not. Start the app first, then the tunnel.

- **Tunnel window closes immediately**  
  Run from Command Prompt to see the error:
  ```bat
  cd C:\Users\User\Documents\Reporting_app
  cloudflared tunnel run 5e10044d-2520-4c7d-8fef-c1bc69a1013c
  ```
  If it says “credentials” or “certificate”, run `cloudflared tunnel login` again and then rerun the tunnel.

- **Site never loads**  
  Confirm DNS (CNAME and orange cloud) in Cloudflare and wait a few minutes for DNS to update.

---

**Summary:** The tunnel was not set to run at startup. Use `start_cloudflare_tunnel.bat` for now, and run `setup_startup.ps1` once so both the app and the tunnel start automatically when you log in.
