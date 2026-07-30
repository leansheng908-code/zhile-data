#!/usr/bin/env python3
"""知乐分布式成长网络 - 事件聚合脚本
读取 events/ 目录下所有 JSON 文件，校验、去重、排序，输出 growth-events.json
由 GitHub Actions 定时或事件触发运行
"""
import json
import os
import glob
import hashlib
from datetime import datetime

EVENTS_DIR = 'events'
OUTPUT_FILE = 'growth-events.json'

REQUIRED_FIELDS = ['type', 'desc', 'instance']
MAX_DESC_LEN = 200
MAX_DETAIL_LEN = 500

DANGEROUS_PATTERNS = ['<script', '<img', '<a ', '<iframe', '<svg', 'onerror', 'onload', 'javascript:', '<object', '<embed']


def has_html_injection(text):
    if not isinstance(text, str):
        return False
    lower = text.lower()
    return any(d in lower for d in DANGEROUS_PATTERNS)


def sanitize_text(text):
    if not isinstance(text, str):
        return text
    return text.replace('<', '&lt;').replace('>', '&gt;')


def validate_event(event):
    if not isinstance(event, dict):
        return False, None
    for field in REQUIRED_FIELDS:
        if field not in event or not event[field]:
            return False, None
    for key, value in event.items():
        if isinstance(value, str):
            if has_html_injection(value):
                return False, None
            event[key] = sanitize_text(value)
    if len(str(event.get('desc', ''))) > MAX_DESC_LEN:
        event['desc'] = str(event['desc'])[:MAX_DESC_LEN] + '...'
    if len(str(event.get('detail', ''))) > MAX_DETAIL_LEN:
        event['detail'] = str(event['detail'])[:MAX_DETAIL_LEN] + '...'
    # 统一时间字段
    if 'time' in event and 'timestamp' not in event:
        event['timestamp'] = event['time']
    # 生成ID
    if 'id' not in event:
        raw = f"{event.get('instance','')}-{event.get('timestamp',event.get('time',''))}-{event.get('type','')}-{event.get('desc','')}"
        event['id'] = hashlib.md5(raw.encode()).hexdigest()[:12]
    return True, event


def main():
    print("=== 知乐成长事件聚合 ===")
    events = []
    seen_ids = set()
    skipped = 0

    for filepath in sorted(glob.glob(os.path.join(EVENTS_DIR, '*.json'))):
        filename = os.path.basename(filepath)
        if filename == '.gitkeep':
            continue
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            event_list = data if isinstance(data, list) else [data]
            for event in event_list:
                valid, event = validate_event(event)
                if not valid:
                    skipped += 1
                    continue
                if event['id'] in seen_ids:
                    continue
                seen_ids.add(event['id'])
                events.append(event)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  SKIP {filename}: {e}")
            skipped += 1

    events.sort(key=lambda x: x.get('timestamp', x.get('time', '')))

    output = {
        'total': len(events),
        'last_aggregated': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'events': events
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Done: {len(events)} events, {skipped} skipped")


if __name__ == '__main__':
    main()
