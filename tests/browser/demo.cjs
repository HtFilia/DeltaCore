const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
(async()=>{
 const browser=await chromium.launch();const base=process.env.DELTACORE_DEMO_URL??'http://127.0.0.1:18020';const out=process.env.DEMO_CHECK_OUTPUT;const results=[];
 if(out)fs.mkdirSync(out,{recursive:true});
 try{for(const width of [1440,390,320])for(const colorScheme of ['light','dark']){
 const context=await browser.newContext({viewport:{width,height:900},colorScheme});const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base+'/demo');const ready=()=>page.waitForFunction(()=>document.querySelector('#status').textContent==='ready');await ready();
 const price=async()=>Number((await page.locator('#price').innerText()).replaceAll(',',''));
 assert(Math.abs(await price()-10.450583572185565)<1e-6);
 assert.equal(await page.locator('#curveRows tr').count(),9);assert.equal(await page.locator('#attributionRows tr').count(),7);
 await page.getByRole('button',{name:'+5 vol points',exact:true}).focus();await page.keyboard.press('Enter');await ready();assert(Number((await page.locator('#fullPnl').innerText()).replaceAll(',',''))>0);
 await page.getByRole('button',{name:'7 calendar days',exact:true}).click();await ready();assert(Number((await page.locator('#fullPnl').innerText()).replaceAll(',',''))<0);
 await page.getByRole('button',{name:'Reset baseline',exact:true}).click();await ready();
 await page.getByText('Independent historical loss sample',{exact:true}).click();await page.locator('#pnls').fill('invalid');await page.getByText(/Historical sample: provide/).waitFor();assert(Math.abs(await price()-10.450583572185565)<1e-6);
 await page.getByText('Change base option assumptions',{exact:true}).click();await page.locator('#spot').fill('110');await ready();assert(Math.abs(await price()-17.662953740590453)<1e-6);
 await page.locator('#spot').fill('120');await page.locator('#spot').fill('100');await ready();assert(Math.abs(await price()-10.450583572185565)<1e-6);
 await page.locator('#volatility').fill('2');await ready();assert((await page.locator('#rangeNote').innerText()).includes('exceed'));assert.equal(await page.locator('#volatility').inputValue(),'2');
 await page.getByText('IV consistency check and diagnostics',{exact:true}).click();await page.locator('#volatility').fill('6');await ready();assert((await page.locator('#ivLog').innerText()).includes('bracketed'));
 await page.locator('#volatility').fill('.2');await page.locator('#expiry').fill('0');await page.waitForFunction(()=>document.querySelector('#status').textContent.includes('unavailable'));assert.equal(await price(),0);assert((await page.locator('#greeks').textContent()).includes('undefined'));
 await page.locator('#expiry').fill('1');await page.locator('#spot').fill('0');await page.waitForFunction(()=>document.querySelector('#status').textContent==='error');assert.equal(await page.locator('#price').innerText(),'—');
 await page.getByRole('button',{name:'Reset baseline',exact:true}).click();await ready();
 const download=page.waitForEvent('download');await page.getByRole('button',{name:'Download input and results JSON'}).click();const file=await download;const caseJson=JSON.parse(fs.readFileSync(await file.path(),'utf8'));assert.equal(caseJson.schema_version,1);assert.equal(caseJson.base.spot,100);assert(caseJson.attribution.residual!==undefined);
 assert(!(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)));assert.deepEqual(errors,[]);
 if(out)await page.screenshot({path:path.join(out,`deltacore-${width}-${colorScheme}.png`),fullPage:true});results.push({width,colorScheme,errors,reference:'passed',reset:'passed',independentRisk:'passed',diagnostics:'passed',download:'passed'});
 await context.close();}if(out)fs.writeFileSync(path.join(out,'browser-results.json'),JSON.stringify(results,null,2));console.log('DeltaCore: six layouts, reference prices, keyboard shocks, signed time, independent errors, range/expiry/IV diagnostics and JSON export passed.');}
 finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
