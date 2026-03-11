import { Client } from 'xrpl';

interface VerifyPaymentParams {
  txHash: string;
  sender: string;
  amount: string;
  destination: string;
}

interface VerificationResult {
  valid: boolean;
  error?: string;
  amount?: string;
  sender?: string;
  ledgerIndex?: number;
}

const XRPL_NODE = 'wss://s.altnet.rippletest.net:51233'; // Testnet

export async function verifyXRPLPayment(params: VerifyPaymentParams): Promise<VerificationResult> {
  const client = new Client(XRPL_NODE);
  
  try {
    await client.connect();

    // Fetch transaction from XRPL
    const response = await client.request({
      command: 'tx',
      transaction: params.txHash,
    });

    await client.disconnect();

    const tx = (response.result as any).tx_json;

    if (!tx) {
      return { valid: false, error: 'Transaction not found' };
    }

    // Check if transaction is validated
    if (!(response.result as any).validated) {
      return { valid: false, error: 'Transaction not yet validated' };
    }

    // Verify it's a Payment transaction
    if (tx.TransactionType !== 'Payment') {
      return { valid: false, error: 'Not a payment transaction' };
    }

    // Verify sender matches
    if (tx.Account !== params.sender) {
      return { valid: false, error: 'Sender address mismatch' };
    }

    // Verify destination matches
    if (tx.Destination !== params.destination) {
      return { valid: false, error: 'Destination address mismatch' };
    }

    // Verify amount matches (in drops)
    const expectedDrops = (parseFloat(params.amount) * 1000000).toString();
    if (tx.Amount !== expectedDrops) {
      return { 
        valid: false, 
        error: `Amount mismatch. Expected: ${expectedDrops} drops, Got: ${tx.Amount}` 
      };
    }

    return {
      valid: true,
      amount: params.amount,
      sender: tx.Account,
      ledgerIndex: (response.result as any).ledger_index,
    };

  } catch (error) {
    await client.disconnect().catch(() => {});
    console.error('XRPL verification error:', error);
    return { valid: false, error: 'Failed to verify transaction' };
  }
}

export async function getBalance(address: string): Promise<string> {
  const client = new Client(XRPL_NODE);
  
  try {
    await client.connect();
    
    const response = await client.request({
      command: 'account_info',
      account: address,
    });

    await client.disconnect();

    const balance = (response.result as any).account_data.Balance;
    return (parseInt(balance) / 1000000).toString();

  } catch (error) {
    await client.disconnect().catch(() => {});
    throw error;
  }
}
