#!/usr/bin/env node
// 用实际浏览器检查成品状态与事件；自定义内容交互由工程提供断言。
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');
const crypto = require('crypto');

const args = process.argv.slice(2);
if (!args.length || args.includes('--help')) {
  console.log('verify-deck.cjs <deck.html> --out <directory> [--playwright-module <entry>] [--interaction-script <cjs/mjs>] [--browser-executable <path>]');
  process.exit(args.includes('--help') ? 0 : 1);
}
const source = path.resolve(args.shift());
const options = {};
while (args.length) {
  const key = args.shift();
  if (!['--out','--playwright-module','--interaction-script','--browser-executable'].includes(key) || !args.length)
    throw new Error(`参数无效：${key}`);
  options[key.slice(2)] = args.shift();
}
if (!options.out) throw new Error('请指定新的 --out 验收目录，保留历史结果。');
const out = path.resolve(options.out);
if (fs.existsSync(path.join(out, 'verification.json'))) throw new Error('已有验收记录，请使用新的 --out 目录。');
fs.mkdirSync(path.join(out, 'frames'), { recursive: true });
const report = {
  source, sha256: crypto.createHash('sha256').update(fs.readFileSync(source)).digest('hex'),
  checkedAt: new Date().toISOString(), viewport: {width:1280,height:720},
  status: 'running', scenes: [], frames: [], transitions: [], navigation: null,
  interaction: {status:'not-run'}, errors: [], warnings: [], externalRequests: [],
};

function resolvePlaywright() {
  if (options['playwright-module']) return require(path.resolve(options['playwright-module']));
  for (const name of ['playwright','playwright-core']) {
    try {return require(require.resolve(name, {paths:[process.cwd(),path.dirname(source),__dirname]}));} catch {}
  }
  throw new Error('未找到已有 Playwright。指定 --playwright-module 模块入口，或使用可用的等价浏览器工具完成检查。');
}
function check(condition, message) {if (!condition) throw new Error(message);}
const safeName = v => String(v).replace(/[^a-zA-Z0-9_-]/g, '_');

(async () => {
  let browser;
  try {
    const {chromium} = resolvePlaywright();
    if (options['browser-executable']) browser = await chromium.launch({headless:true,executablePath:path.resolve(options['browser-executable'])});
    else {
      try {browser = await chromium.launch({headless:true});}
      catch {browser = await chromium.launch({headless:true,channel:'chrome'});}
    }
    const page = await browser.newPage({viewport:report.viewport});
    page.on('pageerror',e=>report.errors.push(e.message));
    page.on('console',m=>{if(m.type()==='error')report.errors.push(m.text());else if(m.type()==='warning')report.warnings.push(m.text());});
    page.on('request',r=>{if(/^https?:/.test(r.url()))report.externalRequests.push(r.url());});
    await page.goto(pathToFileURL(source).href);
    await page.waitForFunction(()=>window.ready && window.__deck,undefined,{timeout:60000});
    const contract = await page.evaluate(()=>{
      const d=window.__deck;
      return {methods:['seek','transitionAt','info','advance','back','jump','setAuto'].filter(k=>typeof d[k]!=='function'),scenes:Array.isArray(d.scenes)&&d.scenes.length};
    });
    check(contract.scenes>0,'缺少可检查的场景。');
    check(contract.methods.length===0,`测试接口缺失：${contract.methods.join(', ')}`);
    report.scenes=await page.evaluate(()=>window.__deck.scenes.map(s=>({id:s.id,title:s.title,beats:s.beats.map(b=>({dur:b.dur,delay:b.delay||0,hold:b.hold||0}))})));
    for (let i=0;i<report.scenes.length;i++) {
      const scene=report.scenes[i];
      for (let beat=0;beat<scene.beats.length;beat++) {
        const b=scene.beats[beat],seconds=b.delay+b.dur+Math.min(1,b.hold);
        await page.evaluate(async x=>window.__deck.seek(x.scene,x.beat,x.seconds),{scene:scene.id,beat,seconds});
        const info=await page.evaluate(()=>window.__deck.info());
        check(info.scene===scene.id && info.beat===beat,`定位失败：${scene.id}/${beat}`);
        const file=`${String(i+1).padStart(2,'0')}-${safeName(scene.id)}-${beat+1}.png`;
        await page.screenshot({path:path.join(out,'frames',file)});
        report.frames.push({scene:scene.id,beat,seconds,path:`frames/${file}`});
      }
      console.log(`已检查 ${scene.id}，${scene.beats.length} 拍`);
      if (i>0) {
        await page.evaluate(async id=>window.__deck.transitionAt(id,.5),scene.id);
        const file=`transition-${safeName(scene.id)}.png`;
        await page.screenshot({path:path.join(out,'frames',file)});
        report.transitions.push({to:scene.id,progress:.5,path:`frames/${file}`});
      }
    }
    const nav=report.scenes.find(s=>s.beats.length>1);
    if (nav) {
      await page.evaluate(async id=>window.__deck.seek(id,0,0),nav.id);
      await page.keyboard.press('ArrowRight');
      const advanced=await page.evaluate(()=>window.__deck.info());
      check(advanced.scene===nav.id && advanced.beat===1,'右方向键未推进到下一拍。');
      await page.evaluate(()=>{const input=document.createElement('input');input.id='deck-verifier-input';document.body.append(input);input.focus();});
      await page.keyboard.press('ArrowRight');
      const editing=await page.evaluate(()=>window.__deck.info());
      check(editing.scene===advanced.scene && editing.beat===advanced.beat,'表单输入时快捷键抢占了方向键。');
      await page.evaluate(()=>{document.getElementById('deck-verifier-input').remove();document.getElementById('stage')?.focus();});
      await page.keyboard.press('ArrowLeft');
      const backed=await page.evaluate(()=>window.__deck.info());
      check(backed.scene===nav.id && backed.beat===0,'左方向键未返回上一拍。');
      report.navigation={passed:true,scene:nav.id,forward:advanced.beat,formFocusPreserved:true,back:backed.beat};
    } else report.navigation={passed:false,reason:'没有多拍场景，须人工核对导航。'};
    if (options['interaction-script']) {
      const modulePath=path.resolve(options['interaction-script']);
      const imported=await import(pathToFileURL(modulePath).href);
      const run=imported.default;
      check(typeof run==='function','交互脚本应导出 async function(page)。');
      const result=await run(page);
      check(result && result.passed===true,'自定义交互断言失败。');
      report.interaction={status:'passed',...result};
      await page.screenshot({path:path.join(out,'frames','interaction.png')});
    }
    await page.setViewportSize({width:390,height:844});
    await page.evaluate(async id=>window.__deck.seek(id,0,1),report.scenes[0].id);
    await page.screenshot({path:path.join(out,'frames','narrow.png')});
    report.narrow=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth}));
    check(report.narrow.scrollWidth<=report.narrow.width,'窄屏页面发生横向溢出。');
    check(report.errors.length===0,'存在页面脚本或控制台错误。');
    report.status=report.interaction.status==='passed' && report.navigation.passed?'passed':'partial';
    if(report.status==='partial')process.exitCode=2;
  } catch(error) {
    report.status='failed';report.errors.push(error.stack||String(error));
    process.exitCode=1;
  } finally {
    fs.writeFileSync(path.join(out,'verification.json'),JSON.stringify(report,null,2));
    if(browser)await browser.close();
    console.log(JSON.stringify({status:report.status,frames:report.frames.length,transitions:report.transitions.length,interaction:report.interaction.status,report:path.join(out,'verification.json')}));
  }
})();
