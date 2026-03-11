import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    console.log('Webhook received:', {
      timestamp: new Date().toISOString(),
      ...body,
    });

    // Handle different event types
    const { event, data } = body;

    switch (event) {
      case 'payment.received':
        console.log('Payment received:', data);
        // Trigger your business logic here
        break;
        
      case 'payment.verified':
        console.log('Payment verified:', data);
        break;
        
      default:
        console.log('Unknown event:', event);
    }

    return NextResponse.json({ received: true });

  } catch (error) {
    console.error('Webhook error:', error);
    return NextResponse.json({ received: false }, { status: 500 });
  }
}
