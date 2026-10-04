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
      min-width: 0;
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

    input[type="range"] { accent-color: var(--accent); }

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
      min-width: 0;
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

    .table-wrap:focus-visible {
      outline: 2px solid var(--accent);
      outline-offset: 2px;
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

    .intro { color: var(--muted); line-height: 1.5; }
    .curve { padding: 16px; }
    .curve h2 { margin: 0 0 8px; font-size: 18px; }
    .curve svg { display: block; width: 100%; height: auto; }
    .curve path { fill: none; stroke: var(--accent); stroke-width: 3; }
    .curve line { stroke: var(--line); }
    .curve text { fill: var(--muted); font-size: 12px; }
    .curve circle { fill: var(--accent); }
    .curve table { min-width: 0; }
    :focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }

    @media (max-width: 860px) {
      main,
      .metrics {
        grid-template-columns: minmax(0, 1fr);
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
      <div class="status" id="status" role="status" aria-live="polite">idle</div>
    </header>

    <main>
      <section class="panel controls" aria-label="Inputs">
        <p class="intro">Explore a European option under Black-Scholes. Change spot or volatility
          to update prices and scenarios. Synthetic inputs; no live market data.</p>
        <div class="grid">
          <label>Type
            <select id="optionType">
              <option value="call">Call</option>
              <option value="put">Put</option>
            </select>
          </label>
          <label>Spot (currency units)
            <input id="spot" type="number" min="0.01" step="0.01" value="100">
          </label>
          <label class="wide">Explore spot (10 to 200)
            <input id="spotSlider" type="range" min="10" max="200" step="1" value="100">
          </label>
          <label>Strike
            <input id="strike" type="number" step="0.01" value="100">
          </label>
          <label>Expiry (years)
            <input id="expiry" type="number" min="0.0001" step="0.01" value="1">
          </label>
          <label>Rate (annual decimal)
            <input id="rate" type="number" step="0.001" value="0.05">
          </label>
          <label>Dividend (annual decimal)
            <input id="dividend" type="number" step="0.001" value="0">
          </label>
          <label>Volatility (annual decimal)
            <input id="volatility" type="number" step="0.01" value="0.20">
          </label>
          <label class="wide">Explore volatility (1% to 100%)
            <input id="volSlider" type="range" min="0.01" max="1" step="0.01" value="0.20">
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
            <span>Recovered input volatility</span>
            <strong id="impliedVol">-</strong>
          </div>
          <div class="metric negative">
            <span>VaR / ES</span>
            <strong id="varEs">-</strong>
          </div>
        </section>

        <section class="panel curve" aria-label="Price sensitivity">
          <h2>Option price versus spot</h2>
          <p class="intro">Nine scenarios from 80% to 120% of the selected spot.
            Other inputs stay fixed.
            The dot marks the selected spot. Prices use the same backend model as the metrics.</p>
          <svg id="priceCurve" viewBox="0 0 640 250" role="img"
            aria-label="Option price versus spot; numerical values in the table below"></svg>
          <details><summary>Inspect curve values</summary>
            <div class="table-wrap" role="region" aria-label="Curve values" tabindex="0">
              <table><thead><tr><th>Spot</th><th>Option price</th></tr></thead>
                <tbody id="curveRows"></tbody></table>
            </div>
          </details>
        </section>

        <section class="panel">
          <div class="table-wrap" role="region" aria-label="Scenario results" tabindex="0">
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

    async function postJson(path, payload, signal) {
      const response = await fetch(path, {
        method: "POST",
        headers: {"content-type": "application/json"},
        body: JSON.stringify(payload), signal
      });
      if (!response.ok) {
        const details = await response.text();
        throw new Error(`${path}: ${response.status} ${details}`);
      }
      return response.json();
    }

    let revision = 0;
    let activeRequest;
    let updateTimer;

    function clearResults() {
      curvePoints = [];
      ["price", "delta", "impliedVol", "varEs"].forEach(id => byId(id).textContent = "—");
      ["scenarioRows", "curveRows", "priceCurve"].forEach(id => byId(id).replaceChildren());
    }

    let curvePoints = [];
    function drawCurve(points) {
      curvePoints = points;
      if (!points.length) return;
      const width = Math.max(280, byId("priceCurve").clientWidth);
      byId("priceCurve").setAttribute("viewBox", `0 0 ${width} 250`);
      const minX = points[0].shocked_spot;
      const maxX = points[points.length - 1].shocked_spot;
      const maxY = Math.max(...points.map(point => point.shocked_price), 0.01) * 1.05;
      const x = value => 62 + (value - minX) / (maxX - minX) * (width - 80);
      const y = value => 210 - value / maxY * 190;
      const path = points.map((point, i) =>
        `${i ? "L" : "M"} ${x(point.shocked_spot)} ${y(point.shocked_price)}`).join(" ");
      byId("priceCurve").innerHTML = `
        <line x1="62" y1="20" x2="62" y2="210" />
        <line x1="62" y1="210" x2="${width - 18}" y2="210" />
        <text x="8" y="16">Price</text><text x="12" y="210">0</text>
        <text x="8" y="35">${maxY.toFixed(2)}</text>
        <text x="62" y="230">${format(minX)}</text>
        <text x="${width - 18}" y="230" text-anchor="end">${format(maxX)}</text>
        <text x="${width / 2}" y="248" text-anchor="middle">Spot (currency units)</text>
        <path d="${path}" />
        <circle cx="${x(points[4].shocked_spot)}" cy="${y(points[4].shocked_price)}" r="5" />`;
      byId("curveRows").innerHTML = points.map(point => `<tr>
        <td>${format(point.shocked_spot)}</td><td>${format(point.shocked_price)}</td></tr>`).join("");
    }

    async function runAnalytics() {
      clearTimeout(updateTimer);
      activeRequest?.abort();
      activeRequest = new AbortController();
      const signal = activeRequest.signal;
      const current = ++revision;
      clearResults();
      byId("runButton").disabled = true;
      byId("status").textContent = "running";
      byId("log").textContent = "";

      try {
        const base = basePayload();
        const pnls = parsePnls();
        const confidence = numberValue("confidence");
        const numericInputs = ["spot", "strike", "expiry", "rate", "dividend",
          "volatility", "confidence"];
        if (numericInputs.some(id => byId(id).value.trim() === ""
              || !Number.isFinite(numberValue(id)))
            || base.spot <= 0 || base.strike <= 0
            || base.time_to_expiry <= 0 || base.volatility <= 0
            || confidence <= 0 || confidence >= 1 || pnls.length < 2
            || pnls.some(value => !Number.isFinite(value))) {
          throw new Error("Enter finite inputs: spot, strike, expiry and volatility "
            + "must be positive; "
            + "confidence must be between 0 and 1; provide at least two PnL observations.");
        }
        const curveShocks = Array.from({length: 9}, (_, i) => ({
          name: `curve_${i}`, spot_shift: (i - 4) * 0.05 * base.spot
        }));
        const [price, greeks, scenario, risk] = await Promise.all([
          postJson("/price/european", base, signal),
          postJson("/greeks/european", base, signal),
          postJson("/risk/scenario-pnl", {...base, shocks: [
            {name: "spot_down_5pct", spot_shift: -0.05 * base.spot},
            {name: "vol_up_5_points", volatility_shift: 0.05}, ...curveShocks
          ]}, signal),
          postJson("/risk/historical-var", {pnls, confidence_level: confidence}, signal)
        ]);
        const implied = price.price <= 0 ? {implied_volatility: null}
          : await postJson("/implied-volatility", {
          option_type: base.option_type,
          spot: base.spot,
          strike: base.strike,
          time_to_expiry: base.time_to_expiry,
          risk_free_rate: base.risk_free_rate,
          dividend_yield: base.dividend_yield,
          target_price: price.price
        }, signal);
        if (current !== revision) return;

        byId("price").textContent = format(price.price);
        byId("delta").textContent = format(greeks.delta);
        byId("impliedVol").textContent = implied.implied_volatility === null
          ? "n/a"
          : format(implied.implied_volatility);
        byId("varEs").textContent = `${format(risk.value_at_risk)} / ${format(
          risk.expected_shortfall
        )}`;
        byId("scenarioRows").innerHTML = scenario.results.slice(0, 2).map((result) => `
          <tr>
            <td>${result.scenario_name}</td>
            <td>${format(result.base_price)}</td>
            <td>${format(result.shocked_price)}</td>
            <td>${format(result.pnl)}</td>
            <td>${format(result.shocked_spot)}</td>
            <td>${format(result.shocked_volatility)}</td>
          </tr>
        `).join("");
        drawCurve(scenario.results.slice(2));
        byId("status").textContent = "ready";
      } catch (error) {
        if (current !== revision || signal.aborted) return;
        byId("status").textContent = "error";
        byId("log").textContent = error instanceof Error ? error.message : String(error);
      } finally {
        if (current === revision) byId("runButton").disabled = false;
      }
    }

    function scheduleUpdate() {
      ++revision;
      activeRequest?.abort();
      clearTimeout(updateTimer);
      clearResults();
      byId("log").textContent = "";
      byId("status").textContent = "updating";
      byId("runButton").disabled = false;
      updateTimer = setTimeout(runAnalytics, 250);
    }

    window.addEventListener("DOMContentLoaded", () => {
      window.addEventListener("resize", () => drawCurve(curvePoints));
      byId("runButton").addEventListener("click", runAnalytics);
      const controls = document.querySelectorAll(
        ".controls input, .controls select, .controls textarea");
      controls.forEach(input => {
        input.addEventListener("input", () => {
          if (input.id === "spotSlider") byId("spot").value = input.value;
          if (input.id === "volSlider") byId("volatility").value = input.value;
          if (input.id === "spot") byId("spotSlider").value = input.value;
          if (input.id === "volatility") byId("volSlider").value = input.value;
          scheduleUpdate();
        });
      });
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
