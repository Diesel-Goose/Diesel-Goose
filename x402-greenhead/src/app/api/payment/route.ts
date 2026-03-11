import { NextRequest, NextResponse } from 'next/server';
import { verifyXRPLPayment } from '@/lib/xrp';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { txHash, sender, amount, destination } = body;

    // Validate required fields
    if (!txHash || !sender || !amount || !destination) {
      return NextResponse.json(
        { error: 'Missing required fields: txHash, sender, amount, destination' },
        { status: 400 }
      );
    }

    // Verify payment on XRPL
    const verification = await verifyXRPLPayment({
      txHash,
      sender,
      amount,
      destination,
    });

    if (!verification.valid) {
      return NextResponse.json(
        { error: verification.error },
        { status: 400 }
      );
    }

    // Payment verified - grant access/service here
    // TODO: Store in database, trigger webhook, etc.

    return NextResponse.json({
      success: true,
      txHash,
      amount: verification.amount,
      sender: verification.sender,
      ledgerIndex: verification.ledgerIndex,
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error('Payment verification error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    endpoint: '/api/payment',
    method: 'POST',
    description: 'Verify XRP payment on XRPL',
    requiredFields: ['txHash', 'sender', 'amount', 'destination'],
    example: {
      txHash: 'A1B2C3D4...',
      sender: 'rSenderAddress',
      amount: '10',
      destination: 'rYourAddress',
    },
  });
}
