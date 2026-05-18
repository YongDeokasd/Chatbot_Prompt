const TOKEN = import.meta.env.VITE_LOCAL_API_TOKEN ?? "";
const POLL_INTERVAL = 5000;

type PriceHandler = (symbol: string, price: number) => void;

export class PriceStream {
  private ws: WebSocket | null = null;
  private pollTimer: ReturnType<typeof setInterval> | null = null;
  private handler: PriceHandler;
  private dead = false;

  constructor(handler: PriceHandler) {
    this.handler = handler;
  }

  start() {
    this.connectWS();
  }

  private connectWS() {
    if (this.dead) return;
    const proto = location.protocol === "https:" ? "wss" : "ws";
    const url = `${proto}://${location.host}/api/ws/prices?token=${TOKEN}`;
    this.ws = new WebSocket(url);

    this.ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data) as { symbol: string; price: number };
        this.handler(data.symbol, data.price);
      } catch {}
    };

    this.ws.onclose = () => {
      if (!this.dead) this.startPolling();
    };

    this.ws.onerror = () => {
      this.ws?.close();
    };
  }

  private startPolling() {
    if (this.pollTimer) return;
    this.pollTimer = setInterval(async () => {
      try {
        const res = await fetch(`/api/benchmarks`, {
          headers: { Authorization: `Bearer ${TOKEN}` },
        });
        if (!res.ok) return;
        const benchmarks = await res.json() as Array<{ symbol: string; exchange: string; active: boolean }>;
        for (const b of benchmarks.filter((x) => x.active)) {
          // Fetch last candle as price proxy
          const to = new Date().toISOString().replace(/\.\d+Z$/, "Z");
          const from = new Date(Date.now() - 60_000).toISOString().replace(/\.\d+Z$/, "Z");
          const q = new URLSearchParams({ symbol: b.symbol, exchange: b.exchange, timeframe: "1m", from, to });
          const cr = await fetch(`/api/market/candles?${q}`, {
            headers: { Authorization: `Bearer ${TOKEN}` },
          });
          if (!cr.ok) continue;
          const data = await cr.json() as { candles: Array<{ close: number }> };
          if (data.candles.length > 0) {
            this.handler(b.symbol, data.candles[data.candles.length - 1].close);
          }
        }
        // Try reconnecting WS after polling
        this.stopPolling();
        this.connectWS();
      } catch {}
    }, POLL_INTERVAL);
  }

  private stopPolling() {
    if (this.pollTimer) {
      clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
  }

  stop() {
    this.dead = true;
    this.stopPolling();
    this.ws?.close();
  }
}
