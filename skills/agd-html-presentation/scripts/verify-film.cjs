#!/usr/bin/env node
// 动画/程序素材工程检查。数值验证不替代连续画面审看与实际听审。
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {pathToFileURL}=require('url');
const args=process.argv.slice(2);
if(!args.length||args.includes('--help')){
  console.log('verify-film.cjs <film.html> --out <directory> --interaction-script <cjs/mjs> [--playwright-module <entry>] [--play-seconds <seconds>]');
  process.exit(args.includes('--help')?0:1);
}
const source=path.resolve(args.shift()),options={};
while(args.length){const key=args.shift();if(!['--out','--interaction-script','--playwright-module','--play-seconds'].includes(key)||!args.length)throw new Error(`参数无效：${key}`);options[key.slice(2)]=args.shift();}
if(!options.out)throw new Error('请提供新的 --out 验收目录。');
const out=path.resolve(options.out);
if(fs.existsSync(path.join(out,'verification.json')))throw new Error('已有验收记录，请另选目录。');
fs.mkdirSync(path.join(out,'frames'),{recursive:true});
const report={source,sha256:crypto.createHash('sha256').update(fs.readFileSync(source)).digest('hex'),checkedAt:new Date().toISOString(),status:'running',frames:[],webgl:null,playback:null,audio:null,interaction:{status:'not-run'},errors:[],warnings:[],externalRequests:[]};
const assert=(v,m)=>{if(!v)throw new Error(m);};
function playwright(){if(options['playwright-module'])return require(path.resolve(options['playwright-module']));for(const name of ['playwright','playwright-core'])try{return require(require.resolve(name,{paths:[process.cwd(),path.dirname(source),__dirname]}));}catch{}throw new Error('未找到已有Playwright，请指定 --playwright-module。');}
(async()=>{
  let browser;
  try{
    const {chromium}=playwright();try{browser=await chromium.launch({headless:true});}catch{browser=await chromium.launch({headless:true,channel:'chrome'});}
    const page=await browser.newPage({viewport:{width:1280,height:720}});
    page.on('pageerror',e=>report.errors.push(e.message));
    page.on('console',m=>{if(m.type()==='error')report.errors.push(m.text());else if(m.type()==='warning')report.warnings.push(m.text());});
    page.on('request',r=>{if(/^https?:/.test(r.url()))report.externalRequests.push(r.url());});
    await page.goto(pathToFileURL(source).href);
    await page.waitForFunction(()=>{const f=window.__film||window.__lab;return f&&(f.ready||window.ready);},undefined,{timeout:60000});
    const meta=await page.evaluate(()=>{const f=window.__film||window.__lab;return{duration:f.duration,missing:['seek','play','pause','getState','renderAudioOffline'].filter(k=>typeof f[k]!=='function')};});
    assert(Number.isFinite(meta.duration)&&meta.duration>0,'缺少有效 duration 秒数。');
    assert(!meta.missing.length,`缺少动画验收接口：${meta.missing.join(', ')}`);
    report.duration=meta.duration;
    report.webgl=await page.evaluate(()=>{for(const c of document.querySelectorAll('canvas')){const g=c.getContext('webgl2');if(g)return{version:g.getParameter(g.VERSION),renderer:g.getParameter(g.RENDERER),width:c.width,height:c.height};}return null;});
    assert(report.webgl,'未检测到 WebGL2 主舞台；本验收器用于实时图形动画。');
    const times=[0,.16,.33,.5,.66,.82,1].map(p=>p*meta.duration);
    for(let i=0;i<times.length;i++){
      const state=await page.evaluate(async t=>{const f=window.__film||window.__lab;await f.seek(t);return f.getState();},times[i]);
      if(Number.isFinite(state.glError))assert(state.glError===0,`时间 ${times[i]} 存在WebGL错误 ${state.glError}`);
      const file=`${String(i+1).padStart(2,'0')}-${times[i].toFixed(2)}s.png`;
      await page.screenshot({path:path.join(out,'frames',file)});
      report.frames.push({time:times[i],state,path:`frames/${file}`});
    }
    const unique=new Set(report.frames.map(f=>crypto.createHash('sha256').update(fs.readFileSync(path.join(out,f.path))).digest('hex')));
    assert(unique.size>=3,'不同时间点未呈现足够画面变化。');
    if(options['interaction-script']){
      const mod=await import(pathToFileURL(path.resolve(options['interaction-script'])).href);
      assert(typeof mod.default==='function','交互脚本应导出 async function(page)。');
      const result=await mod.default(page);assert(result?.passed===true,'内容交互断言失败。');
      report.interaction={status:'passed',...result};
    }
    report.audio=await page.evaluate(async()=>{
      const f=window.__film||window.__lab,result=await f.renderAudioOffline(2,24000);
      let channels,sampleRate;
      if(result&&typeof result.getChannelData==='function'){channels=Array.from({length:result.numberOfChannels},(_,i)=>result.getChannelData(i));sampleRate=result.sampleRate;}
      else if(result?.channels){channels=result.channels;sampleRate=result.sampleRate;}
      else throw new Error('离线音频须返回 AudioBuffer 或 {channels:[Float32Array],sampleRate}。');
      let sum=0,peak=0,nonzero=0,count=0;
      for(const channel of channels)for(const sample of channel){if(!Number.isFinite(sample))throw new Error('音频包含非有限采样');sum+=sample*sample;peak=Math.max(peak,Math.abs(sample));if(Math.abs(sample)>1e-7)nonzero++;count++;}
      return{channels:channels.length,sampleRate,samples:count,rms:Math.sqrt(sum/Math.max(1,count)),peak,nonzero,subjectiveListening:'not-performed'};
    });
    assert(report.audio.samples>0&&report.audio.rms>1e-6,'离线音频为空或静音。');
    assert(report.audio.peak<=1.0001,'离线音频超过标准满幅，需要检查增益或限幅。');
    const playSeconds=options['play-seconds']===undefined?Math.min(meta.duration,45):Math.min(meta.duration,Number(options['play-seconds']));
    assert(Number.isFinite(playSeconds)&&playSeconds>0,'play-seconds须为正数。');
    await page.evaluate(()=>{const f=window.__film||window.__lab;f.seek(0);f.pause();});
    // 先给真实用户手势，再明确启动时间线。
    await page.mouse.click(640,360);
    await page.evaluate(async()=>{const f=window.__film||window.__lab;await f.seek(0);await f.play();});
    const began=Date.now();
    console.log(`开始连续播放检查，${playSeconds.toFixed(1)} 秒`);
    await page.waitForTimeout((playSeconds+.3)*1000);
    report.playback=await page.evaluate(()=>{const f=window.__film||window.__lab;f.pause();return f.getState();});
    report.playback={...report.playback,wallSeconds:(Date.now()-began)/1000,requestedSeconds:playSeconds,wholeDurationRequested:playSeconds>=meta.duration};
    const observedTime=report.playback.time;
    if(Number.isFinite(report.playback.glError))assert(report.playback.glError===0,'连续播放出现WebGL错误。');
    assert(Number.isFinite(observedTime)&&observedTime>=playSeconds*.85,'连续播放的实际时间推进不足。');
    await page.setViewportSize({width:390,height:844});
    await page.evaluate(()=>{const f=window.__film||window.__lab;f.seek(f.duration*.5);});
    await page.screenshot({path:path.join(out,'frames','narrow.png')});
    report.narrow=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth}));
    assert(report.narrow.scrollWidth<=report.narrow.width,'窄屏出现横向溢出。');
    assert(!report.errors.length,'出现脚本、着色器或控制台错误。');
    report.status=report.interaction.status==='passed'?'passed':'partial';
    if(report.status==='partial')process.exitCode=2;
  }catch(error){report.status='failed';report.errors.push(error.stack||String(error));process.exitCode=1;}
  finally{fs.writeFileSync(path.join(out,'verification.json'),JSON.stringify(report,null,2));if(browser)await browser.close();console.log(JSON.stringify({status:report.status,frames:report.frames.length,audio:report.audio,report:path.join(out,'verification.json')}));}
})();
