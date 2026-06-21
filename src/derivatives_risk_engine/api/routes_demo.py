from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

DEMO_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DeltaCore Demo</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f5f7f8;
      --panel: #ffffff;
      --ink: #172126;
      --muted: #68757d;
      --line: #d9e0e3;
      --accent: #006d77;
      --accent-dark: #004e56;
      --danger: #a23b3b;
      --positive: #0f7b55;
      --shadow: 0 10px 30px rgba(23, 33, 38, 0.08);
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--ink);
      font-family:
        Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .shell {
      width: min(1180px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 24px 0 32px;
    }

    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 18px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--line);
    }

    h1 {
      margin: 0;
      font-size: 28px;
      line-height: 1.1;
      letter-spacing: 0;
    }

    .status {
      min-width: 112px;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 7px 12px;
      background: var(--panel);
      color: var(--muted);
      font-size: 13px;
      text-align: center;
    }

    main {
      display: grid;
      grid-template-columns: minmax(280px, 360px) 1fr;
      gap: 16px;
      align-items: start;
    }

    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }

    .controls {
      padding: 16px;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }

    label {
      display: grid;
      gap: 5px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.2;
    }

    input,
    select,
    textarea {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 9px 10px;
      color: var(--ink);
      background: #ffffff;
      font: inherit;
      font-size: 14px;
    }

    textarea {
      min-height: 120px;
      resize: vertical;
      line-height: 1.45;
    }

    .wide {
      grid-column: 1 / -1;
    }

    button {
      width: 100%;
      border: 0;
      border-radius: 6px;
      margin-top: 14px;
      padding: 11px 12px;
      background: var(--accent);
      color: #ffffff;
      font-weight: 700;
      cursor: pointer;
    }

    button:hover {
      background: var(--accent-dark);
    }

    button:disabled {
      cursor: wait;
      opacity: 0.72;
    }

    .results {
      display: grid;
      gap: 16px;
    }

    .metrics {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      padding: 16px;
    }

    .metric {
      min-height: 94px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: #fbfcfc;
    }

    .metric span {
      display: block;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.2;
      margin-bottom: 8px;
    }

    .metric strong {
      display: block;
      overflow-wrap: anywhere;
      font-size: 24px;
      line-height: 1.15;
      letter-spacing: 0;
    }

    .metric.negative strong {
      color: var(--danger);
    }

    .metric.positive strong {
      color: var(--positive);
    }

    .table-wrap {
      overflow-x: auto;
      padding: 0 16px 16px;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 620px;
      font-size: 14px;
    }

    th,
    td {
      border-bottom: 1px solid var(--line);
      padding: 10px 8px;
      text-align: right;
      white-space: nowrap;
    }

    th:first-child,
    td:first-child {
      text-align: left;
    }

    th {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }

    .log {
      margin: 0;
      padding: 0 16px 16px;
      color: var(--danger);
      min-height: 20px;
      font-size: 13px;
    }

    @media (max-width: 860px) {
      main,
      .metrics {
        grid-template-columns: 1fr;
      }

      header {
        align-items: flex-start;
        flex-direction: column;
      }

      .status {
        width: 100%;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <header>
      <h1>DeltaCore Demo</h1>
      <div class="status" id="status">idle</div>
    </header>

    <main>
      <section class="panel controls" aria-label="Inputs">
        <div class="grid">
          <label>Type
            <select id="optionType">
              <option value="call">Call</option>
              <option value="put">Put</option>
            </select>
          </label>
          <label>Spot
            <input id="spot" type="number" step="0.01" value="100">
          </label>
          <label>Strike
            <input id="strike" type="number" step="0.01" value="100">
          </label>
          <label>Expiry
            <input id="expiry" type="number" step="0.01" value="1">
          </label>
          <label>Rate
            <input id="rate" type="number" step="0.001" value="0.05">
          </label>
          <label>Dividend
            <input id="dividend" type="number" step="0.001" value="0">
          </label>
          <label>Volatility
            <input id="volatility" type="number" step="0.01" value="0.20">
          </label>
          <label>Confidence
            <input id="confidence" type="number" step="0.01" value="0.80">
          </label>
          <label class="wide">PnL observations
            <textarea id="pnls">12, 7, 5, 2, 0, -1, -3, -8, -10, -20</textarea>
          </label>
        </div>
        <button id="runButton" type="button">Run analytics</button>
      </section>

      <section class="results" aria-label="Results">
        <section class="panel metrics">
          <div class="metric">
            <span>Price</span>
            <strong id="price">-</strong>
          </div>
          <div class="metric">
            <span>Delta</span>
            <strong id="delta">-</strong>
          </div>
          <div class="metric">
            <span>Implied vol</span>
            <strong id="impliedVol">-</strong>
          </div>
          <div class="metric negative">
            <span>VaR / ES</span>
            <strong id="varEs">-</strong>
          </div>
        </section>

        <section class="panel">
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Scenario</th>
                  <th>Base</th>
                  <th>Shocked</th>
                  <th>PnL</th>
                  <th>Spot</th>
                  <th>Vol</th>
                </tr>
              </thead>
              <tbody id="scenarioRows"></tbody>
            </table>
          </div>
          <p class="log" id="log"></p>
        </section>
      </section>
    </main>
  </div>

  <script>
    const byId = (id) => document.getElementById(id);
    const format = (value) => Number(value).toLocaleString(undefined, {
      maximumFractionDigits: 6
    });

    function numberValue(id) {
      return Number(byId(id).value);
    }

    function basePayload() {
      return {
        option_type: byId("optionType").value,
        spot: numberValue("spot"),
        strike: numberValue("strike"),
        time_to_expiry: numberValue("expiry"),
        risk_free_rate: numberValue("rate"),
        dividend_yield: numberValue("dividend"),
        volatility: numberValue("volatility")
      };
    }

    function parsePnls() {
      return byId("pnls").value
        .split(/[\\s,]+/)
        .filter(Boolean)
        .map(Number);
    }

    async function postJson(path, payload) {
      const response = await fetch(path, {
        method: "POST",
        headers: {"content-type": "application/json"},
        body: JSON.stringify(payload)
      });
      if (!response.ok) {
        const details = await response.text();
        throw new Error(`${path}: ${response.status} ${details}`);
      }
      return response.json();
    }

    async function runAnalytics() {
      byId("runButton").disabled = true;
      byId("status").textContent = "running";
      byId("log").textContent = "";

      try {
        const base = basePayload();
        const priceResponse = await fetch("/price/european", {
          method: "POST",
          headers: {"content-type": "application/json"},
          body: JSON.stringify(base)
        });
        if (!priceResponse.ok) {
          const details = await priceResponse.text();
          throw new Error(`/price/european: ${priceResponse.status} ${details}`);
        }
        const price = await priceResponse.json();
        const greeks = await postJson("/greeks/european", base);
        const implied = await postJson("/implied-volatility", {
          option_type: base.option_type,
          spot: base.spot,
          strike: base.strike,
          time_to_expiry: base.time_to_expiry,
          risk_free_rate: base.risk_free_rate,
          dividend_yield: base.dividend_yield,
          target_price: price.price
        });
        const scenario = await postJson("/risk/scenario-pnl", {
          ...base,
          shocks: [
            {name: "spot_down_5pct", spot_shift: -0.05 * base.spot},
            {name: "vol_up_5_points", volatility_shift: 0.05}
          ]
        });
        const risk = await postJson("/risk/historical-var", {
          pnls: parsePnls(),
          confidence_level: numberValue("confidence")
        });

        byId("price").textContent = format(price.price);
        byId("delta").textContent = format(greeks.delta);
        byId("impliedVol").textContent = implied.implied_volatility === null
          ? "n/a"
          : format(implied.implied_volatility);
        byId("varEs").textContent = `${format(risk.value_at_risk)} / ${format(
          risk.expected_shortfall
        )}`;
        byId("scenarioRows").innerHTML = scenario.results.map((result) => `
          <tr>
            <td>${result.scenario_name}</td>
            <td>${format(result.base_price)}</td>
            <td>${format(result.shocked_price)}</td>
            <td>${format(result.pnl)}</td>
            <td>${format(result.shocked_spot)}</td>
            <td>${format(result.shocked_volatility)}</td>
          </tr>
        `).join("");
        byId("status").textContent = "ready";
      } catch (error) {
        byId("status").textContent = "error";
        byId("log").textContent = error instanceof Error ? error.message : String(error);
      } finally {
        byId("runButton").disabled = false;
      }
    }

    window.addEventListener("DOMContentLoaded", () => {
      byId("runButton").addEventListener("click", runAnalytics);
      runAnalytics();
    });
  </script>
</body>
</html>
"""


@router.get("/demo", response_class=HTMLResponse)
def demo() -> HTMLResponse:
    """Serve the lightweight browser demo."""
    return HTMLResponse(DEMO_HTML)
