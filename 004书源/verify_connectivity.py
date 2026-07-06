"""
书源实测连通性校验 — 真正发 HTTP 请求验证能否访问
用法: python verify_connectivity.py [书源JSON] [--output 结果JSON]
"""
import json, sys, os
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import time

try:
    import requests
except ImportError:
    print("需要 requests 库: pip install requests")
    sys.exit(1)

TIMEOUT = 8          # 单源超时
MAX_WORKERS = 20     # 并发数
BOOK_KEYWORDS = ['小说', '章节', '目录', '阅读', 'chapter', 'novel', 'book']

def check_source(source, index, total):
    """对单个书源做连通性+内容校验"""
    name = source.get('bookSourceName', '?')
    url = source.get('bookSourceUrl', '')
    
    result = {
        'name': name,
        'url': url[:80],
        'status': 'unknown',
        'http_code': 0,
        'error': '',
        'has_book_content': False,
        'time_ms': 0,
        'index': index,
    }
    
    if not url:
        result['status'] = 'no_url'
        return result
    
    # 清理 URL（有些书源 URL 带注释前缀如 "69-明月"）
    if not url.startswith('http'):
        result['status'] = 'bad_url'
        result['error'] = f'非HTTP: {url[:50]}'
        return result
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    
    try:
        start = time.time()
        # 先 HEAD
        try:
            hr = requests.head(url, timeout=TIMEOUT/2, headers=headers, allow_redirects=True)
        except:
            hr = None
        
        # GET
        r = requests.get(url, timeout=TIMEOUT, headers=headers, allow_redirects=True)
        elapsed = (time.time() - start) * 1000
        result['time_ms'] = int(elapsed)
        result['http_code'] = r.status_code
        result['final_url'] = r.url[:80]
        
        if r.status_code >= 500:
            result['status'] = 'server_error'
            return result
        if r.status_code >= 400:
            result['status'] = 'blocked'
            result['error'] = f'HTTP {r.status_code}'
            return result
        
        # 检查内容是否像小说网站
        text = r.text[:50000] if r.text else ''
        content_len = len(text)
        result['content_len'] = content_len
        
        if content_len < 500:
            result['status'] = 'empty_page'
            result['error'] = f'页面过小({content_len}B)'
            return result
        
        keyword_hits = sum(1 for kw in BOOK_KEYWORDS if kw in text)
        if keyword_hits >= 2:
            result['status'] = 'ok'
            result['has_book_content'] = True
        elif keyword_hits == 1:
            result['status'] = 'maybe_ok'
        else:
            # 可能是重定向到首页或反爬页面
            result['status'] = 'no_book_content'
            result['error'] = f'无书站特征词'
        
        return result
        
    except requests.exceptions.Timeout:
        result['status'] = 'timeout'
        result['error'] = f'超时({TIMEOUT}s)'
    except requests.exceptions.SSLError:
        result['status'] = 'ssl_error'
        result['error'] = 'SSL证书错误'
    except requests.exceptions.ConnectionError as e:
        result['status'] = 'unreachable'
        result['error'] = str(e)[:80]
    except Exception as e:
        result['status'] = 'error'
        result['error'] = f'{type(e).__name__}: {str(e)[:80]}'
    
    return result


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if not path:
        path = os.path.join(os.path.dirname(__file__) or '.', 'verified', '精选_Hermes推荐.json')
    
    out_path = sys.argv[2] if len(sys.argv) > 2 else path.replace('.json', '_连通校验.json')
    
    with open(path, 'r', encoding='utf-8') as f:
        sources = json.load(f)
    
    total = len(sources)
    print(f"书源总数: {total}")
    print(f"并发数: {MAX_WORKERS} | 单源超时: {TIMEOUT}s")
    print(f"预计耗时: {total/MAX_WORKERS*TIMEOUT/60:.1f} 分钟\n")
    
    results = []
    done = 0
    start = time.time()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(check_source, s, i+1, total): i for i, s in enumerate(sources)}
        
        for future in as_completed(futures):
            r = future.result()
            results.append(r)
            done += 1
            # 进度
            if done % 50 == 0 or done == total:
                elapsed = time.time() - start
                rate = done / elapsed
                eta = (total - done) / rate if rate > 0 else 0
                ok_count = sum(1 for x in results if x['status'] == 'ok')
                print(f"  [{done}/{total}] {elapsed:.0f}s | 速率 {rate:.1f}/s | ETA {eta:.0f}s | ✅{ok_count}")
    
    # 分类统计
    from collections import Counter
    statuses = Counter(r['status'] for r in results)
    
    print(f"\n{'='*60}")
    print(f"实测结果 ({total} 个书源)")
    print(f"{'='*60}")
    
    STATUS_LABELS = {
        'ok':            '✅ 正常(有书站内容)',
        'maybe_ok':      '⚠️  可能正常(特征词少)',
        'no_book_content':'🔸 可达但无书站特征',
        'empty_page':    '🔸 页面过小/空白',
        'timeout':       '🔴 超时',
        'unreachable':   '🔴 不可达',
        'blocked':       '🔴 被拦截(4xx)',
        'server_error':  '🔴 服务器错误(5xx)',
        'ssl_error':     '🔴 SSL错误',
        'bad_url':       '⚫ URL格式错误',
        'no_url':        '⚫ 无URL',
        'error':         '🔴 其他错误',
    }
    
    for status, label in STATUS_LABELS.items():
        if status in statuses:
            pct = statuses[status] / total * 100
            print(f"  {label:30s} {statuses[status]:>5}  ({pct:4.1f}%)")
    
    ok_count = statuses.get('ok', 0) + statuses.get('maybe_ok', 0)
    print(f"\n  可用率: {ok_count}/{total} ({ok_count/total*100:.1f}%)")
    
    # 保存结果
    results.sort(key=lambda x: x['index'])
    output = {
        'total': total,
        'tested_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'summary': dict(statuses),
        'ok_count': ok_count,
        'details': results,
    }
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果保存: {out_path}")


if __name__ == '__main__':
    main()
