#!/usr/bin/env node
const fs = require('node:fs');
const https = require('node:https');
const { Buffer } = require('node:buffer');
const path = require('node:path');
const { URL } = require('node:url');

const args = process.argv.slice(2);
let prompt = '';
let outputFile = '';
let aspectRatio = '1:1';
let model = process.env.YUNWU_IMAGE_MODEL || 'gpt-image-1';
let quality = process.env.YUNWU_IMAGE_QUALITY || 'standard';

for (let i = 0; i < args.length; i++) {
    if (args[i] === '--prompt' && args[i + 1]) {
        prompt = args[i + 1];
        i++;
    } else if (args[i] === '--output' && args[i + 1]) {
        outputFile = args[i + 1];
        i++;
    } else if (args[i] === '--aspect-ratio' && args[i + 1]) {
        aspectRatio = args[i + 1];
        i++;
    } else if (args[i] === '--model' && args[i + 1]) {
        model = args[i + 1];
        i++;
    } else if (args[i] === '--quality' && args[i + 1]) {
        quality = args[i + 1];
        i++;
    }
}

if (!prompt) {
    console.error('Error: --prompt is required');
    process.exit(1);
}

if (!outputFile) {
    const dir = path.join(process.env.USERPROFILE || process.env.HOME || '/home/ubuntu', 'Pictures', 'Clawd');
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    outputFile = path.join(dir, `marketing_image_${Date.now()}.png`);
}

const apiKey = process.env.YUNWU_API_KEY;
if (!apiKey) {
    console.error('Error: YUNWU_API_KEY is required');
    process.exit(1);
}

const imageEndpoints = [
    'https://yunwu.ai/v1/images/generations',
    'https://yunwu.zeabur.app/v1/images/generations',
    'https://api.apiplus.org/v1/images/generations'
];
const chatEndpoints = [
    'https://yunwu.ai/v1/chat/completions',
    'https://yunwu.zeabur.app/v1/chat/completions',
    'https://api.apiplus.org/v1/chat/completions'
];
const geminiEndpoints = [
    'https://yunwu.ai/v1beta/models',
    'https://api.apiplus.org/v1beta/models'
];

const sizeMap = {
    '1:1': '1024x1024',
    '16:9': '1792x1024',
    '9:16': '1024x1792',
    '4:3': '1365x1024',
    '3:4': '1024x1365'
};
const size = sizeMap[aspectRatio] || sizeMap['1:1'];

console.log('🎨 生成营销图片中...');
console.log(`   Prompt: "${prompt.substring(0, 80)}${prompt.length > 80 ? '...' : ''}"`);
console.log(`   Ratio:  ${aspectRatio}`);
console.log(`   Size:   ${size}`);
console.log(`   Model:  ${model}`);

const payload = {
    model,
    prompt,
    n: 1,
    size,
    quality
};
const isGeminiModel = model.toLowerCase().includes('gemini');

function postJson(url, body, headers, timeoutMs = 180000) {
    return new Promise((resolve, reject) => {
        const parsed = new URL(url);
        const req = https.request({
            hostname: parsed.hostname,
            path: `${parsed.pathname}${parsed.search}`,
            method: 'POST',
            port: parsed.port || 443,
            headers,
            timeout: timeoutMs
        }, (res) => {
            let raw = '';
            res.on('data', (chunk) => {
                raw += chunk.toString();
            });
            res.on('end', () => {
                const contentType = String(res.headers['content-type'] || '');
                let json = null;
                if (contentType.includes('application/json') || raw.trim().startsWith('{')) {
                    try {
                        json = JSON.parse(raw);
                    } catch (error) {
                        reject(new Error(`Invalid JSON response: ${error.message}`));
                        return;
                    }
                }
                resolve({
                    statusCode: res.statusCode || 0,
                    statusMessage: res.statusMessage || '',
                    json,
                    raw
                });
            });
        });
        req.on('timeout', () => {
            req.destroy(new Error('Request timeout'));
        });
        req.on('error', reject);
        req.write(JSON.stringify(body));
        req.end();
    });
}

function downloadImage(url, outputPath, redirects = 0) {
    return new Promise((resolve, reject) => {
        if (redirects > 5) {
            reject(new Error('Too many redirects'));
            return;
        }
        const req = https.get(url, (res) => {
            if (res.statusCode && [301, 302, 303, 307, 308].includes(res.statusCode) && res.headers.location) {
                const next = new URL(res.headers.location, url).toString();
                res.resume();
                downloadImage(next, outputPath, redirects + 1).then(resolve).catch(reject);
                return;
            }
            if (res.statusCode !== 200) {
                reject(new Error(`Download failed: ${res.statusCode} ${res.statusMessage || ''}`));
                return;
            }
            const file = fs.createWriteStream(outputPath);
            res.pipe(file);
            file.on('finish', () => {
                file.close(() => resolve());
            });
            file.on('error', (err) => reject(err));
        });
        req.on('error', reject);
    });
}

function extractImageFromObject(node) {
    if (Array.isArray(node)) {
        for (const item of node) {
            const found = extractImageFromObject(item);
            if (found) return found;
        }
        return null;
    }
    if (!node || typeof node !== 'object') {
        if (typeof node === 'string' && node.startsWith('data:image/') && node.includes('base64,')) {
            return { b64: node.split('base64,')[1] };
        }
        return null;
    }
    if (typeof node.b64_json === 'string' && node.b64_json) return { b64: node.b64_json };
    if (typeof node.b64 === 'string' && node.b64) return { b64: node.b64 };
    if (typeof node.base64 === 'string' && node.base64) return { b64: node.base64 };
    if (typeof node.url === 'string' && /^https?:\/\//.test(node.url)) return { url: node.url };
    if (node.image_url && typeof node.image_url === 'object' && typeof node.image_url.url === 'string') {
        return { url: node.image_url.url };
    }
    for (const value of Object.values(node)) {
        const found = extractImageFromObject(value);
        if (found) return found;
    }
    return null;
}

async function generate() {
    const headers = {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
    };

    let lastError = 'Unknown error';
    if (isGeminiModel) {
        const geminiPayload = {
            contents: [
                {
                    parts: [{ text: prompt }]
                }
            ],
            generationConfig: {
                responseModalities: ['TEXT', 'IMAGE']
            }
        };
        for (const endpoint of geminiEndpoints) {
            try {
                const url = `${endpoint}/${encodeURIComponent(model)}:generateContent`;
                const result = await postJson(url, geminiPayload, headers);
                if (result.statusCode !== 200) {
                    const errorMessage =
                        result.json?.error?.message ||
                        result.json?.message ||
                        result.raw?.substring(0, 300) ||
                        `${result.statusCode} ${result.statusMessage}`;
                    lastError = `Gemini API ${url} 返回异常: ${errorMessage}`;
                    continue;
                }
                const parts = result.json?.candidates?.[0]?.content?.parts || [];
                const imagePart = parts.find((part) => part?.inlineData?.data || part?.inline_data?.data);
                const b64 = imagePart?.inlineData?.data || imagePart?.inline_data?.data;
                if (!b64) {
                    lastError = `Gemini API ${url} 未返回图片数据`;
                    continue;
                }
                fs.writeFileSync(outputFile, Buffer.from(b64, 'base64'));
                console.log(`✅ 图片已保存: ${outputFile}`);
                console.log(`MEDIA: ${outputFile}`);
                return;
            } catch (error) {
                lastError = `Gemini API ${endpoint} 请求失败: ${error.message}`;
            }
        }
    }

    const chatPayload = {
        model,
        messages: [{ role: 'user', content: prompt }],
        size,
        quality
    };
    for (const endpoint of chatEndpoints) {
        try {
            const result = await postJson(endpoint, chatPayload, headers);
            if (result.statusCode !== 200) {
                const errorMessage =
                    result.json?.error?.message ||
                    result.json?.message ||
                    result.raw?.substring(0, 300) ||
                    `${result.statusCode} ${result.statusMessage}`;
                lastError = `Chat API ${endpoint} 返回异常: ${errorMessage}`;
                continue;
            }
            const found = extractImageFromObject(result.json);
            if (!found) {
                lastError = `Chat API ${endpoint} 未返回图片数据`;
                continue;
            }
            if (found.b64) {
                fs.writeFileSync(outputFile, Buffer.from(found.b64, 'base64'));
                console.log(`✅ 图片已保存: ${outputFile}`);
                console.log(`MEDIA: ${outputFile}`);
                return;
            }
            if (found.url) {
                await downloadImage(found.url, outputFile);
                console.log(`✅ 图片已保存: ${outputFile}`);
                console.log(`MEDIA: ${outputFile}`);
                return;
            }
            lastError = `Chat API ${endpoint} 返回结构不支持`;
        } catch (error) {
            lastError = `Chat API ${endpoint} 请求失败: ${error.message}`;
        }
    }

    for (const endpoint of imageEndpoints) {
        try {
            const result = await postJson(endpoint, payload, headers);
            if (result.statusCode !== 200) {
                const errorMessage =
                    result.json?.error?.message ||
                    result.json?.message ||
                    result.raw?.substring(0, 300) ||
                    `${result.statusCode} ${result.statusMessage}`;
                lastError = `API ${endpoint} 返回异常: ${errorMessage}`;
                continue;
            }
            const item = result.json?.data?.[0];
            if (!item) {
                lastError = `API ${endpoint} 未返回图片数据`;
                continue;
            }
            if (item.b64_json) {
                fs.writeFileSync(outputFile, Buffer.from(item.b64_json, 'base64'));
                console.log(`✅ 图片已保存: ${outputFile}`);
                console.log(`MEDIA: ${outputFile}`);
                return;
            }
            if (item.url) {
                await downloadImage(item.url, outputFile);
                console.log(`✅ 图片已保存: ${outputFile}`);
                console.log(`MEDIA: ${outputFile}`);
                return;
            }
            lastError = `API ${endpoint} 返回结构不支持`;
        } catch (error) {
            lastError = `API ${endpoint} 请求失败: ${error.message}`;
        }
    }
    throw new Error(lastError);
}

generate()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(`❌ 生成失败: ${error.message}`);
        if (!outputFile.endsWith('.png')) {
            console.error('提示: 建议输出文件使用 .png 后缀');
        }
        process.exit(1);
    });
