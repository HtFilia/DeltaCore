// Opt-in browser check against the running API; requires Playwright.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

(async () => {
  const browser = await chromium.launch();
  const base = process.env.DELTACORE_DEMO_URL ?? 'http://127.0.0.1:18020';
  const output = process.env.DEMO_CHECK_OUTPUT;
  if (output) fs.mkdirSync(output, {recursive: true});
  try {
    for (const width of [1440, 390]) {
      for (const colorScheme of ['light', 'dark']) {
        const context = await browser.newContext({viewport: {width, height: 1000}, colorScheme});
        const page = await context.newPage();
        const errors = [];
        page.on('pageerror', error => errors.push(error.message));
        await page.goto(`${base}/demo`);
        const ready = () => page.waitForFunction(() => document.querySelector('#status').textContent === 'ready');
        const price = async () => Number((await page.locator('#price').innerText()).replaceAll(',', ''));
        await ready();
        // Independently validated closed-form fixture, also used by API tests.
        assert(Math.abs(await price() - 10.450583572185565) < 1e-6);
        assert.equal(await page.locator('#curveRows tr').count(), 9);
        assert.equal(await page.locator('#priceCurve path').count(), 1);
        await page.getByText('Inspect curve values', {exact: true}).click();
        await page.locator('#spotSlider').focus();
        await page.keyboard.press('ArrowRight');
        await ready();
        assert.equal(await page.locator('#spot').inputValue(), '101');
        assert(await price() > 10.450583572185565);
        await page.locator('#spot').fill('110');
        await ready();
        assert(Math.abs(await price() - 17.662953740590453) < 1e-6);
        const centre = page.locator('#curveRows tr').nth(4);
        assert.equal(await centre.locator('td').first().innerText(), '110');
        assert(Math.abs(Number(await centre.locator('td').last().innerText()) - await price()) < 1e-6);
        // Fast edits must render the latest input, not an earlier request.
        await page.locator('#spot').fill('120');
        await page.locator('#spot').fill('100');
        await ready();
        assert(Math.abs(await price() - 10.450583572185565) < 1e-6);
        await page.locator('#optionType').selectOption('put');
        await ready();
        const parityPut = 10.450583572185565 + 100 * Math.exp(-0.05) - 100;
        assert(Math.abs(await price() - parityPut) < 1e-6);
        await page.locator('#spot').fill('0');
        await page.waitForFunction(() => document.querySelector('#status').textContent === 'error');
        assert.equal(await page.locator('#price').innerText(), '—');
        assert.equal(await page.locator('#priceCurve path').count(), 0);
        await page.setViewportSize({width, height: 950});
        assert.equal(await page.locator('#priceCurve path').count(), 0);
        await page.locator('#spot').fill('100');
        await ready();
        if (width === 390) {
          await page.getByRole('region', {name: 'Scenario results'}).focus();
          await page.keyboard.press('ArrowRight');
          await page.waitForFunction(() => document.querySelector('[aria-label="Scenario results"]').scrollLeft > 0);
        }
        assert(!(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)));
        assert.deepEqual(errors, []);
        if (output) await page.screenshot({path: path.join(output, `deltacore-${width}-${colorScheme}.png`), fullPage: true});
        await context.close();
      }
    }
    console.log('DeltaCore browser checks passed: reference prices/parity, keyboard sliders, live curve, latest inputs, invalid inputs, mobile scrolling.');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
