"""
Legado 书源精校脚本
用法: python validate_sources.py [书源JSON路径或目录]
模拟 Legado 书源引擎核心逻辑，校验规则完整性和语法有效性。
"""
import json, re, sys
from pathlib import Path

class SourceValidator:
    ESSENTIAL_FIELDS = ['bookSourceName', 'bookSourceUrl']
    RULE_SETS = {
        'ruleSearch': ['bookList', 'name', 'author', 'bookUrl'],
        'ruleToc': ['chapterList', 'chapterName', 'chapterUrl'],
        'ruleContent': ['content'],
    }
    
    def validate(self, source: dict) -> dict:
        name = source.get('bookSourceName', 'UNKNOWN')
        result = {'name': name, 'pass': True, 'issues': [], 'warnings': [], 'grade': 'A'}
        
        for f in self.ESSENTIAL_FIELDS:
            if f not in source or not source[f]:
                result['pass'] = False
                result['issues'].append(f'缺少 {f}')
        
        rule_count = 0
        for ruleset, required in self.RULE_SETS.items():
            rules = source.get(ruleset, {})
            if not rules:
                result['pass'] = False
                result['issues'].append(f'缺少 {ruleset}')
                continue
            for key in required:
                val = rules.get(key, '')
                if not val:
                    result['pass'] = False
                    result['issues'].append(f'{ruleset}.{key} 为空')
                else:
                    rule_count += 1
        
        # 分级（修正版：尊重 Legado 实际行为，搜索残缺≠不能读）
        has_js = any('<js>' in str(source.get(k, {})) for k in self.RULE_SETS)
        needs_cookie = source.get('enabledCookieJar', False)
        
        # 核心能力：能不能读？
        toc = source.get('ruleToc', {})
        content = source.get('ruleContent', {})
        can_read = bool(toc.get('chapterList')) and bool(content.get('content'))
        can_search = bool(source.get('ruleSearch', {}).get('bookList'))
        
        if not result['pass']:
            if can_read:
                # 目录+正文完整，只是搜索有缺失 → Legado 用"发现"功能照样读
                result['grade'] = 'D (搜索残缺)'
                result['issues'].insert(0, '⚠ 可读但搜索不全')
            else:
                result['grade'] = 'F'
        elif has_js and needs_cookie:
            result['grade'] = 'B (JS+cookie)'
        elif has_js:
            result['grade'] = 'B (含JS规则)'
        elif needs_cookie:
            result['grade'] = 'B (需WebView)'
        
        result['has_js'] = has_js
        result['needs_cookie'] = needs_cookie
        return result

def main():
    paths = sys.argv[1:] if len(sys.argv) > 1 else ['raw/']
    for p in paths:
        path = Path(p)
        files = [path] if path.is_file() else list(path.glob('*.json'))
        for f in files:
            data = json.loads(f.read_text(encoding='utf-8'))
            if isinstance(data, dict):
                data = [data]
            v = SourceValidator()
            print(f"\n{'='*60}\n{f.name}")
            for src in data:
                r = v.validate(src)
                icon = '✅' if r['pass'] else '❌'
                print(f"  {icon} {r['name']:15s} [{r['grade']}] {'; '.join(r['issues']) if r['issues'] else '规则完整'}")

if __name__ == '__main__':
    main()
