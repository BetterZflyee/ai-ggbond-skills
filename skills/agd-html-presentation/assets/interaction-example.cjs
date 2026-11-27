// 配套示范交互断言；正式作品应按自己的交互状态改写。
module.exports = async function(page) {
  await page.evaluate(()=>window.__deck.seek('relationship',0,3));
  const before=await page.evaluate(()=>window.__deck.instance.debug);
  const point=await page.evaluate(()=>{
    const d=window.__deck, h=d.instance.debug.handle, r=document.getElementById('stage').getBoundingClientRect(), v=d.state.view;
    return {x:r.left+v.offsetX+h.x*v.scale,y:r.top+v.offsetY+h.y*v.scale,target:r.left+v.offsetX+1300*v.scale};
  });
  await page.mouse.move(point.x,point.y);await page.mouse.down();
  await page.mouse.move(point.target,point.y,{steps:8});
  await page.evaluate(()=>{window.__deck.pause();window.__deck.step(1/60);});
  await page.mouse.up();
  const released=await page.evaluate(()=>window.__deck.instance.debug);
  await page.evaluate(()=>window.__deck.step(3));
  const held=await page.evaluate(()=>window.__deck.instance.debug);
  await page.evaluate(()=>{window.__deck.advance();window.__deck.step(3);});
  const next=await page.evaluate(()=>window.__deck.instance.debug);
  const passed=Math.abs(released.value-before.value)>.2 && !released.dragging &&
    Math.abs(held.value-released.value)<.001 && next.userWeight<.001;
  return {passed,details:{before,released,held,next}};
};
