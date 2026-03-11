'use client';

import { useState } from 'react';

export default function Home() {
  const [txHash, setTxHash] = useState('');
  const [sender, setSender] = useState('');
  const [amount, setAmount] = useState('');
  const [destination, setDestination] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const verifyPayment = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('/api/payment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ txHash, sender, amount, destination }),
      });

      const data = await response.json();

      if (response.ok) {
        setResult(data);
      } else {
        setError(data.error || 'Verification failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-4xl font-bold mb-2">XRP Payment Gateway</h1>
        <p className="text-gray-400 mb-8">Verify XRP payments on XRPL Testnet</p>

        <div className="space-y-4 bg-gray-800 p-6 rounded-lg">
          <div>
            <label className="block text-sm font-medium mb-1">Transaction Hash</label>
            <input
              type="text"
              value={txHash}
              onChange={(e) => setTxHash(e.target.value)}
              placeholder="A1B2C3D4..."
              className="w-full px-4 py-2 bg-gray-700 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Sender Address</label>
            <input
              type="text"
              value={sender}
              onChange={(e) => setSender(e.target.value)}
              placeholder="rSender..."
              className="w-full px-4 py-2 bg-gray-700 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Amount (XRP)</label>
            <input
              type="text"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="10"
              className="w-full px-4 py-2 bg-gray-700 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Destination Address</label>
            <input
              type="text"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              placeholder="rYourAddress..."
              className="w-full px-4 py-2 bg-gray-700 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
            />
          </div>

          <button
            onClick={verifyPayment}
            disabled={loading}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded-lg font-bold transition-colors"
          >
            {loading ? 'Verifying...' : 'Verify Payment'}
          </button>
        </div>

        {result && (
          <div className="mt-6 p-4 bg-green-900/30 border border-green-500 rounded-lg">
            <h3 className="text-green-400 font-bold mb-2">✅ Payment Verified</h3>
            <pre className="text-sm text-gray-300 overflow-x-auto">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}

        {error && (
          <div className="mt-6 p-4 bg-red-900/30 border border-red-500 rounded-lg">
            <h3 className="text-red-400 font-bold mb-2">❌ Error</h3>
            <p className="text-gray-300">{error}</p>
          </div>
        )}

        <div className="mt-8 p-4 bg-gray-800 rounded-lg">
          <h3 className="font-bold mb-2">How to test</h3>
          <ol className="list-decimal list-inside space-y-1 text-gray-400 text-sm">
            <li>Create XRPL Testnet wallet: <a href="https://test.bithomp.com/" className="text-blue-400">test.bithomp.com</a></li>
            <li>Fund it with Testnet XRP (faucet)</li>
            <li>Send XRP to your destination address</li>
            <li>Copy the transaction hash here</li>
            <li>Click Verify Payment</li>
          </ol>
        </div>
      </div>
    </main>
  );
}
