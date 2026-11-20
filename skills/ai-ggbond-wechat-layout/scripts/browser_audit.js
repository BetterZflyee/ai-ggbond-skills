/* Evaluate this expression in an isolated preview browser. Read-only DOM audit. */
(() => {
  const all=[...document.querySelectorAll('body *')];
  const blocks=[...document.querySelectorAll('[data-layout-block]')];
  const id=e=>e.closest('[data-layout-block]')?.dataset.layoutBlock||null;
  const rgb=s=>{const m=s.match(/[\d.]+/g);return m?[Number(m[0]),Number(m[1]),Number(m[2]),m[3]===undefined?1:Number(m[3])]:null;};
  const luminance=c=>c.slice(0,3).map(x=>x/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((v,x,i)=>v+x*[.2126,.7152,.0722][i],0);
  const background=e=>{let colors=[];for(let p=e;p;p=p.parentElement){let c=rgb(getComputedStyle(p).backgroundColor);if(c&&c[3]>0)colors.push(c);}let color=[255,255,255];for(const c of colors.reverse())color=color.map((x,i)=>c[i]*c[3]+x*(1-c[3]));return color;};
  const pairs=new Map();
  for(const e of document.querySelectorAll('[data-layout-field],[data-layout-copy-of],a')){
    if(!e.textContent.trim())continue;
    const fg=rgb(getComputedStyle(e).color),bg=background(e);if(!fg)continue;
    const a=luminance(fg),b=luminance(bg),ratio=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);
    const key=fg.join(',')+'/'+bg.join(',');
    if(!pairs.has(key))pairs.set(key,{foreground:fg,background:bg,ratio,passed:ratio>=4.5,exampleBlock:id(e)});
  }
  const headings=[...document.querySelectorAll('h2,h3')].map(h=>{
    const block=h.closest('[data-layout-block]'),prev=block?.previousElementSibling,next=block?.nextElementSibling;
    return {block:id(h),text:h.textContent,before:prev?h.getBoundingClientRect().top-prev.getBoundingClientRect().bottom:null,after:next?.firstElementChild?next.firstElementChild.getBoundingClientRect().top-h.getBoundingClientRect().bottom:null};
  });
  const lineIssues=[];
  for(const element of document.querySelectorAll('h2,h3,p')){
    if(!element.textContent.trim())continue;
    const walker=document.createTreeWalker(element,NodeFilter.SHOW_TEXT),lines=new Map();
    let node;
    while((node=walker.nextNode())){
      let offset=0;
      for(const c of node.textContent){
        const range=document.createRange();range.setStart(node,offset);range.setEnd(node,offset+c.length);offset+=c.length;
        if(!c.trim())continue;
        const rect=range.getBoundingClientRect();if(!rect.width||!rect.height)continue;
        const y=Math.round(rect.top/3)*3;
        if(!lines.has(y))lines.set(y,[]);
        lines.get(y).push(c);
      }
    }
    const textLines=[...lines.entries()].sort((a,b)=>a[0]-b[0]).map(x=>x[1].join(''));
    if(/^H/.test(element.tagName)&&textLines.length>1&&textLines.at(-1).length<=2)lineIssues.push({code:'SHORT_HEADING_LAST_LINE',block:id(element),lastLine:textLines.at(-1)});
    for(const line of textLines){
      if(/^[，。！？；：、）】》」』]/.test(line))lineIssues.push({code:'LINE_START_PUNCTUATION',block:id(element),line});
      if(/[（【《「『]$/.test(line))lineIssues.push({code:'LINE_END_OPENING_PUNCTUATION',block:id(element),line});
    }
  }
  const images=[...document.images].map(i=>{
    const rect=i.getBoundingClientRect(),sourceFont=Number(i.dataset.sourceMinTextPx)||null;
    return {block:id(i),loaded:i.complete&&i.naturalWidth>0,natural:[i.naturalWidth,i.naturalHeight],rendered:[rect.width,rect.height],distorted:i.naturalWidth>0&&Math.abs(i.naturalWidth/i.naturalHeight-rect.width/rect.height)>.01,upscaled:rect.width>i.naturalWidth+1,estimatedTextPx:sourceFont&&i.naturalWidth?sourceFont*rect.width/i.naturalWidth:null};
  });
  const visibleBounds=e=>{const r=e.getBoundingClientRect();let left=r.left,right=r.right;for(let p=e.parentElement;p;p=p.parentElement){if(['auto','scroll','hidden','clip'].includes(getComputedStyle(p).overflowX)){const pr=p.getBoundingClientRect();left=Math.max(left,pr.left+p.clientLeft);right=Math.min(right,pr.left+p.clientLeft+p.clientWidth);}}return {left,right,width:Math.max(0,right-left)};};
  const overflow=all.filter(e=>{const r=visibleBounds(e);return r.width&&(r.right>innerWidth+1||r.left< -1);}).map(e=>({tag:e.tagName,block:id(e)}));
  const horizontalScroll=all.filter(e=>['auto','scroll'].includes(getComputedStyle(e).overflowX)&&e.scrollWidth>e.clientWidth+1).map(e=>({tag:e.tagName,block:id(e),visibleWidth:e.clientWidth,contentWidth:e.scrollWidth}));
  const brokenNumbers=[...document.querySelectorAll('[data-layout-number]')].filter(e=>{const range=document.createRange();range.selectNodeContents(e.firstElementChild||e);return new Set([...range.getClientRects()].filter(r=>r.width).map(r=>Math.round(r.top/3))).size>1;}).map(e=>({block:id(e),text:e.textContent}));
  const clipping=all.filter(e=>{const s=getComputedStyle(e);return (['hidden','clip'].includes(s.overflowY)&&e.scrollHeight>e.clientHeight+1)||(['hidden','clip'].includes(s.overflowX)&&e.scrollWidth>e.clientWidth+1);}).map(e=>({tag:e.tagName,block:id(e)}));
  return {viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,blocks:blocks.length,overflow,clipping,horizontalScroll,brokenNumbers,headings,contrast:[...pairs.values()],images,lineIssues,scope:'browser evidence only; punctuation and short-line findings need editorial judgment; table scroll remains inside its container'};
})()
