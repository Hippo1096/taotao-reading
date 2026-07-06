#!/usr/bin/env python3
"""
Legado 书源全链路精校验脚本
模拟 Legado AnalyzeUrl 行为，走通 搜索→目录→正文 完整链路，
输出每源的详细结果供 AI 判断。

用法: python verify_deep.py [输入JSON] [--output 输出JSON] [--keyword 搜索词] [--workers 并发数]
默认输入: verified/精选_主流小说_实测优先.json
默认搜索词: 诡秘之主
"""

import json, os, sys, re, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote, urljoin, urlparse
from collections import Counter

import requests
from bs4 import BeautifulSoup

# 配置
TIMEOUT = 15  # 秒
DEFAULT_WORKERS = 8
KEYWORD = "诡秘之主"  # 默认搜索词， Legado 常用测试词
USER_AGENT = "Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"

# 正则：匹配 Legado 搜索 URL 末尾的 JSON 配置
URL_OPTION_PATTERN = re.compile(r',\s*(\{[^}]+\})\s*$')

# ─── 辅助函数 ────────────────────────────────────────────────

def parse_legado_url(search_url_tpl):
    """
    解析 Legado 搜索 URL 模板，返回请求参数。
    格式: "URL,{json配置}" 或 "URL"
    """
    method = "GET"
    data = {}
    extra_headers = {}
    charset = "utf-8"
    url_part = search_url_tpl
    
    m = URL_OPTION_PATTERN.search(search_url_tpl)
    if m:
        url_part = search_url_tpl[:m.start()]
        try:
            config = json.loads(m.group(1))
            method = config.get("method", "GET").upper()
            charset = config.get("charset", "utf-8")
            if config.get("headers"):
                extra_headers = config["headers"] if isinstance(config["headers"], dict) else json.loads(config["headers"])
        except:
            pass
    
    return url_part, method, charset, extra_headers


def build_legado_request(search_url_tpl, keyword, page=1, base_url=""):
    """
    模拟 Legado AnalyzeUrl 的行为，构建 HTTP 请求参数。
    返回: (method, final_url, data_dict, extra_headers, encoding_hint)
    """
    url_part, method, charset, extra_headers = parse_legado_url(search_url_tpl)
    
    # 替换模板变量
    url_part = url_part.replace("{{key}}", keyword)
    url_part = url_part.replace("{{page}}", str(page))
    
    # 处理相对 URL (使用 base_url)
    if not url_part.startswith("http"):
        if base_url:
            url_part = urljoin(base_url, url_part)
        else:
            url_part = "http://" + url_part.lstrip("/")
    
    # 构建请求体
    data = {}
    if method == "POST":
        # 从 URL 配置中提取 body 模板
        m = URL_OPTION_PATTERN.search(search_url_tpl)
        body_tmpl = ""
        if m:
            try:
                config = json.loads(m.group(1))
                body_tmpl = config.get("body", "")
            except:
                pass
        
        body_tmpl = body_tmpl.replace("{{key}}", keyword)
        body_tmpl = body_tmpl.replace("{{page}}", str(page))
        
        for pair in body_tmpl.split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                # 模拟 Legado 的 URLEncoder.encode(v, charset)
                if v:
                    try:
                        data[k] = quote(v, encoding=charset)
                    except UnicodeEncodeError:
                        data[k] = v
                else:
                    data[k] = v
    
    return method, url_part, data, extra_headers, charset


def legado_get(search_url_tpl, keyword, base_url="", timeout=TIMEOUT):
    """
    模拟 Legado AnalyzeUrl.getStrResponseAwait() 发送 HTTP 请求。
    返回: (status, final_url, body_text, encoding)
    """
    method, url, data, headers, charset = build_legado_request(search_url_tpl, keyword, base_url=base_url)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': USER_AGENT,
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    })
    
    # 合并自定义 headers
    if headers:
        session.headers.update(headers)
    
    try:
        if method == "POST" and data:
            r = session.post(url, data=data, timeout=timeout, allow_redirects=True)
        else:
            r = session.get(url, timeout=timeout, allow_redirects=True)
        
        # 编码处理 (模拟 Legado 的 charset 配置)
        if charset and charset != "utf-8":
            try:
                r.encoding = charset
            except:
                r.encoding = r.apparent_encoding or "utf-8"
        else:
            r.encoding = r.apparent_encoding or "utf-8"
        
        return r.status_code, r.url, r.text, r.encoding
    
    except requests.exceptions.Timeout:
        return 0, url, "", ""
    except requests.exceptions.SSLError:
        return -1, url, "", ""
    except Exception as e:
        return -2, url, str(e), ""


def check_search_result(html_text, encoding=""):
    """
    判断搜索结果是否命中真实书站内容。
    返回: (命中数量, 样本文本列表)
    """
    if not html_text or len(html_text) < 100:
        return 0, []
    
    try:
        soup = BeautifulSoup(html_text, 'html.parser')
    except:
        return 0, []
    
    # 提取候选文本
    candidates = []
    
    # 方法1: 找所有链接中的文本
    for a in soup.select('a[href]'):
        txt = a.get_text(strip=True)
        if txt and 4 <= len(txt) <= 100:
            candidates.append(txt)
    
    # 方法2: 找列表项中的文本
    for li in soup.select('li'):
        txt = li.get_text(strip=True)
        if txt and 4 <= len(txt) <= 100:
            candidates.append(txt)
    
    # 去重
    candidates = list(dict.fromkeys(candidates))
    
    # 判断是否为书站内容的启发式规则
    valid = []
    for txt in candidates:
        # 排除明显的非书站内容
        if any(kw in txt for kw in ['首页', '登录', '注册', '关于', '联系', '友情链接', 
                                       'Copyright', 'Powered', '备案', '站长', '广告',
                                       '上一章', '下一章', '返回', '跳转', 'javascript',
                                       '没有搜索', '搜索结果', '信息提示']):
            continue
        # 保留看起来像书名的文本
        if len(txt) >= 2:
            valid.append(txt)
    
    return len(valid), valid[:10]  # 返回前10个样本


def check_chapter_list(html_text, book_url=""):
    """
    判断目录页是否有连贯的章节列表。
    返回: (章节数量, 样本章节名列表)
    """
    if not html_text or len(html_text) < 200:
        return 0, []
    
    try:
        soup = BeautifulSoup(html_text, 'html.parser')
    except:
        return 0, []
    
    # 提取所有链接文本
    candidates = []
    for a in soup.select('a[href]'):
        txt = a.get_text(strip=True)
        if txt and 2 <= len(txt) <= 100:
            candidates.append(txt)
    
    # 去重
    candidates = list(dict.fromkeys(candidates))
    
    # 判断是否为章节名
    chapter_names = []
    for txt in candidates:
        # 排除明显的非章节内容
        if any(kw in txt for kw in ['首页', '登录', '注册', '关于', '联系', '友情链接',
                                       'Copyright', 'Powered', '备案', '广告',
                                       '上一章', '下一章', '返回', 'javascript',
                                       '最新', '推荐', '热门', '排行']):
            continue
        # 保留看起来像章节的文本
        if len(txt) >= 2:
            chapter_names.append(txt)
    
    return len(chapter_names), chapter_names[:10]


def check_content(html_text):
    """
    判断正文页是否有小说内容。
    返回: (正文字数, 样本文本)
    """
    if not html_text or len(html_text) < 200:
        return 0, ""
    
    try:
        soup = BeautifulSoup(html_text, 'html.parser')
    except:
        return 0, ""
    
    # 方法1: 找常见正文容器
    for sel in ['#content', '#chaptercontent', '.content', '#txt', '#nr1', 
                '.txt', '#booktxt', '#htmlContent', '.showtxt', 'article',
                '#BookText', '#book_text', '.novel_content', '#main_body',
                '#readcontent', '.read_content', '#booktext', '.text']:
        el = soup.select_one(sel)
        if el:
            txt = el.get_text().strip()
            if len(txt) > 100:
                return len(txt), txt[:300]
    
    # 方法2: 找所有<div>中的文本，取最长的一段
    max_len = 0
    max_txt = ""
    for div in soup.find_all('div'):
        txt = div.get_text().strip()
        if 100 < len(txt) > max_len:
            # 排除含有大量脚本/样式的div
            if '<script' not in str(div) and '<style' not in str(div):
                max_len = len(txt)
                max_txt = txt[:300]
    
    if max_len > 100:
        return max_len, max_txt
    
    return 0, ""


def deep_verify_source(source, keyword=KEYWORD):
    """
    对单个书源进行全链路精校验。
    返回: (书源信息, 校验结果字典)
    """
    name = source.get('bookSourceName', '?')
    search_url = source.get('searchUrl', '') or source.get('searchUrl', '')
    base_url = source.get('bookSourceUrl', '')
    grade = source.get('grade', '?')
    
    result = {
        'name': name,
        'grade': grade,
        'base_url': base_url,
        'search_url': search_url,
        'keyword': keyword,
        'search_ok': False,
        'search_count': 0,
        'search_samples': [],
        'chapter_ok': False,
        'chapter_count': 0,
        'chapter_samples': [],
        'content_ok': False,
        'content_length': 0,
        'content_sample': '',
        'full_chain_ok': False,
        'error': '',
        'verdict': 'unknown',
    }
    
    # ─── 第一步: 搜索 ───
    if not search_url:
        result['error'] = '无搜索URL'
        result['verdict'] = 'invalid'
        return name, result
    
    status, final_url, body, enc = legado_get(search_url, keyword, base_url=base_url)
    result['search_http'] = status
    
    if status != 200:
        result['error'] = f'搜索HTTP {status}'
        result['verdict'] = 'http_fail'
        return name, result
    
    count, samples = check_search_result(body, enc)
    result['search_count'] = count
    result['search_samples'] = samples[:5]
    result['search_ok'] = count >= 3
    
    if not result['search_ok']:
        result['error'] = f'搜索未命中 (count={count})'
        result['verdict'] = 'search_empty'
        return name, result
    
    # ─── 第二步: 目录 (从搜索结果取第一本书的 URL) ───
    # 尝试从搜索结果中提取第一个书籍链接
    try:
        soup = BeautifulSoup(body, 'html.parser')
        first_link = soup.select_one('a[href]')
        if first_link and first_link.get('href'):
            book_url = first_link['href']
            if not book_url.startswith('http'):
                book_url = urljoin(base_url, book_url)
            
            # 获取目录页
            ch_status, ch_url, ch_body, ch_enc = legado_get(book_url, '', base_url=base_url)
            result['chapter_http'] = ch_status
            
            if ch_status == 200:
                ch_count, ch_samples = check_chapter_list(ch_body, book_url)
                result['chapter_count'] = ch_count
                result['chapter_samples'] = ch_samples[:5]
                result['chapter_ok'] = ch_count >= 5
                
                if result['chapter_ok']:
                    # ─── 第三步: 正文 (取第一章) ───
                    # 从目录页提取第一个章节链接
                    ch_soup = BeautifulSoup(ch_body, 'html.parser')
                    ch_first = ch_soup.select_one('a[href]')
                    if ch_first and ch_first.get('href'):
                        ch1_url = ch_first['href']
                        if not ch1_url.startswith('http'):
                            ch1_url = urljoin(ch_url, ch1_url)
                        
                        ct_status, ct_url, ct_body, ct_enc = legado_get(ch1_url, '', base_url=base_url)
                        result['content_http'] = ct_status
                        
                        if ct_status == 200:
                            ct_len, ct_sample = check_content(ct_body)
                            result['content_length'] = ct_len
                            result['content_sample'] = ct_sample[:200]
                            result['content_ok'] = ct_len >= 200
    except Exception as e:
        result['error'] = f'目录/正文异常: {str(e)[:50]}'
    
    # ─── 综合判定 ───
    if result['search_ok'] and result['chapter_ok'] and result['content_ok']:
        result['full_chain_ok'] = True
        result['verdict'] = 'pass'
    elif result['search_ok'] and result['chapter_ok']:
        result['verdict'] = 'partial'
    elif result['search_ok']:
        result['verdict'] = 'search_only'
    else:
        result['verdict'] = 'fail'
    
    return name, result


def batch_deep_verify(sources, keyword=KEYWORD, workers=DEFAULT_WORKERS):
    """
    批量精校验。
    返回: (通过列表, 部分通过列表, 失败列表)
    """
    passed = []
    partial = []
    failed = []
    errors = []
    
    total = len(sources)
    print(f"开始全链路精校验: {total} 个书源, 关键词=\"{keyword}\", 并发={workers}")
    print("=" * 60)
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(deep_verify_source, src, keyword): src for src in sources}
        
        for i, future in enumerate(as_completed(futures), 1):
            name, result = future.result()
            
            # 分类
            if result['full_chain_ok']:
                passed.append((name, result))
            elif result['verdict'] == 'partial':
                partial.append((name, result))
            else:
                failed.append((name, result))
                errors.append(f"  ❌ {name}: {result.get('error', '?')}")
            
            # 实时汇报
            if i % 10 == 0 or i == total:
                print(f"\r[{i}/{total}] ✅{len(passed)} ⚠️{len(partial)} ❌{len(failed)}", end='', flush=True)
    
    print(f"\n\n{'=' * 60}")
    print(f"精校验完成: 通过={len(passed)}, 部分={len(partial)}, 失败={len(failed)}")
    
    return passed, partial, failed


def save_results(passed, partial, failed, output_path):
    """
    保存精校验结果到 JSON。
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    result = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'keyword': KEYWORD,
        'total': len(passed) + len(partial) + len(failed),
        'passed': len(passed),
        'partial': len(partial),
        'failed': len(failed),
        'passed_sources': [{'name': n, 'grade': r['grade'], 'base_url': r['base_url'], 
                           'search_samples': r['search_samples'],
                           'chapter_samples': r['chapter_samples'],
                           'content_sample': r['content_sample'][:200]}
                          for n, r in passed],
        'partial_sources': [{'name': n, 'verdict': r['verdict'], 'error': r.get('error', ''),
                            'search_count': r['search_count'], 'chapter_count': r['chapter_count']}
                           for n, r in partial],
        'failed_sources': [{'name': n, 'error': r.get('error', ''), 'search_http': r.get('search_http', 0)}
                          for n, r in failed],
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"结果已保存: {output_path}")


# ─── 主函数 ──────────────────────────────────────────────────

def main():
    # 解析命令行参数
    input_path = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else "verified/精选_主流小说_实测优先.json"
    output_path = sys.argv[sys.argv.index('--output') + 1] if '--output' in sys.argv else "verified/精校验结果.json"
    keyword = sys.argv[sys.argv.index('--keyword') + 1] if '--keyword' in sys.argv else KEYWORD
    workers = int(sys.argv[sys.argv.index('--workers') + 1]) if '--workers' in sys.argv else DEFAULT_WORKERS
    
    # 加载书源
    if not os.path.exists(input_path):
        print(f"错误: 文件不存在 {input_path}")
        return
    
    with open(input_path, 'r', encoding='utf-8') as f:
        sources = json.load(f)
    
    # 批量精校验
    passed, partial, failed = batch_deep_verify(sources, keyword=keyword, workers=workers)
    
    # 保存结果
    save_results(passed, partial, failed, output_path)
    
    # 打印样本
    print(f"\n{'=' * 60}")
    print(f"通过样本 (前5个):")
    for name, r in passed[:5]:
        print(f"\n  ✅ {name}")
        print(f"     搜索: {r['search_samples'][:2] if r['search_samples'] else '?'}")
        print(f"     目录: {r['chapter_samples'][:2] if r['chapter_samples'] else '?'}")
        print(f"     正文: {r['content_sample'][:100] if r['content_sample'] else '?'}")


if __name__ == '__main__':
    main()
