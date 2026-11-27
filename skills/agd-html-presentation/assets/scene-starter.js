// 接口示范：正式作品应按主题重新创作，见 SKILL.md。
export const scenes = (() => {
  const topic = __TOPIC_JSON__;
  const W = 1920, H = 1080;
  const colors = {bg:'#101722',ink:'#f3f0e9',dim:'#a6b0bb',accent:'#e7ad72',soft:'#647a92',line:'#2c3c4d'};
  const cap = n => Math.max(0,Math.min(1,n));
  const mix = (a,b,p) => a+(b-a)*p;
  const ease = p => {p=cap(p);return p*p*(3-2*p);};
  function text(c,value,x,y,size=56,color=colors.ink,align='left') {
    c.font=`${size>=70?'500':'400'} ${size}px "PingFang SC","Microsoft YaHei",system-ui,sans-serif`;
    c.fillStyle=color;c.textAlign=align;c.textBaseline='middle';c.fillText(value,x,y);
  }
  function background(c) {c.fillStyle=colors.bg;c.fillRect(0,0,W,H);}
  function dot(c,x,y,r=18,alpha=1) {c.save();c.globalAlpha=alpha;c.fillStyle=colors.accent;c.beginPath();c.arc(x,y,r,0,Math.PI*2);c.fill();c.restore();}
  function heading(c,title,subtitle='') {text(c,title,130,160,76);if(subtitle)text(c,subtitle,134,266,34,colors.dim);}
  function footer(c,n) {text(c,'运行底座示范 · 正式作品需重新创作',130,990,25,colors.dim);text(c,String(n),1790,990,28,colors.dim,'right');}
  function reveal({ctx,A,B,p,width,height}) {
    if(p<=0){ctx.drawImage(A,0,0);return;}
    if(p>=1){ctx.drawImage(B,0,0);return;}
    ctx.drawImage(A,0,0);
    ctx.save();ctx.beginPath();ctx.arc(960,610,ease(p)*Math.hypot(width,height),0,Math.PI*2);ctx.clip();ctx.drawImage(B,0,0);ctx.restore();
  }
  function makeParticles(random) {
    return Array.from({length:64},(_,i)=>({x:180+random()*1560,y:360+random()*510,phase:random()*Math.PI*2,index:i}));
  }
  return [
    {
      id:'opening', title:'从主题找到关系',
      beats:[{dur:2.4,hold:3},{dur:3.5,hold:4},{dur:3,hold:3}],
      notes:[`主题：${topic}。本工程展示运行接口，正式创作应为主题设计自己的论证与视觉模型。`,'各个元素开始连接；用位置变化代替额外的说明文字。','同一核心对象留在画面中心，下一场由它展开。'],
      create(ctx) {
        const particles=makeParticles(ctx.random);let s;
        return {update(state){s=state;},render(c,state){
          const p=state.k(1,0,3.5),q=state.k(2,0,3);background(c);
          const title=topic.length>22?topic.slice(0,21)+'…':topic;
          heading(c,title,'示范：观察元素怎样形成关系');
          c.strokeStyle=colors.line;c.lineWidth=2;
          for(const a of particles){
            const angle=a.index/particles.length*Math.PI*2;
            const tx=960+Math.cos(angle)*350*(1-q),ty=610+Math.sin(angle)*210*(1-q);
            const x=mix(a.x+(state.reducedMotion?0:Math.sin(state.t*.5+a.phase)*14),tx,p),y=mix(a.y,ty,p);
            c.globalAlpha=p*(1-q)*.6;c.beginPath();c.moveTo(x,y);c.lineTo(960,610);c.stroke();c.globalAlpha=1;
            dot(c,x,y,5+q*5,.25+.7*state.k(0,0,2.4));
          }
          dot(c,960,610,22+q*15);footer(c,1);
        }};
      }
    },
    {
      id:'relationship',title:'用交互观察关系',enterWith:reveal,transitionDuration:1.2,
      beats:[{dur:2,hold:4},{dur:3.5,hold:5},{dur:3,hold:4}],
      notes:['拖动画面下方的滑块，改变元素的聚合程度。','松手后保留用户参数；进入下一拍时约2.6秒回到编排位置。','让元素回到同一个核心点，作为下一个场景的视觉入口。'],
      create(ctx) {
        const particles=makeParticles(ctx.random);
        let split=.45,user=.45,weight=0,returning=false,dragging=false,offset=0,lastBeat=0;
        const xOf=()=>470+split*980;
        return {
          enter(state){lastBeat=state.beat;split=user=.45;weight=0;dragging=returning=false;},
          update(state){
            if(state.beat!==lastBeat){lastBeat=state.beat;if(weight>0&&!dragging)returning=true;}
            if(returning&&!dragging)weight=state.reducedMotion?0:Math.max(0,weight-state.dt/2.6);
            const automatic=mix(mix(.45,.8,state.k(1,0,3.5)),1,state.k(2,0,3));
            split=mix(automatic,user,ease(weight));
          },
          pointer(kind,x,y){
            if(kind==='down' && Math.abs(x-xOf())<70 && Math.abs(y-860)<70){dragging=true;returning=false;offset=x-xOf();weight=1;user=split;return true;}
            if(kind==='move'&&dragging){user=cap((x-offset-470)/980);weight=1;return true;}
            if(kind==='up'||kind==='cancel'){const was=dragging;dragging=false;return was;}
            return false;
          },
          get debug(){return {value:split,userValue:user,userWeight:weight,dragging,returning,handle:{x:xOf(),y:860}};},
          render(c,state){
            background(c);heading(c,'改变一个条件，观察整幅画面','拖动下方滑块；变化会作用到全部元素');
            const settled=state.k(2,0,3);
            c.strokeStyle=colors.line;c.lineWidth=2;
            for(const a of particles){
              const angle=a.index/particles.length*Math.PI*2;
              const tx=960+Math.cos(angle)*mix(420,35,split)*(1-settled),ty=610+Math.sin(angle)*mix(180,15,split)*(1-settled);
              const x=mix(a.x,tx,state.k(0,0,2)),y=mix(a.y,ty,state.k(0,0,2));
              c.beginPath();c.moveTo(960,610);c.lineTo(x,y);c.stroke();dot(c,x,y,7,.7);
            }
            dot(c,960,610,37);
            c.strokeStyle=colors.soft;c.lineWidth=6;c.beginPath();c.moveTo(470,860);c.lineTo(1450,860);c.stroke();
            dot(c,xOf(),860,dragging?27:22);
            text(c,'分散',440,860,30,colors.dim,'right');text(c,'聚合',1480,860,30,colors.dim);
            text(c,`${Math.round(split*100)}%`,960,930,33,colors.ink,'center');footer(c,2);
          }
        };
      }
    },
    {
      id:'return',title:'带着新理解回到起点',enterWith:reveal,transitionDuration:1.1,
      beats:[{dur:3,hold:3},{dur:4,hold:5}],
      notes:['同一个核心点保留在相同坐标，周围的关系展开。','结尾重新提出开场问题，让此前的变化成为回答。'],
      create(ctx) {
        return {render(c,state){
          background(c);heading(c,'回到同一个对象','让结尾带回开场，而理解已经改变');
          const p=state.k(0,0,3),q=state.k(1,0,4);
          for(let i=0;i<6;i++){
            const a=i/6*Math.PI*2,x=960+Math.cos(a)*340*p,y=610+Math.sin(a)*220*p;
            c.strokeStyle=colors.line;c.lineWidth=3;c.beginPath();c.moveTo(960,610);c.lineTo(x,y);c.stroke();dot(c,x,y,14);
          }
          dot(c,960,610,37);c.globalAlpha=q;text(c,'现在，哪些关系变得清楚了？',960,860,54,colors.ink,'center');c.globalAlpha=1;footer(c,3);
        }};
      }
    }
  ];
})();
