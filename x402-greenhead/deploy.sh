#!/bin/bash
# Deploy x402.greenhead.io
# Greenhead Labs - Woody Pintail

echo "========================================"
echo "Deploying X402 Gateway"
echo "Greenhead Labs"
echo "========================================"
echo ""

cd "$(dirname "$0")"

# Build
echo "Building..."
npm run build

# Deploy
echo ""
echo "Deploying to Vercel..."
vercel --prod --scope=greenhead-labs --yes

echo ""
echo "========================================"
echo "✅ Deployed!"
echo "========================================"
echo ""
echo "Next: Configure DNS in GoDaddy"
echo "  CNAME: x402 → cname.vercel-dns.com"
echo ""
