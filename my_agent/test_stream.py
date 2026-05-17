"""Test agent SSE streaming and count tool calls."""
import sys
import io
import json
import httpx

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MSG = '你好，请用中文回答：有什么适合新手的Python学习资源推荐？'

tool_count = 0
tools_used = []
current_event = None
chunks = 0

print("Sending request...")
with httpx.Client(timeout=90) as client:
    with client.stream('POST', 'http://127.0.0.1:8100/chat/stream',
                       json={'message': MSG}) as resp:
        for raw_line in resp.iter_lines():
            line = raw_line.strip() if isinstance(raw_line, str) else raw_line.decode('utf-8', errors='replace').strip()
            if not line:
                continue
            if line.startswith('event: '):
                current_event = line[7:]
            elif line.startswith('data: '):
                data_str = line[6:]
                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError:
                    continue
                if current_event == 'status':
                    t = data.get('type', '')
                    if t == 'tool_start':
                        tool_count += 1
                        tools_used.append(data.get('tool', '?'))
                        print(f'\n  [TOOL_START] {data.get("tool", "?")}')
                    elif t == 'tool_end':
                        print(f'  [TOOL_END] {data.get("tool", "?")}')
                elif current_event == 'token':
                    c = data.get('content', '')
                    if c:
                        print(c, end='', flush=True)
                        chunks += 1

print()
print(f'\n{"="*50}')
print(f'Tool calls: {tool_count}')
print(f'Tools used: {tools_used}')
print(f'Token chunks: {chunks}')
