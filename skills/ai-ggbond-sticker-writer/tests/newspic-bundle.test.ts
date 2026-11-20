import {test, expect, beforeEach, afterEach} from "bun:test";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import {createHash} from "node:crypto";
import {readStickerBundle, assertStickerWritable, uploadStickerImages} from "../adapters/newspic-bundle.ts";

let root: string;
let file: string;
let data: any;
beforeEach(()=>{
  root=fs.mkdtempSync(path.join(os.tmpdir(),"newspic-bundle-test-"));file=path.join(root,"bundle.json");
  fs.writeFileSync(path.join(root,"one.png"),"image fixture bytes");
  const hash=createHash("sha256").update("image fixture bytes").digest("hex");
  data={owner:"ai-ggbond-sticker-writer",schema_version:1,article_type:"newspic",status:"ready",title:"测试",content:"纯文本，保留 12.00%。\n\n#标签",images:[{id:"one",order:1,path:"one.png",sha256:hash,alt:"图一"}],draft_target:{account:null,existing_media_id:null}};
});
afterEach(()=>fs.rmSync(root,{recursive:true,force:true}));
function load(){fs.writeFileSync(file,JSON.stringify(data));fs.writeFileSync(path.join(root,"manifest.json"),JSON.stringify({owner:data.owner,files:{"bundle.json":createHash("sha256").update(fs.readFileSync(file)).digest("hex")}}));return readStickerBundle(file);}

test("native copy remains plain text and images remain ordered",()=>{
  const bundle=load();expect(bundle.content).toBe(data.content);expect(bundle.images[0].id).toBe("one");expect(()=>assertStickerWritable(bundle)).not.toThrow();
});
test("reject article HTML in native caption",()=>{data.content="<p>正文</p>";expect(load).toThrow("plain text");});
test("missing or reordered images cannot silently pass",()=>{data.images[0].order=2;expect(load).toThrow("order");});
test("image tampering invalidates handoff",()=>{fs.writeFileSync(path.join(root,"one.png"),"changed");expect(load).toThrow("changed after review");});
test("pending review can be inspected locally but cannot be uploaded",()=>{data.status="review_required";const b=load();expect(()=>assertStickerWritable(b)).toThrow("review is pending");});
test("existing draft does not get a duplicate create",()=>{data.draft_target.existing_media_id="existing";expect(()=>assertStickerWritable(load())).toThrow("existing draft");});
test("stop at failed upload; never skip an image",async()=>{
  data.images.push({...data.images[0],id:"two",order:2},{...data.images[0],id:"three",order:3});
  const bundle=load();const called:string[]=[];
  await expect(uploadStickerImages(bundle,async p=>{called.push(p);if(called.length===2)throw new Error("mock failure");return {media_id:"first"};})).rejects.toThrow("mock failure");
  expect(called.length).toBe(2);
});
test("upload result without media ID is not success",async()=>{await expect(uploadStickerImages(load(),async()=>({}))).rejects.toThrow("no media_id");});
test("caption changed after pack audit is detected",()=>{load();data.content="Changed caption";fs.writeFileSync(file,JSON.stringify(data));expect(()=>readStickerBundle(file)).toThrow("manifest changed");});
