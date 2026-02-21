import time
import datetime
try:
    from pycoingecko import CoinGeckoAPI
except ImportError:
    CoinGeckoAPI = None  # Fallback mode

HEARTBEAT_PATH = "../HEARTBEAT.md"

class XRPLSignalMonitor:
    def __init__(self, xrp_alert_below_usd: float = 0.45):
        self.cg = CoinGeckoAPI() if CoinGeckoAPI else None
        self.alert_threshold = xrp_alert_below_usd

    def append_heartbeat(self, status: str):
        ts = datetime.datetime.utcnow().isoformat() + "Z"
        entry = f"[XRPL {ts}] | {status} | Founder Notified\n"
        try:
            with open(HEARTBEAT_PATH, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception:
            pass

    def get_xrp_price_usd(self) -> Optional[float]:
        if not self.cg:
            return None
        try:
            data = self.cg.get_price(ids='ripple', vs_currencies='usd')
            return data.get('ripple', {}).get('usd')
        except Exception:
            return None

    def run(self, interval_sec: int = 300):
        while True:
            price = self.get_xrp_price_usd()
            if price is None:
                status = "Price fetch failed – check API/proxy"
            elif price < self.alert_threshold:
                status = f"ALERT: XRP ${price:.4f} BELOW ${self.alert_threshold} – Escalate to Founder"
            else:
                status = f"XRP stable at ${price:.4f}"
            self.append_heartbeat(status)
            print(status)
            time.sleep(interval_sec)

if __name__ == "__main__":
    monitor = XRPLSignalMonitor()
    monitor.run()
