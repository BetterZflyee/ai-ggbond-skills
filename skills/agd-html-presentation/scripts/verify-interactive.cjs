#!/usr/bin/env node
// Runtime verification for an interaction-first standalone HTML presentation.
const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
const argv=process.argv.slice(2),file=argv.shift();
if(!file){console.error('用法：verify-interactive.cjs <HTML> --out <新目录> [--starter | --interaction-script <cjs>] [--audio-check-script <cjs> | --silent-reason <用户明确要求静音的原因>] [--playwright-module <path>]');process.exit(1);}
function arg(key){const i=argv.indexOf(key);return i<0?null:argv[i+1];}
const out=path.resolve(arg('--out')||'interactive-verification'),starter=argv.includes('--starter'),custom=arg('--interaction-script'),audioCustom=arg('--audio-check-script'),silentReason=arg('--silent-reason');
if(silentReason&&(starter||audioCustom)){console.error('--silent-reason 仅用于用户明确要求的静音作品，不能与默认有声起点或声音检查一起使用。');process.exit(1);}
if(fs.existsSync(out)){console.error('验收目录已存在，请选择新目录。');process.exit(1);}fs.mkdirSync(out,{recursive:true});
const report={file:path.resolve(file),scope:starter?'default starter runtime smoke test':'custom presentation runtime verification',checks:[],errors:[],console:[],screenshots:[],reviewBoundary:'Runtime, actual input, output waveform and generated samples only; this report does not certify scene semantics, visual review or subjective listening.'};let browser;
function check(name,pass,details){report.checks.push({name,pass:!!pass,details});if(!pass)throw Error(name);}
function save(){fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));}
function observe(page){page.on('pageerror',e=>report.errors.push(e.message));page.on('console',m=>{if(['warning','error'].includes(m.type()))report.console.push({type:m.type(),text:m.text()});});}
// Playwright evaluation may grant a synthetic activation. A cold page is observed
// with CDP userGesture:false until its first actual pointer/key action.
async function coldState(cdp){const r=await cdp.send('Runtime.evaluate',{expression:'window.__presentation?.ready ? window.__presentation.getState() : null',userGesture:false,returnByValue:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result.value;}
async function waitColdReady(page,cdp){const until=Date.now()+30000;while(Date.now()<until){const s=await coldState(cdp);if(s)return s;await page.waitForTimeout(60);}throw Error('cold starter did not become ready');}
async function audible(page){await page.waitForFunction(()=>{const a=window.__presentation.getState().audio;return a?.unlocked&&a.contextState==='running'&&Number.isFinite(a.liveRms)&&a.liveRms>0.00001;},undefined,{timeout:7000});return page.evaluate(()=>window.__presentation.getState().audio);}
async function quiet(page){await page.waitForTimeout(180);const a=await page.evaluate(()=>window.__presentation.getState().audio);check('post-master mute is silent',a.muted&&a.liveRms===0&&a.livePeak===0,a);return a;}
async function runCustom(script,page){const run=require(path.resolve(script));return (typeof run==='function'?run:run.check)(page);}
(async()=>{
 const modulePath=arg('--playwright-module')||require.resolve('playwright',{paths:[process.cwd(),path.dirname(path.resolve(file))]});
 const {chromium}=require(modulePath);browser=await chromium.launch({channel:'chrome',headless:true});
 const page=await browser.newPage({viewport:{width:1280,height:720}});
 observe(page);
 await page.goto(pathToFileURL(path.resolve(file)).href);await page.waitForFunction(()=>window.__presentation?.ready,undefined,{timeout:30000});
 const initial=await page.evaluate(()=>window.__presentation.getState());check('standalone HTML ready',initial.ready&&!initial.error,initial);
 check('interaction protocol',await page.evaluate(()=>['next','previous','goTo','getState'].every(k=>typeof window.__presentation[k]==='function')));
 check('scene count',Number.isInteger(initial.beatCount)&&initial.beatCount>=2,initial.beatCount);
 await page.waitForTimeout(1500);const hold=await page.evaluate(()=>window.__presentation.getState());check('scene remains under user control',hold.targetBeat===initial.targetBeat&&!hold.moving,{before:initial.targetBeat,after:hold.targetBeat});
 for(let i=0;i<initial.beatCount;i++){
  await page.evaluate(i=>window.__presentation.goTo(i),i);await page.waitForFunction(i=>{const s=window.__presentation.getState();return !s.moving&&s.beat===i;},i,{timeout:10000});
  const state=await page.evaluate(()=>window.__presentation.getState());check('scene '+i+' settles',state.beat===i&&state.glError===0,state);const shot=`scene-${i}.png`;await page.screenshot({path:path.join(out,shot)});report.screenshots.push(shot);
 }
 await page.evaluate(()=>window.__presentation.goTo(0,{immediate:true}));await page.evaluate(()=>window.__presentation.next());await page.waitForTimeout(250);
 const mid=await page.evaluate(()=>window.__presentation.getState());check('transition has intermediate state',mid.reducedMotion||mid.moving&&mid.transition>0&&mid.transition<1,mid);
 await page.screenshot({path:path.join(out,'transition.png')});await page.waitForFunction(()=>!window.__presentation.getState().moving);
 await page.evaluate(()=>window.__presentation.previous());await page.waitForFunction(()=>!window.__presentation.getState().moving);check('previous returns',await page.evaluate(()=>window.__presentation.getState().beat===0));
 if(starter){
  const p=await browser.newPage({viewport:{width:1280,height:720},reducedMotion:'reduce'});observe(p);const cdp=await p.context().newCDPSession(p);await p.goto(pathToFileURL(path.resolve(file)).href);const cold=await waitColdReady(p,cdp);
  check('first frame is ready without sound permission',cold.ready&&cold.audio&&!cold.audio.unlocked&&cold.audio.liveRms===0,cold.audio);
  const coldActivation=await cdp.send('Runtime.evaluate',{expression:'({active:navigator.userActivation.isActive,sticky:navigator.userActivation.hasBeenActive})',userGesture:false,returnByValue:true});
  check('cold sound observation has no synthetic activation',!coldActivation.result.value.active&&!coldActivation.result.value.sticky,coldActivation.result.value);
  const lightBefore=await coldState(cdp),pixelsBefore=await p.screenshot(),sun=lightBefore.contentTargets.sun;check('rendered sun is directly hittable',sun.visible,sun);
  await p.mouse.move(sun.x,sun.y);await p.mouse.down();await p.mouse.move(sun.x,sun.y-110,{steps:12});await p.mouse.up();await p.waitForTimeout(80);
  const lightAfter=await p.evaluate(()=>window.__presentation.getState()),pixelsAfter=await p.screenshot();check('real sun drag changes material rendering',lightAfter.light>lightBefore.light+.2&&lightAfter.lightOwner==='user'&&!pixelsBefore.equals(pixelsAfter)&&lightAfter.targetBeat===0,{before:lightBefore.light,after:lightAfter.light});
  const pointerAudio=await audible(p);check('first real pointer drag enables actual sound',pointerAudio.livePeak>0&&pointerAudio.active,pointerAudio);
  check('content input reaches sound state',Math.abs(pointerAudio.input.light-lightAfter.light)<.001,{visual:lightAfter.light,audio:pointerAudio.input});
  check('content light changes the sound filter',Math.abs(pointerAudio.parameters['light:sea:cutoff']-(800+3400*lightAfter.light))<.01,pointerAudio.parameters);
  check('no navigation prompts or numeric HUD in default',await p.locator('nav,button,input,output,#hint,#dots,#count,#steps,#light-handle').count()===0);
  check('no instructional text in default',!(/拖动|滚轮|方向键|单击|点击|上一步|下一步/.test(await p.locator('body').innerText())));
  const start=await p.evaluate(()=>window.__presentation.getState()),before=await p.screenshot();await p.mouse.move(720,430);await p.mouse.down();await p.mouse.move(940,350,{steps:12});await p.mouse.up();await p.waitForTimeout(80);
  const orbit=await p.evaluate(()=>window.__presentation.getState()),after=await p.screenshot();check('real drag changes camera and rendered image',Math.abs(orbit.orbit.x-start.orbit.x)>.1&&orbit.cameraOwner==='user'&&!orbit.pointerActive&&!before.equals(after)&&orbit.targetBeat===0,{before:start.orbit,after:orbit.orbit});
  await p.waitForTimeout(600);const release=await p.evaluate(()=>window.__presentation.getState());check('release preserves user choices',Math.abs(release.light-lightAfter.light)<.001&&Math.abs(release.orbit.x-orbit.orbit.x)<.001,release);
  await p.mouse.click(720,430);check('short canvas click advances',await p.evaluate(()=>window.__presentation.getState().beat===1));check('canvas keeps keyboard focus',await p.locator('canvas').evaluate(e=>document.activeElement===e));await p.mouse.wheel(0,650);await p.waitForTimeout(80);check('wheel navigation',await p.evaluate(()=>window.__presentation.getState().beat===2));
  await p.keyboard.press('ArrowLeft');check('keyboard navigation',await p.evaluate(()=>window.__presentation.getState().beat===1));await p.mouse.click(720,430,{button:'right'});check('right click returns',await p.evaluate(()=>window.__presentation.getState().beat===0));
  for(const [width,height] of [[390,844],[320,568]]){await p.setViewportSize({width,height});await p.waitForTimeout(80);check('narrow screen '+width,await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await p.screenshot({path:path.join(out,`mobile-${width}.png`)});}
  check('no player or audio controls in default',await p.locator('#play,#pause,#mute,#scrub').count()===0);
  const muteBeat=await p.evaluate(()=>window.__presentation.getState().targetBeat);await p.keyboard.press('m');await quiet(p);await p.keyboard.press('m');const restored=await audible(p);check('M restores actual output',!restored.muted&&restored.livePeak>0,restored);
  check('mute key preserves narrative progress',await p.evaluate(()=>window.__presentation.getState().targetBeat)===muteBeat);
  check('internal audio inspection API',await p.evaluate(()=>['setMuted','renderAudioOffline'].every(k=>typeof window.__presentation[k]==='function')));
  await p.evaluate(()=>window.__presentation.setMuted(true));await quiet(p);await p.evaluate(()=>window.__presentation.setMuted(false));await audible(p);
  const offline=await p.evaluate(async()=>{
   const api=window.__presentation,spec={seconds:1.4,sampleRate:24000};
   const sea=await api.renderAudioOffline({...spec,scene:'sea',input:{light:.12}}),bright=await api.renderAudioOffline({...spec,scene:'sea',input:{light:.9}}),stone=await api.renderAudioOffline({...spec,scene:'stone',input:{light:.9}}),muted=await api.renderAudioOffline({...spec,scene:'sea',input:{light:.9},muted:true});
   const stats=a=>{let finite=true,peak=0,power=0,difference=0,n=a.channels[0].length;for(let c=0;c<a.channels.length;c++)for(const v of a.channels[c]){finite=finite&&Number.isFinite(v);peak=Math.max(peak,Math.abs(v));power+=v*v;}for(let i=0;i<n;i++)difference+=Math.abs(a.channels[0][i]-a.channels[1][i]);return {channels:a.channels.length,sampleRate:a.sampleRate,frames:n,finite,peak,rms:Math.sqrt(power/(n*a.channels.length)),stereoDifference:difference/n,sameSourceGraph:a.sameSourceGraph===true};};
   const delta=(a,b)=>{let d=0;for(let i=0;i<a.channels[0].length;i++)d+=Math.abs(a.channels[0][i]-b.channels[0][i]);return d/a.channels[0].length;};
   return {sea:stats(sea),bright:stats(bright),stone:stats(stone),muted:stats(muted),inputDifference:delta(sea,bright),sceneDifference:delta(bright,stone)};
  });
  check('same-source stereo sound renders with finite nonzero PCM',Object.values(offline).filter(v=>v&&typeof v==='object'&&v!==offline.muted).every(v=>v.sameSourceGraph&&v.channels===2&&v.frames>0&&v.finite&&v.rms>0.00001&&v.peak<1&&v.stereoDifference>0.000001),offline);
  check('content and scene change generated sound',offline.inputDifference>0.00001&&offline.sceneDifference>0.00001,offline);
  check('same-source offline mute is silent',offline.muted.finite&&offline.muted.rms===0&&offline.muted.peak===0,offline.muted);
  report.audio={passed:true,pointerOutput:pointerAudio,restoredOutput:restored,offline,activation:'Fresh context observed with CDP userGesture:false before actual pointerdown; no autoplay bypass flags. Wheel alone was not used to claim playback permission.',listeningReview:'Not performed by this runtime test.'};
  check('pointer page has no audio error',!await p.evaluate(()=>window.__presentation.getState().audioError));await p.close();report.contentInteraction={passed:true,method:'real pointer camera and rendered-sun manipulation, reduced motion freezes ambient animation to isolate image differences'};
  // The normal-motion page verifies scene-weight handoff and event cleanup.
  await page.keyboard.press('ArrowRight');const keyAudio=await audible(page);check('real key enables actual sound',keyAudio.livePeak>0,keyAudio);
  await page.evaluate(()=>window.__presentation.goTo(0,{immediate:true}));await page.waitForTimeout(150);
  const seaAudio=await page.evaluate(()=>window.__presentation.getState().audio);
  await page.evaluate(()=>window.__presentation.goTo(window.__presentation.getState().beatCount-1));
  await page.waitForFunction(()=>{const a=window.__presentation.getState().audio;return a.sceneWeights[0]>.05&&a.sceneWeights[1]>.05;},undefined,{timeout:5000});
  const bridge=await page.evaluate(()=>window.__presentation.getState());
  const blendRaw=Math.max(0,Math.min(1,(bridge.storyTime-18)/8)),blend=blendRaw*blendRaw*(3-2*blendRaw),expectedWeights=[Math.cos(blend*Math.PI/2),Math.sin(blend*Math.PI/2)];
  check('sound worlds follow the rendered visual mix',bridge.moving&&bridge.audio.sceneWeights.every((v,i)=>Number.isFinite(v)&&Math.abs(v-expectedWeights[i])<.00001)&&bridge.audio.motionProgress>0&&bridge.audio.motionProgress<1,{storyTime:bridge.storyTime,expectedWeights,audio:bridge.audio});
  await page.waitForFunction(()=>!window.__presentation.getState().moving);const stoneAudio=await page.evaluate(()=>window.__presentation.getState().audio);
  check('scene weights follow completed visual world',seaAudio.scene==='sea'&&stoneAudio.scene==='stone'&&seaAudio.sceneWeights[0]>.99&&stoneAudio.sceneWeights[1]>.99,{sea:seaAudio,stone:stoneAudio});
  await page.evaluate(()=>window.__presentation.goTo(0));await page.waitForTimeout(160);const reverse=await page.evaluate(()=>window.__presentation.getState().audio);check('return changes audio direction',reverse.reverse===true,reverse);
  for(let i=0;i<8;i++){await page.evaluate(i=>window.__presentation.goTo(i%2?0:3),i);await page.waitForTimeout(45);}
  await page.waitForFunction(()=>!window.__presentation.getState().moving);await page.waitForTimeout(500);const rapid=await page.evaluate(()=>window.__presentation.getState().audio);check('rapid changes retain bounded transient voices',Number.isFinite(rapid.activeTransientCount)&&rapid.activeTransientCount<=8&&rapid.liveRms>0&&rapid.livePeak<1,rapid);
  const perMotion={};for(const e of rapid.soundEvents)if(e.motionId!=null)perMotion[e.motionId]=(perMotion[e.motionId]||0)+1;check('motion sounds are emitted once per identity',Object.keys(perMotion).length>=8&&Object.values(perMotion).every(n=>n===1),perMotion);
  report.audio.sceneTransition={sea:seaAudio,mid:bridge.audio,stone:stoneAudio,reverse,rapid};
  const hiddenStart=await page.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'));return window.__presentation.getState();});
  await page.waitForTimeout(200);const hidden=await page.evaluate(()=>window.__presentation.getState());
  check('hidden signal silences output and freezes environment',!hidden.audio.active&&hidden.audio.liveRms===0&&hidden.audio.livePeak===0&&hidden.environmentTime===hiddenStart.environmentTime,hidden);
  await page.evaluate(()=>{delete document.hidden;document.dispatchEvent(new Event('visibilitychange'));});await page.waitForTimeout(200);await audible(page);const shown=await page.evaluate(()=>window.__presentation.getState());
  check('shown signal restores sound and advances environment',shown.audio.active&&shown.audio.liveRms>0&&shown.environmentTime>hidden.environmentTime,{hiddenTime:hidden.environmentTime,shownTime:shown.environmentTime,audio:shown.audio});
  report.audio.background={scope:'Production visibilitychange handler exercised by a temporary document.hidden getter and dispatched event; not an OS tab visibility test.',hidden,shown};
  check('normal-motion page has no audio error',!shown.audioError);
 }else if(custom){report.contentInteraction=await runCustom(custom,page);check('custom real content interaction',report.contentInteraction?.passed,report.contentInteraction);}
 if(!starter){
  if(audioCustom){report.audio=await runCustom(audioCustom,page);check('custom actual audio output verification',report.audio?.passed,report.audio);}
  else if(silentReason){report.audio={passed:true,skipped:true,reason:silentReason,scope:'User explicitly requested a silent work; this is not a browser-permission workaround.'};}
  else report.audio={passed:false,missing:'Provide --audio-check-script for scene/action/transition sound, post-master nonzero/mute/restore and cleanup checks; use --silent-reason only for an explicitly silent request.'};
 }
 check('page errors',report.errors.length===0,report.errors);check('console errors',report.console.every(x=>x.type!=='error'),report.console);
 report.status=report.contentInteraction?.passed&&report.audio?.passed?'passed':'partial';report.completed=new Date().toISOString();save();console.log(JSON.stringify({status:report.status,scope:report.scope,checks:report.checks.length,output:out}));if(report.status==='partial')process.exitCode=2;
})().catch(e=>{report.status='failed';report.fatal=e.stack||String(e);save();console.error(e);process.exitCode=1;}).finally(async()=>{if(browser)await browser.close();});
