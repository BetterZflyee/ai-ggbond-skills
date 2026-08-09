#!/usr/bin/env python3
"""
SF 离线语音转写脚本
通过 SF 内部 llm-model-hub-apis 代理调用阿里云 qwen3-asr-flash-filetrans
"""
import json, base64, subprocess, time, tempfile, sys, os

# 从环境变量或 Claude 配置读取 JWT
def get_jwt():
    """获取 JWT token"""
    for source in ['SF_JWT', 'ANTHROPIC_AUTH_TOKEN']:
        val = os.environ.get(source, '')
        if val and val.startswith('eyJ'):
            return val
    # 尝试从 settings.json 读取
    settings_path = os.path.expanduser('~/.claude/settings.json')
    if os.path.exists(settings_path):
        with open(settings_path) as f:
            settings = json.load(f)
        token = settings.get('env', {}).get('ANTHROPIC_AUTH_TOKEN', '')
        if token and token.startswith('eyJ'):
            return token
    print("ERROR: 未找到 JWT token。请设置 SF_JWT 环境变量或确保 ~/.claude/settings.json 中有 ANTHROPIC_AUTH_TOKEN", file=sys.stderr)
    sys.exit(1)

JWT = get_jwt()
BASE_URL = "https://llm-model-hub-apis.sf-express.com/v1/audio/transcriptions"
MODEL = "aliyun/qwen3-asr-flash-filetrans"


def api(method, url, body=None, extra_headers=None):
    """调用 API（使用 curl 避免 Python SSL 问题）"""
    cmd = ['curl', '-s', '-X', method, url,
           '-H', f'Authorization: Bearer {JWT}',
           '-H', 'Content-Type: application/json']
    if extra_headers:
        for k, v in extra_headers.items():
            cmd += ['-H', f'{k}: {v}']
    if body:
        cmd += ['-d', json.dumps(body)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        return {'error': f'curl error: {result.stderr[:200]}'}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {'error': f'Invalid JSON: {result.stdout[:200]}'}


def transcribe(audio_file, output_file, max_chunk_b64=58000):
    """
    转写音频文件

    Args:
        audio_file: MP3 音频文件路径（建议 32kbps 单声道 16kHz）
        output_file: 输出 JSON 文件路径
        max_chunk_b64: 每个分片最大 base64 字符数（默认 58000，SF API 限制 61440）

    Returns:
        list of sentences with begin_time, end_time, text
    """
    # 读取音频
    with open(audio_file, 'rb') as f:
        full_b64 = base64.b64encode(f.read()).decode('utf-8')

    # 获取时长
    probe = subprocess.run(['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
        '-of', 'csv=p=0', audio_file], capture_output=True, text=True)
    total_dur = float(probe.stdout.strip())

    # 计算分片大小
    cps = len(full_b64) / total_dur
    chunk_dur = max_chunk_b64 / cps

    print(f"[transcribe] 音频时长: {total_dur:.1f}s, {len(full_b64)} chars base64")
    print(f"[transcribe] 分片大小: {chunk_dur:.1f}s/片, 预计 {int(total_dur/chunk_dur)+1} 片")

    # 分片
    tmpdir = tempfile.mkdtemp(prefix='asr_')
    chunks = []
    t = 0.0
    while t < total_dur:
        dur = min(chunk_dur, total_dur - t)
        out = f"{tmpdir}/c_{len(chunks):04d}.mp3"
        subprocess.run(['ffmpeg', '-y', '-i', audio_file, '-ss', str(t), '-t', str(dur),
            '-b:a', '32k', '-ac', '1', '-ar', '16000', out], capture_output=True)
        with open(out, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode('utf-8')
        data_url = f"data:audio/mp3;base64,{b64}"
        chunks.append({'start': t, 'dur': dur, 'data_url': data_url})
        t += dur

    print(f"[transcribe] 共 {len(chunks)} 个分片，开始转写...")

    all_sentences = []
    errors = 0
    rate_limited = 0

    for i, c in enumerate(chunks):
        label = f"[{int(c['start']//60):02d}:{int(c['start']%60):02d}]"
        if i % 10 == 0:
            print(f"[transcribe] {i+1}/{len(chunks)} {label}...", end=' ', flush=True)

        # 创建任务
        resp = api('POST', BASE_URL, {
            'model': MODEL,
            'input': {'file_url': c['data_url']},
            'parameters': {'channel_id': [0], 'enable_itn': False, 'enable_words': True}
        })

        if 'error' in resp:
            err_msg = str(resp['error'])
            if '429' in err_msg or 'rate' in err_msg.lower():
                rate_limited += 1
                time.sleep(10)  # 等 10 秒
                # 重试一次
                time.sleep(5)
                resp = api('POST', BASE_URL, {
                    'model': MODEL,
                    'input': {'file_url': c['data_url']},
                    'parameters': {'channel_id': [0], 'enable_itn': False, 'enable_words': True}
                })
                if 'error' in resp:
                    errors += 1
                    continue
            else:
                errors += 1
                continue

        if 'output' not in resp:
            errors += 1
            continue

        task_id = resp['output']['task_id']

        # 轮询状态
        for _ in range(60):
            time.sleep(2)
            status = api('GET', f'{BASE_URL}/{task_id}', extra_headers={'model': MODEL})
            ts = status.get('output', {}).get('task_status', '?')

            if ts == 'SUCCEEDED':
                dl_url = status['output']['result']['transcription_url']
                dl = api('POST', f'{BASE_URL}/download', {'url': dl_url}, extra_headers={'model': MODEL})

                if 'transcripts' in dl:
                    for tscript in dl['transcripts']:
                        for s in tscript.get('sentences', []):
                            s['begin_time'] = s.get('begin_time', 0) + int(c['start'] * 1000)
                            s['end_time'] = s.get('end_time', 0) + int(c['start'] * 1000)
                        all_sentences.extend(tscript.get('sentences', []))
                elif 'sentences' in dl:
                    for s in dl['sentences']:
                        s['begin_time'] = s.get('begin_time', 0) + int(c['start'] * 1000)
                    all_sentences.extend(dl['sentences'])
                break
            elif ts == 'FAILED':
                errors += 1
                break
        else:
            errors += 1  # 超时

        # 频率控制：每 3 个分片休息一下
        if i > 0 and i % 5 == 0:
            time.sleep(3)

    # 保存结果
    result = {
        'sentences': all_sentences,
        'stats': {
            'total_chunks': len(chunks),
            'total_sentences': len(all_sentences),
            'errors': errors,
            'rate_limited': rate_limited,
            'audio_duration': total_dur
        }
    }
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n[transcribe] 完成: {len(all_sentences)} 句, {errors} 错误, {rate_limited} 限流")
    return all_sentences


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <audio.mp3> [output.json]", file=sys.stderr)
        print("  音频文件建议: 32kbps MP3, 单声道, 16kHz", file=sys.stderr)
        sys.exit(1)

    audio = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else audio.replace('.mp3', '_transcript.json')
    transcribe(audio, output)