/**
 * Local/production server: serves portfolio.html + POST /api/contact (SMTP via Nodemailer).
 * Copy .env.example → .env and set SMTP_* (Gmail: use an App Password).
 */
require('dotenv').config();
const express = require('express');
const nodemailer = require('nodemailer');
const path = require('path');

const app = express();
const PORT = Number(process.env.PORT || 3000);

const CONTACT_TO = process.env.CONTACT_TO_EMAIL || 'ahadke26@gmail.com';

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

app.use(express.json({ limit: '48kb' }));

app.post('/api/contact', async (req, res) => {
  const { name, email, message } = req.body || {};

  if (!name || !email || !message) {
    return res.status(400).json({ ok: false, error: 'Please fill in name, email, and message.' });
  }
  const nm = String(name).trim();
  const em = String(email).trim();
  const msg = String(message).trim();
  if (nm.length > 200 || em.length > 254 || msg.length > 10000) {
    return res.status(400).json({ ok: false, error: 'One or more fields are too long.' });
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em)) {
    return res.status(400).json({ ok: false, error: 'Please enter a valid email address.' });
  }

  const host = process.env.SMTP_HOST;
  const user = process.env.SMTP_USER;
  const pass = process.env.SMTP_PASS;

  if (!host || !user || !pass) {
    console.error('Missing SMTP_HOST, SMTP_USER, or SMTP_PASS in .env');
    return res.status(503).json({
      ok: false,
      error: 'Mail is not configured on the server. Set SMTP_* in .env.',
    });
  }

  const transporter = nodemailer.createTransport({
    host,
    port: Number(process.env.SMTP_PORT || 587),
    secure: process.env.SMTP_SECURE === 'true',
    auth: { user, pass },
  });

  try {
    await transporter.sendMail({
      from: `"Portfolio site" <${user}>`,
      to: CONTACT_TO,
      replyTo: em,
      subject: `Portfolio contact from ${nm}`,
      text: `From: ${nm} <${em}>\n\n${msg}`,
      html:
        `<p><b>From:</b> ${escapeHtml(nm)} &lt;${escapeHtml(em)}&gt;</p>` +
        `<p style="white-space:pre-wrap">${escapeHtml(msg)}</p>`,
    });
    res.json({ ok: true });
  } catch (err) {
    console.error('sendMail:', err.message);
    res.status(500).json({ ok: false, error: 'Could not send message. Try again later.' });
  }
});

const root = __dirname;
app.get('/', (_req, res) => {
  res.sendFile(path.join(root, 'portfolio.html'));
});

app.use(express.static(root, { index: false }));

app.listen(PORT, () => {
  console.log(`Portfolio server http://localhost:${PORT}`);
  console.log(`Contact → ${CONTACT_TO} (configure SMTP in .env)`);
});
