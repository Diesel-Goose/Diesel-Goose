# X402 - Simple XRP Payment Gateway

Simple XRP payment receiver for Greenhead Labs. Verify XRP payments on XRPL.

## Quick Start

```bash
npm install
npm run dev
```

## API

### POST /api/payment

Verify an XRP payment.

**Request:**
```json
{
  "txHash": "A1B2C3D4...",
  "sender": "rSenderAddress",
  "amount": "10",
  "destination": "rYourAddress"
}
```

**Response:**
```json
{
  "success": true,
  "txHash": "A1B2C3D4...",
  "amount": "10",
  "sender": "rSenderAddress",
  "ledgerIndex": 123456,
  "timestamp": "2024-03-10T..."
}
```

## Deploy

```bash
vercel --prod --scope=greenhead-labs
```

## DNS Setup

Add CNAME in GoDaddy:
- Name: `x402`
- Value: `cname.vercel-dns.com`
