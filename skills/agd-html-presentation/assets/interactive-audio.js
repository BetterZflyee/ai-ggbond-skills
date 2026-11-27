/** Configurable state-driven sound. Original procedural PCM, no fixed-duration soundtrack. */
(()=>{'use strict';
const SR=24000,TAU=Math.PI*2;
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,Number(x)||0));
const smooth=x=>{x=clamp(x);return x*x*(3-2*x);};
const lerp=(a,b,p)=>a+(b-a)*p;
function random(seed){let x=seed>>>0;return()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return(x>>>0)/4294967296;};}
function createSources(){
  const cache=new Map(),wave=new Float32Array(8192);
  for(let i=0;i<wave.length;i++)wave[i]=Math.sin(TAU*i/wave.length);
  const sine=p=>{let x=(p-Math.floor(p))*wave.length,k=Math.floor(x);return lerp(wave[k],wave[(k+1)%wave.length],x-k);};
  function noise(){
    if(cache.has('noise'))return cache.get('noise');
    const n=SR*4,join=Math.floor(SR*.08),channels=[];
    for(let ch=0;ch<2;ch++){
      const r=random(63937+ch*7919),raw=new Float32Array(n+join);let a=0,b=0,c=0;
      for(let i=0;i<raw.length;i++){const w=r()*2-1;a=.99765*a+.099046*w;b=.963*b+.2965164*w;c=.57*c+1.0526913*w;raw[i]=(a+b+c+w*.1848)*.18;}
      const data=raw.slice(0,n);for(let i=0;i<join;i++)data[i]=lerp(raw[n+i],raw[i],smooth(i/join));channels.push(data);
    }
    const out={channels,sampleRate:SR,duration:n/SR};cache.set('noise',out);return out;
  }
  function asset(kind,variant=0,reverse=false){
    const key=kind+'.'+variant+(reverse?'.reverse':'');if(cache.has(key))return cache.get(key);
    if(reverse){const a=asset(kind,variant);const out={...a,peakOffset:a.duration-a.peakOffset,channels:a.channels.map(x=>x.slice().reverse())};cache.set(key,out);return out;}
    const durations={paper:.58,tape:1.12,scan:.22,clack:.17,knock:.43,servo:.55,glass:1.8,particle:.72,pulse:.5,air:1.7,impact:1.15,latch:.28};
    const duration=durations[kind]||.5,n=Math.ceil(duration*SR),r=random(18277+kind.charCodeAt(0)*137+variant*317),data=new Float32Array(n);let low=0,slow=0,phase=0;
    for(let i=0;i<n;i++){
      const t=i/SR,u=t/duration,w=r()*2-1;low+=.24*(w-low);slow+=.018*(w-slow);let v=0;
      if(kind==='paper'||kind==='tape'){const grain=.3+.7*(.5+.5*sine(t*(kind==='tape'?29:17)+variant))**3,env=Math.sin(Math.PI*u)**1.2;v=((low-slow)*grain*1.5+slow*.5)*env;}
      else if(kind==='scan'){phase+=(1000+650*u)/SR;v=.23*sine(phase)*Math.exp(-Math.pow((t-.035)/.023,2))+.16*sine(t*1510)*Math.exp(-Math.pow((t-.115)/.025,2))+.04*(w-low)*Math.exp(-t*50);}
      else if(['clack','knock','latch'].includes(kind)){const f=kind==='clack'?340:kind==='knock'?145:710;v=.43*sine(t*f)*Math.exp(-t*25)+.2*sine(t*f*2.61)*Math.exp(-t*50)+.24*low*Math.exp(-t*95);}
      else if(kind==='servo'){phase+=(175+600*smooth(u))/SR;v=(.18*sine(phase)+.07*sine(phase*2.03)+.2*low)*Math.sin(Math.PI*u)**1.5;}
      else if(kind==='glass'||kind==='particle'){const f=(kind==='glass'?587.33:440)*(1+variant*.003);v=.28*sine(t*f)*Math.exp(-t*3.1)+.13*sine(t*f*2.756)*Math.exp(-t*5.8)+.06*sine(t*f*4.07)*Math.exp(-t*9)+.025*low*Math.exp(-t*80);}
      else if(kind==='pulse'){v=.42*sine(t*73.416)*Math.exp(-t*11)+.11*sine(t*146.83)*Math.exp(-t*16)+.045*low*Math.exp(-t*42);}
      else if(kind==='air'){const env=Math.sin(Math.PI*u)**2;v=((low-slow)*(.6+u)+slow*1.35)*env+.025*sine(t*(52+18*u))*env;}
      else if(kind==='impact'){phase+=(39+65*Math.exp(-t*25))/SR;v=.42*sine(phase)*Math.exp(-t*5)+.12*sine(t*78)*Math.exp(-t*9)+.14*low*Math.exp(-t*35);}
      data[i]=v*smooth(t/.004)*smooth((duration-t)/.045);
    }
    let peakAt=0,peak=0;for(let i=0;i<data.length;i++)if(Math.abs(data[i])>peak){peak=Math.abs(data[i]);peakAt=i/SR;}const out={channels:[data],sampleRate:SR,duration,peakOffset:peakAt};cache.set(key,out);return out;
  }
  function ir(){if(cache.has('ir'))return cache.get('ir');const duration=1.18,n=Math.ceil(SR*duration),channels=[];for(let ch=0;ch<2;ch++){const r=random(9217+ch*91),data=new Float32Array(n);let lp=0;for(let i=0;i<n;i++){const t=i/SR;lp+=.33*(r()*2-1-lp);data[i]=lp*Math.exp(-t*5.4)*smooth((t-.016)/.015)*.23;}for(const[t,g]of[[.027,.12],[.052,-.075],[.088,.05]])data[Math.floor((t+ch*.003)*SR)]+=g;channels.push(data);}const out={channels,sampleRate:SR,duration};cache.set('ir',out);return out;}
  return{noise,asset,ir,count:()=>cache.size};
}

function bufferFor(ctx,data,resample=false){const sr=resample?ctx.sampleRate:data.sampleRate,n=Math.round(data.channels[0].length*sr/data.sampleRate),b=ctx.createBuffer(data.channels.length,n,sr);data.channels.forEach((x,ch)=>{if(sr===data.sampleRate)b.copyToChannel(x,ch);else{const dest=b.getChannelData(ch);for(let i=0;i<n;i++){const at=i*data.sampleRate/sr,k=Math.floor(at);dest[i]=lerp(x[k]||0,x[Math.min(x.length-1,k+1)]||0,at-k);}}});return b;}
function set(param,value,now,tau=.045){param.cancelScheduledValues(now);param.setTargetAtTime(value,now,tau);}
function createInteractiveAudio(options={}){
  const profiles=(options.scenes?.length?options.scenes:[{id:'space',tones:[110,165],noiseGain:.035,cutoff:2200}]).map((p,i)=>({id:String(i),tones:[110,165],toneGain:.035,noiseGain:.035,cutoff:2200,pan:0,beatSound:'pulse',transitionSound:'air',...p}));
  const controls=options.controls||[],sources=createSources();
  const index=v=>typeof v==='string'?Math.max(0,profiles.findIndex(p=>p.id===v)):clamp(Math.floor(v),0,profiles.length-1);
  const normalize=s=>({...s,scene:index(s.scene??0),nextScene:s.nextScene==null?null:index(s.nextScene),blend:clamp(s.blend),input:{...s.input},motionDuration:clamp(s.motionDuration??1.35,.08,12)});
  let current=normalize({}),graph=null,unlocked=false,active=true,muted=false,disposed=false,unlocking=null,lastMotion=null,eventCount=0;
  const soundEvents=[];
  function makeGraph(ctx){
    const nodes=[],continuous=[],voices=[],events=new Set(),cache=new Map(),keep=n=>(nodes.push(n),n);
    const buffer=data=>{if(!cache.has(data))cache.set(data,bufferFor(ctx,data));return cache.get(data);};
    const bus={bed:keep(ctx.createGain()),action:keep(ctx.createGain()),transition:keep(ctx.createGain())},sum=keep(ctx.createGain()),master=keep(ctx.createGain()),analyser=keep(ctx.createAnalyser());
    const hp=keep(ctx.createBiquadFilter()),comp=keep(ctx.createDynamicsCompressor());hp.type='highpass';hp.frequency.value=28;comp.threshold.value=-12;comp.knee.value=15;comp.ratio.value=3;comp.attack.value=.008;comp.release.value=.22;
    const ir=keep(ctx.createConvolver()),wet=keep(ctx.createGain());ir.buffer=bufferFor(ctx,sources.ir(),true);wet.gain.value=.19;ir.connect(wet);wet.connect(sum);
    for(const [name,b] of Object.entries(bus)){b.gain.value=name==='bed'?.9:.8;b.connect(sum);const send=keep(ctx.createGain());send.gain.value=name==='transition'?.25:.12;b.connect(send);send.connect(ir);}
    sum.connect(hp);hp.connect(comp);comp.connect(master);master.connect(analyser);analyser.connect(ctx.destination);analyser.fftSize=1024;master.gain.value=0;
    for(let i=0;i<profiles.length;i++){
      const p=profiles[i],filter=keep(ctx.createBiquadFilter()),gain=keep(ctx.createGain()),pan=keep(ctx.createStereoPanner());filter.type='lowpass';filter.frequency.value=p.cutoff;filter.Q.value=.5;gain.gain.value=0;pan.pan.value=p.pan;filter.connect(gain);gain.connect(pan);pan.connect(bus.bed);
      const tones=p.tones.map((frequency,j)=>{const o=keep(ctx.createOscillator()),g=keep(ctx.createGain());o.type='sine';o.frequency.value=frequency;g.gain.value=p.toneGain/(1+j*.45);o.connect(g);g.connect(filter);o.start(0);continuous.push(o);return o;});
      const n=keep(ctx.createBufferSource()),ng=keep(ctx.createGain());n.buffer=buffer(sources.noise());n.loop=true;n.playbackRate.value=.85+i*.071;ng.gain.value=p.noiseGain;n.connect(ng);ng.connect(filter);n.start(0,(i*.47)%n.buffer.duration);continuous.push(n);
      voices.push({filter,gain,tones,noiseGain:ng,pan});
    }
    const g={ctx,nodes,continuous,voices,bus,master,analyser,events,buffer,weights:[],parameters:{}};
    g.free=()=>{for(const s of continuous)try{s.stop();}catch{}for(const e of events)try{e.source.stop();}catch{}for(const n of nodes)try{n.disconnect();}catch{}events.clear();};
    return g;
  }
  function apply(g,s,now=g.ctx.currentTime,exact=false){
    const w=profiles.map(()=>0);if(Array.isArray(s.weights)){s.weights.forEach((x,i)=>{if(i<w.length)w[i]=clamp(x);});}else if(s.nextScene!==null&&s.nextScene!==s.scene){w[s.scene]=Math.cos(s.blend*Math.PI/2);w[s.nextScene]=Math.sin(s.blend*Math.PI/2);}else w[s.scene]=1;
    const assign=(p,v)=>exact?p.setValueAtTime(v,now):set(p,v,now);
    g.voices.forEach((v,i)=>assign(v.gain.gain,w[i]));g.weights=w;
    for(const c of controls){const i=index(c.scene??s.scene),v=g.voices[i],value=clamp(s.input[c.input]??c.default??.5),out=lerp(c.min??0,c.max??1,value);g.parameters[c.input+':'+profiles[i].id+':'+c.target]=out;if(c.target==='cutoff')assign(v.filter.frequency,clamp(out,40,20000));else if(c.target==='noiseGain')assign(v.noiseGain.gain,clamp(out,0,.3));else if(c.target==='pitch')v.tones.forEach((o,j)=>assign(o.frequency,profiles[i].tones[j]*clamp(out,.25,4)));else if(c.target==='pan')assign(v.pan.pan,clamp(out,-1,1));}
  }
  function level(g=graph,value=(active && !muted) ? .95 : 0){if(!g)return;const now=g.ctx.currentTime;g.master.gain.cancelScheduledValues(now);g.master.gain.setValueAtTime(g.master.gain.value,now);g.master.gain.linearRampToValueAtTime(value,now+.06);}
  function clearEvents(g){const now=g.ctx.currentTime;for(const e of g.events){e.gain.gain.cancelScheduledValues(now);e.gain.gain.setValueAtTime(e.gain.gain.value,now);e.gain.gain.linearRampToValueAtTime(0,now+.055);try{e.source.stop(now+.06);}catch{}}}
  function emit(g,kind,payload={}){
    const time=Math.max(g.ctx.currentTime,Number(payload.at)||g.ctx.currentTime),variant=eventCount%4,data=sources.asset(kind,variant,!!payload.reverse),source=g.ctx.createBufferSource(),gain=g.ctx.createGain(),pan=g.ctx.createStereoPanner();source.buffer=g.buffer(data);source.playbackRate.value=clamp(payload.rate??1,.3,3);gain.gain.value=clamp(payload.gain??.17,0,.5);pan.pan.value=clamp(payload.pan??0,-1,1);source.connect(gain);gain.connect(pan);pan.connect(g.bus[payload.group||'action']);const e={source,gain,pan};g.events.add(e);source.onended=()=>{g.events.delete(e);source.disconnect();gain.disconnect();pan.disconnect();};source.start(time);source.stop(time+data.duration/source.playbackRate.value+.02);
    if(payload.record!==false){eventCount++;soundEvents.push({kind,at:time,peakAt:time+data.peakOffset/source.playbackRate.value,motionId:payload.motionId??null,reverse:!!payload.reverse,group:payload.group||'action'});if(soundEvents.length>100)soundEvents.shift();}return e;
  }
  function syncMotion(){
    if(!graph||!unlocked||!active||current.motionId==null||current.motionId===lastMotion)return;
    lastMotion=current.motionId;clearEvents(graph);
    if(current.motionProgress>=1)return;
    const cross=current.crossScene??(current.nextScene!==null&&current.scene!==current.nextScene),target=current.targetScene==null?(current.blend>.5?(current.nextScene??current.scene):current.scene):index(current.targetScene),profile=profiles[target];
    const kind=current.transitionSound||(cross?profile.transitionSound:profile.beatSound);
    emit(graph,kind,{group:cross?'transition':'action',gain:cross?.23:.16,reverse:current.reverse,motionId:current.motionId,rate:cross?clamp(sources.asset(kind).duration/Math.max(.08,current.motionDuration*(1-clamp(current.motionProgress))),.3,3):1});
  }
  async function unlock(){
    if(disposed)return false;if(unlocking)return unlocking;
    unlocking=(async()=>{const C=globalThis.AudioContext||globalThis.webkitAudioContext;if(!C)return false;if(!graph)graph=makeGraph(new C());await graph.ctx.resume();unlocked=graph.ctx.state==='running';if(unlocked){apply(graph,current);level();syncMotion();}return unlocked;})().finally(()=>{unlocking=null;});return unlocking;
  }
  function update(raw){current=normalize(raw);if(graph){apply(graph,current);syncMotion();}}
  function trigger(kind,payload={}){if(!graph||!unlocked||!active||disposed)return false;emit(graph,kind,payload);return true;}
  function getState(){let rms=0,peak=0;if(graph){const d=new Float32Array(graph.analyser.fftSize);graph.analyser.getFloatTimeDomainData(d);for(const v of d){rms+=v*v;peak=Math.max(peak,Math.abs(v));}rms=Math.sqrt(rms/d.length);}return{contextState:graph?.ctx.state||'uninitialized',unlocked,active,muted,scene:profiles[graph?.weights.length?graph.weights.indexOf(Math.max(...graph.weights)):current.scene].id,fromScene:profiles[current.scene].id,nextScene:current.nextScene==null?null:profiles[current.nextScene].id,sceneWeights:graph?.weights||[],input:{...current.input},parameters:{...graph?.parameters},liveRms:rms,livePeak:peak,activeTransientCount:graph?.events.size||0,eventCount,soundEvents:soundEvents.slice(),motionId:current.motionId??null,motionProgress:current.motionProgress??1,reverse:!!current.reverse,disposed};}
  async function renderOffline(spec={}){
    const C=globalThis.OfflineAudioContext||globalThis.webkitOfflineAudioContext;if(!C)throw Error('OfflineAudioContext unavailable');const sampleRate=Math.round(clamp(spec.sampleRate??24000,8000,96000)),seconds=clamp(spec.seconds??3,.1,30),ctx=new C(2,Math.ceil(seconds*sampleRate),sampleRate),g=makeGraph(ctx),s=normalize({...current,...spec,nextScene:spec.nextScene??null,blend:spec.blend??0});apply(g,s,0,true);g.master.gain.setValueAtTime(spec.muted?0:.95,0);for(const e of spec.events||[])emit(g,e.kind,{...e,at:Math.max(.001,e.at||.001),record:false});const rendered=await ctx.startRendering();const result={channels:[rendered.getChannelData(0).slice(),rendered.getChannelData(1).slice()],sampleRate,duration:rendered.duration,sameSourceGraph:true,scene:profiles[s.scene].id};g.free();return result;
  }
  return{unlock,update,trigger,getState,renderOffline,setMuted(value){muted=!!value;level();},setActive(value){active=!!value;if(!active&&graph)clearEvents(graph);level();},dispose(){disposed=true;if(graph){graph.free();graph.ctx.close();graph=null;}}};
}
globalThis.AGDInteractiveAudio={create:createInteractiveAudio};
})();
