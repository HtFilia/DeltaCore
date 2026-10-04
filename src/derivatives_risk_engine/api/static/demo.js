const byId = id => document.getElementById(id);
const fmt = value => Number(value).toLocaleString(undefined, {maximumFractionDigits:6});
const defaults = {optionType:'call',spot:'100',strike:'100',expiry:'1',rate:'0.05',dividend:'0',volatility:'0.20',spotShock:'-5',volShock:'0',elapsedDays:'0'};
const presets = {spot:[-5,0,0],vol:[0,5,0],combined:[-5,5,0],time:[0,0,7],none:[0,0,0]};
let revision=0, active, timer, exported=null, riskRevision=0;
const text = (id,value) => byId(id).textContent=value;
async function postJson(path,payload,signal){
  const res=await fetch(path,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload),signal});
  const data=await res.json();
  if(!res.ok) throw new Error(typeof data.detail==='string'?data.detail:'Check finite inputs and supported ranges.');
  return data;
}
function basePayload(){
  const keys=['spot','strike','expiry','rate','dividend','volatility'];
  if(keys.some(k=>byId(k).value.trim()===''||!Number.isFinite(Number(byId(k).value))))throw new Error('Enter finite base inputs.');
  const b={option_type:byId('optionType').value,spot:Number(byId('spot').value),strike:Number(byId('strike').value),time_to_expiry:Number(byId('expiry').value),risk_free_rate:Number(byId('rate').value),dividend_yield:Number(byId('dividend').value),volatility:Number(byId('volatility').value)};
  if(b.spot<=0||b.strike<=0||b.time_to_expiry<0||b.volatility<=0)throw new Error('Spot, strike and volatility must be positive; expiry cannot be negative.');
  return b;
}
function shockPayload(b){
  const keys=['spotShock','volShock','elapsedDays'];
  if(keys.some(k=>byId(k).value.trim()===''||!Number.isFinite(Number(byId(k).value))))throw new Error('Enter finite shock inputs.');
  const pct=Number(byId('spotShock').value), vol=Number(byId('volShock').value), days=Number(byId('elapsedDays').value);
  if(pct < -99 || pct >100 || Math.abs(vol)>100 || days<0 || days>36500)throw new Error('Spot shock range: −99% to +100%; vol shock: ±100 points; elapsed days: 0 to 36500.');
  return {name:'Selected shock',spot_shift:b.spot*pct/100,volatility_shift:vol/100,elapsed_years:days/365};
}
function clearAttribution(){['shockedPrice','fullPnl','residual'].forEach(id=>text(id,'—'));byId('attributionRows').replaceChildren();byId('contributionChart').replaceChildren();text('explanation','Choose a supported shock to explain the move.');}
function drawCurve(points,b,result){
  const svg=byId('priceCurve');const width=Math.max(280,svg.clientWidth), min=points[0].shocked_spot,max=points.at(-1).shocked_spot;
  const maxY=Math.max(...points.map(p=>p.shocked_price),result?.shocked_price||0,0.01)*1.2;
  const x=v=>50+(v-min)/(max-min)*(width-75), y=v=>215-v/maxY*170;
  svg.setAttribute('viewBox',`0 0 ${width} 270`);
  const ns='http://www.w3.org/2000/svg';svg.replaceChildren();
  const add=(tag,attrs,label)=>{const el=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>el.setAttribute(k,String(v)));if(label)el.textContent=label;svg.append(el);};
  add('line',{x1:50,y1:25,x2:50,y2:215});add('line',{x1:50,y1:215,x2:width-25,y2:215});
  add('path',{d:points.map((p,i)=>`${i?'L':'M'}${x(p.shocked_spot)} ${y(p.shocked_price)}`).join(' ')});
  add('text',{x:5,y:18},'Price');add('text',{x:5,y:35},fmt(maxY));add('text',{x:20,y:217},'0');
  add('text',{x:50,y:240},fmt(min));add('text',{x:width-25,y:240,'text-anchor':'end'},fmt(max));add('text',{x:width/2,y:265,'text-anchor':'middle'},'Spot (currency units)');
  const basePrice=result?.base_price??Number(byId('price').textContent.replaceAll(',',''));
  add('circle',{cx:x(b.spot),cy:y(basePrice),r:5});add('text',{x:x(b.spot)+6,y:y(basePrice)-10},'Base');
  if(result){add('circle',{cx:x(result.shocked_spot),cy:y(result.shocked_price),r:5,style:'fill:#b23745'});add('text',{x:Math.min(width-50,x(result.shocked_spot)+6),y:y(result.shocked_price)+18},'Shocked');}
  byId('curveRows').replaceChildren();points.forEach(p=>{const tr=document.createElement('tr');[p.shocked_spot,p.shocked_price].forEach(v=>{const td=document.createElement('td');td.textContent=fmt(v);tr.append(td);});byId('curveRows').append(tr);});
}
function renderAttribution(r){
  text('shockedPrice',fmt(r.shocked_price));text('fullPnl',fmt(r.full_pnl));text('residual',fmt(r.residual));
  text('explanation',`Full repricing changes value by ${fmt(r.full_pnl)} currency units. The local approximation explains ${fmt(r.approximation)}; its residual is ${fmt(r.residual)}.`);
  const rows=[['Delta',r.spot_delta,'Δ × spot change'],['Gamma',r.spot_gamma,'½ Γ × spot change²'],['Vega',r.vol_vega,'Vega × absolute vol change'],['Theta',r.calendar_theta,'Theta × elapsed calendar years'],['Approximation',r.approximation,'Sum of the four contributions'],['Full repricing',r.full_pnl,'Shocked price − base price'],['Residual',r.residual,'Full repricing − approximation']];
  byId('attributionRows').replaceChildren();rows.forEach(row=>{const tr=document.createElement('tr');row.forEach((v,i)=>{const td=document.createElement('td');td.textContent=i===1?fmt(v):v;tr.append(td);});byId('attributionRows').append(tr);});
  const plot=rows.filter((_,i)=>i<4||i===6),max=Math.max(...plot.map(row=>Math.abs(row[1])),0.001);byId('contributionChart').replaceChildren();
  plot.forEach(([label,value])=>{const row=document.createElement('div');row.className='contribution';const name=document.createElement('span');name.textContent=label;const track=document.createElement('div');track.className='track';const fill=document.createElement('div');fill.className=`fill ${value<0?'loss':''}`;fill.style.width=`${Math.abs(value)/max*100}%`;track.append(fill);const amount=document.createElement('span');amount.textContent=fmt(value);row.append(name,track,amount);byId('contributionChart').append(row);});
}
async function runAnalytics(){
  clearTimeout(timer);active?.abort();active=new AbortController();const signal=active.signal,current=++revision;
  exported=null;byId('download').disabled=true;clearAttribution();text('status','running');text('log','');text('shockError','');text('price','—');text('impliedVol','—');byId('priceCurve').replaceChildren();
  try{
    const b=basePayload();
    let shock;try{shock=shockPayload(b);}catch(e){text('shockError',e.message);}
    const [price,greeks]=await Promise.all([postJson('/price/european',b,signal),b.time_to_expiry>0?postJson('/greeks/european',b,signal):Promise.resolve(null)]);
    if(current!==revision)return;
    text('price',fmt(price.price));text('greeks',greeks?Object.entries(greeks).filter(([k])=>['delta','gamma','vega','theta','rho'].includes(k)).map(([k,v])=>`${k}: ${fmt(v)}`).join(' · ')+' (delta/gamma per spot unit, vega/rho per absolute unit, theta per calendar year)':'Greeks undefined at expiry.');
    text('rangeNote',(b.spot<10||b.spot>200||b.volatility<0.01||b.volatility>1)?'Numeric inputs exceed the slider exploration range; calculations use the actual numeric values.':'');
    let result=null;
    if(shock){try{const data=await postJson('/risk/scenario-attribution',{...b,shocks:[shock]},signal);result=data[0];}catch(e){if(signal.aborted)throw e;text('shockError',e.message);}}
    if(current!==revision)return;
    if(result)renderAttribution(result);
    const min=Math.min(b.spot*.8,result?.shocked_spot??b.spot),max=Math.max(b.spot*1.2,result?.shocked_spot??b.spot);
    const curve=await postJson('/risk/scenario-pnl',{...b,shocks:Array.from({length:9},(_,i)=>({name:`Curve point ${i+1}`,spot_shift:min+(max-min)*i/8-b.spot}))},signal);
    if(current!==revision)return;drawCurve(curve.results,b,result);text('curveNote',min<b.spot*.8||max>b.spot*1.2?'Domain expanded to include the selected shock.':'Base domain: 80%–120% of base spot. Same-model repricing.');
    let iv=null,ivError=null;try{iv=await postJson('/implied-volatility',{option_type:b.option_type,spot:b.spot,strike:b.strike,time_to_expiry:b.time_to_expiry,risk_free_rate:b.risk_free_rate,dividend_yield:b.dividend_yield,target_price:price.price},signal);}catch(e){if(signal.aborted)throw e;ivError=e.message;}
    if(current!==revision)return;text('impliedVol',iv?.implied_volatility==null?'n/a':fmt(iv.implied_volatility));text('ivLog',ivError?`Consistency service unavailable: ${ivError}. Solver diagnostics unavailable.`:`${iv.diagnostics.failure_reason||'Converged'} · residual ${fmt(iv.diagnostics.objective_value)} · ${iv.diagnostics.iterations} iterations · vol bounds ${iv.diagnostics.lower_bound} to ${iv.diagnostics.upper_bound}`);
    exported={schema_version:1,case_version:'option-risk-v1',engine_revision:byId('revision').textContent,units:'One option; currency-unit prices; annual continuous rates/lognormal vol; elapsed calendar years = days/365',base:b,shock:shock??null,pricing:price,greeks,attribution:result,curve:curve.results,iv_consistency:iv,iv_error:ivError,evidence_categories:['Independent reference fixtures (linked tests)','Finite-difference checks (linked tests)','Internal same-model repricing/IV agreement']};
    byId('download').disabled=false;text('status',result?'ready':'Price ready; attribution unavailable');
  }catch(e){if(current!==revision||signal.aborted)return;text('status','error');text('log',e.message);}
}
function schedule(){++revision;active?.abort();exported=null;byId('download').disabled=true;text('status','updating');text('price','—');text('impliedVol','—');text('ivLog','Updating consistency check…');text('greeks','Updating…');byId('priceCurve').replaceChildren();clearAttribution();clearTimeout(timer);timer=setTimeout(runAnalytics,200);}
async function runRisk(){const current=++riskRevision;text('varEs','—');text('riskLog','');try{const values=byId('pnls').value.split(/[\s,]+/).filter(Boolean).map(Number),confidence=Number(byId('confidence').value);if(values.length<2||values.some(v=>!Number.isFinite(v))||!Number.isFinite(confidence)||confidence<=0||confidence>=1)throw new Error('Historical sample: provide at least two finite P&Ls and confidence between 0 and 1.');const r=await postJson('/risk/historical-var',{pnls:values,confidence_level:confidence});if(current!==riskRevision)return;text('varEs',`${fmt(r.value_at_risk)} / ${fmt(r.expected_shortfall)} (VaR / ES)`);text('riskLog',`${r.num_observations} supplied observations; ${r.tail_observations} losses at/beyond quantile index ${r.quantile_index}.`);}catch(e){if(current===riskRevision)text('riskLog',e.message);}}
document.querySelectorAll('.controls input,.controls select').forEach(el=>el.addEventListener('input',()=>{if(el.id==='spotSlider')byId('spot').value=el.value;if(el.id==='volSlider')byId('volatility').value=el.value;if(el.id==='spot')byId('spotSlider').value=el.value;if(el.id==='volatility')byId('volSlider').value=el.value;schedule();}));
document.querySelectorAll('[data-preset]').forEach(btn=>btn.addEventListener('click',()=>{const values=presets[btn.dataset.preset];['spotShock','volShock','elapsedDays'].forEach((id,i)=>byId(id).value=values[i]);schedule();}));
byId('reset').addEventListener('click',()=>{Object.entries(defaults).forEach(([id,v])=>byId(id).value=v);byId('spotSlider').value=100;byId('volSlider').value=.2;schedule();});byId('runButton').addEventListener('click',runAnalytics);
['pnls','confidence'].forEach(id=>byId(id).addEventListener('input',runRisk));
byId('download').addEventListener('click',()=>{if(!exported)return;const url=URL.createObjectURL(new Blob([JSON.stringify(exported,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='deltacore-option-risk.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
fetch('/demo-meta').then(r=>r.json()).then(m=>text('revision',m.revision)).catch(()=>{});runAnalytics();runRisk();

window.addEventListener('resize',()=>{if(exported)drawCurve(exported.curve,exported.base,exported.attribution);});
