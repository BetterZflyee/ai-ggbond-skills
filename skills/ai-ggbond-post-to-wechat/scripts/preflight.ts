#!/usr/bin/env npx -y bun
/**
 * 推送前预检脚本
 * 检查 Markdown 文件是否包含图片引用，图片文件是否存在
 * 
 * 用法：npx -y bun preflight.ts /path/to/article.md [--images-dir /path/to/images/]
 */

import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

interface CheckResult {
  name: string;
  ok: boolean;
  detail: string;
}

const results: CheckResult[] = [];

function log(label: string, ok: boolean, detail: string) {
  results.push({ name: label, ok, detail });
  console.log(`${ok ? "✅" : "❌"} ${label}: ${detail}`);
}

function warn(label: string, detail: string) {
  results.push({ name: label, ok: true, detail });
  console.log(`⚠️  ${label}: ${detail}`);
}

const args = process.argv.slice(2);
if (args.length === 0 || args.includes("--help")) {
  console.log(`推送前预检：检查图片引用、文件存在、Tailscale 状态、API 凭证

用法：
  npx -y bun preflight.ts <article.md> [--images-dir <dir>]

检查项：
  1. Markdown 文件存在且非空
  2. 包含 ![alt](path) 图片引用
  3. 引用的图片文件实际存在
  4. images/ 目录中的文件都有对应引用
  5. 封面图存在
  6. Tailscale exit node 状态
  7. API 凭证配置`);
  process.exit(0);
}

const mdPath = path.resolve(args[0]!);
const imagesDirIdx = args.indexOf("--images-dir");
const imagesDir = imagesDirIdx >= 0 ? path.resolve(args[imagesDirIdx + 1]!) : undefined;

// 1. Markdown 文件检查
if (!fs.existsSync(mdPath)) {
  log("Markdown 文件", false, `不存在: ${mdPath}`);
  process.exit(1);
}
const mdContent = fs.readFileSync(mdPath, "utf-8");
if (mdContent.length === 0) {
  log("Markdown 文件", false, "文件为空");
  process.exit(1);
}
log("Markdown 文件", true, `${mdPath} (${(mdContent.length / 1024).toFixed(1)}KB)`);

// 2. 图片引用检查
const imgRegex = /!\[([^\]]*)\]\(([^)]+)\)/g;
const imgRefs: { alt: string; path: string; line: number }[] = [];
let match;
let lineNum = 0;
for (const line of mdContent.split("\n")) {
  lineNum++;
  const lineRegex = /!\[([^\]]*)\]\(([^)]+)\)/g;
  while ((match = lineRegex.exec(line)) !== null) {
    imgRefs.push({ alt: match[1] || "", path: match[2] || "", line: lineNum });
  }
}

if (imgRefs.length === 0) {
  log("图片引用", false, "Markdown 中没有 ![alt](path) 图片引用！正文图片将全部丢失！");
} else {
  log("图片引用", true, `找到 ${imgRefs.length} 个图片引用`);
}

// 3. 图片文件存在检查
const baseDir = path.dirname(mdPath);
let missingImages = 0;
for (const ref of imgRefs) {
  const imgPath = path.isAbsolute(ref.path) ? ref.path : path.resolve(baseDir, ref.path);
  if (!fs.existsSync(imgPath)) {
    log(`图片 #${ref.line}`, false, `文件不存在: ${imgPath}`);
    missingImages++;
  } else {
    const stats = fs.statSync(imgPath);
    if (stats.size === 0) {
      log(`图片 #${ref.line}`, false, `文件为空: ${imgPath}`);
      missingImages++;
    }
  }
}
if (missingImages === 0 && imgRefs.length > 0) {
  log("图片文件", true, "所有引用的图片文件都存在");
}

// 4. images/ 目录交叉检查
const checkDir = imagesDir || path.join(baseDir, "images");
if (fs.existsSync(checkDir)) {
  const dirFiles = fs.readdirSync(checkDir).filter(f => /\.(png|jpg|jpeg|gif|webp)$/i.test(f));
  const referencedFiles = new Set(imgRefs.map(r => path.basename(r.path)));
  const unreferenced = dirFiles.filter(f => !referencedFiles.has(f));
  
  if (unreferenced.length > 0) {
    warn("未引用图片", `${unreferenced.length} 个图片在 images/ 目录中但未被 Markdown 引用:`);
    for (const f of unreferenced) {
      console.log(`   ⚠️  ${f}`);
    }
  } else if (dirFiles.length > 0) {
    log("图片交叉检查", true, `images/ 目录中 ${dirFiles.length} 个图片全部被引用`);
  }
} else {
  warn("images/ 目录", `不存在: ${checkDir}`);
}

// 5. 封面图检查（常见命名）
const coverNames = ["cover.png", "cover.jpg", "cover.jpeg"];
let coverFound = false;
for (const name of coverNames) {
  const coverPath = path.join(baseDir, name);
  if (fs.existsSync(coverPath)) {
    log("封面图", true, coverPath);
    coverFound = true;
    break;
  }
}
if (!coverFound) {
  warn("封面图", "未在文章目录找到 cover.png/jpg，推送时需用 --cover 参数指定");
}

// 6. Tailscale 状态
const tsResult = spawnSync("tailscale", ["status"], { stdio: "pipe", timeout: 5000 });
if (tsResult.status === 0) {
  const tsOutput = tsResult.stdout?.toString() || "";
  if (tsOutput.includes("exit node")) {
    warn("Tailscale", "检测到 exit node 配置，请确认 `curl -s ifconfig.me` 返回白名单 IP");
  } else {
    warn("Tailscale", "未使用 exit node，如果 IP 是动态的，可能触发 40164 错误");
  }
} else {
  warn("Tailscale", "未安装或未运行");
}

// 7. API 凭证
const envPath = path.join(os.homedir(), ".ai-ggbond-skills", ".env");
if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, "utf-8");
  if (envContent.includes("WECHAT_APP_ID") && envContent.includes("WECHAT_APP_SECRET")) {
    log("API 凭证", true, envPath);
  } else {
    log("API 凭证", false, `${envPath} 中缺少 WECHAT_APP_ID 或 WECHAT_APP_SECRET`);
  }
} else {
  log("API 凭证", false, `未找到 ${envPath}`);
}

// 总结
console.log("\n--- 预检结果 ---");
const failed = results.filter(r => !r.ok);
const warnings = results.filter(r => r.ok && r.name.includes("⚠") || false);
if (failed.length === 0) {
  console.log("🎉 预检通过！可以推送。");
  if (imgRefs.length === 0) {
    console.log("⚠️  但注意：Markdown 中没有图片引用，正文将没有图片。");
  }
} else {
  console.log(`❌ ${failed.length} 个问题需要修复：`);
  for (const f of failed) {
    console.log(`  • ${f.name}: ${f.detail}`);
  }
  process.exit(1);
}

import os from "node:os";
