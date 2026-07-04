/**
 * WhatsApp Web service using whatsapp-web.js.
 * - GET /status  → { ready: boolean, qr?: string } (qr is data URL when not ready)
 * - POST /send   → { to: string, message: string } → sends via WhatsApp
 * Session is persisted via LocalAuth (no re-scan unless session is invalid).
 */
const express = require('express');
const { Client, LocalAuth } = require('whatsapp-web.js');
const QRCode = require('qrcode');

// Keep process alive and log crashes (e.g. after QR scan when library throws)
process.on('uncaughtException', (err) => {
  console.error('Uncaught exception:', err);
});
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled rejection at:', promise, 'reason:', reason);
});

const app = express();
app.use(express.json());

const PORT = process.env.WHATSAPP_SERVICE_PORT || 3001;

let client = null;
let isReady = false;
let currentQrDataUrl = null;

function initClient() {
  if (client) return;
  client = new Client({
    authStrategy: new LocalAuth({ clientId: 'reporting-app' }),
    puppeteer: {
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--disable-gpu',
        '--no-first-run',
      ],
    },
  });

  client.on('qr', async (qr) => {
    isReady = false;
    try {
      currentQrDataUrl = await QRCode.toDataURL(qr, { margin: 2 });
      console.log('QR code generated; scan with WhatsApp on your phone.');
    } catch (err) {
      console.error('QR to image failed:', err);
      currentQrDataUrl = null;
    }
  });

  client.on('ready', () => {
    try {
      isReady = true;
      currentQrDataUrl = null;
      console.log('WhatsApp client is ready.');
    } catch (err) {
      console.error('Error in ready handler:', err);
    }
  });

  client.on('authenticated', () => {
    try {
      console.log('WhatsApp authenticated (loading...)');
    } catch (err) {
      console.error('Error in authenticated handler:', err);
    }
  });

  client.on('auth_failure', (msg) => {
    console.error('Auth failure:', msg);
    isReady = false;
  });

  client.on('disconnected', (reason) => {
    isReady = false;
    console.log('Disconnected:', reason);
  });

  client.initialize().catch((err) => {
    console.error('Client init error:', err);
  });
}

initClient();

/** GET /status - readiness and optional QR data URL for admin UI */
app.get('/status', (req, res) => {
  const payload = { ready: isReady };
  if (!isReady && currentQrDataUrl) payload.qr = currentQrDataUrl;
  res.json(payload);
});

/**
 * POST /send - send a text message.
 * Body: { to: string (E.164 e.g. +27821234567), message: string }
 * Returns: { success: true } or { success: false, error: string }
 */
app.post('/send', async (req, res) => {
  if (!isReady || !client) {
    return res.status(503).json({
      success: false,
      error: 'WhatsApp client not ready. Scan the QR code in Admin → WhatsApp.',
    });
  }
  const { to, message } = req.body || {};
  if (!to || typeof message !== 'string') {
    return res.status(400).json({
      success: false,
      error: 'Missing or invalid "to" or "message".',
    });
  }
  // E.164 (+27821234567) → WhatsApp ID (27821234567@c.us)
  const digits = String(to).replace(/\D/g, '');
  if (!digits.length) {
    return res.status(400).json({
      success: false,
      error: 'Invalid phone number.',
    });
  }
  const chatId = `${digits}@c.us`;
  try {
    await client.sendMessage(chatId, message);
    return res.json({ success: true });
  } catch (err) {
    console.error('Send error:', err);
    return res.status(500).json({
      success: false,
      error: err.message || 'Failed to send message.',
    });
  }
});

app.get('/health', (req, res) => {
  res.json({ ok: true, ready: isReady });
});

app.listen(PORT, '127.0.0.1', () => {
  console.log(`WhatsApp service listening on http://127.0.0.1:${PORT}`);
});
