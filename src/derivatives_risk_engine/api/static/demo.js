
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
      ["price", "delta", "impliedVol"].forEach(id => byId(id).textContent = "—");
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
        
        const numericInputs = ["spot", "strike", "expiry", "rate", "dividend",
          "volatility"];
        if (numericInputs.some(id => byId(id).value.trim() === ""
              || !Number.isFinite(numberValue(id)))
            || base.spot <= 0 || base.strike <= 0
            || base.time_to_expiry < 0 || base.volatility <= 0
            ) {
          throw new Error("Enter finite inputs: spot, strike, expiry and volatility "
            + "must be positive; "
            + "confidence must be between 0 and 1; provide at least two PnL observations.");
        }
        const curveShocks = Array.from({length: 9}, (_, i) => ({
          name: `curve_${i}`, spot_shift: (i - 4) * 0.05 * base.spot
        }));
        const [price, greeks, scenario] = await Promise.all([
          postJson("/price/european", base, signal),
          base.time_to_expiry === 0 ? Promise.resolve({delta: null}) : postJson("/greeks/european", base, signal),
          postJson("/risk/scenario-pnl", {...base, shocks: [
            {name: "spot_down_5pct", spot_shift: -0.05 * base.spot},
            {name: "vol_up_5_points", volatility_shift: 0.05}, ...curveShocks
          ]}, signal)
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
        byId("delta").textContent = greeks.delta === null ? "undefined at expiry" : format(greeks.delta);
        byId("impliedVol").textContent = implied.implied_volatility === null
          ? "n/a"
          : format(implied.implied_volatility);
        byId("ivLog").textContent = implied.diagnostics?.failure_reason || "IV consistency check: own model price, not market calibration.";
        byId("rangeNote").textContent = (base.volatility > 1 || base.volatility < 0.01 || base.spot < 10 || base.spot > 200) ? "Numeric inputs exceed the slider exploration range; calculations use the numeric values shown." : "";
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

    let riskRevision = 0;
    async function runRisk() {
      const current = ++riskRevision;
      byId("varEs").textContent = "—";
      byId("riskLog").textContent = "";
      try {
        const pnls = parsePnls(), confidence = numberValue("confidence");
        if (pnls.length < 2 || pnls.some(value => !Number.isFinite(value)) || !Number.isFinite(confidence) || confidence <= 0 || confidence >= 1) throw new Error("Historical sample: provide at least two finite P&Ls and confidence between 0 and 1.");
        const risk = await postJson("/risk/historical-var", {pnls, confidence_level: confidence});
        if (current !== riskRevision) return;
        byId("varEs").textContent = `${format(risk.value_at_risk)} / ${format(risk.expected_shortfall)}`;
        byId("riskLog").textContent = `${risk.num_observations} independent supplied observations; ${risk.tail_observations} losses at/beyond the empirical quantile. Unrelated to this option.`;
      } catch (error) { if (current === riskRevision) byId("riskLog").textContent = error.message; }
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
      byId("runButton").addEventListener("click", () => {runAnalytics(); runRisk();});
      const controls = document.querySelectorAll(
        ".controls input, .controls select, .controls textarea");
      controls.forEach(input => {
        input.addEventListener("input", () => {
          if (["pnls", "confidence"].includes(input.id)) {runRisk(); return;}
          if (input.id === "spotSlider") byId("spot").value = input.value;
          if (input.id === "volSlider") byId("volatility").value = input.value;
          if (input.id === "spot") byId("spotSlider").value = input.value;
          if (input.id === "volatility") byId("volSlider").value = input.value;
          scheduleUpdate();
        });
      });
      runAnalytics(); runRisk();
    });
  