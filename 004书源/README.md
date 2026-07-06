# 004书源 — Legado 阅读APP 书源管理

> 更新：2026-07-05 | **1,960 个去重书源** | 原精选 + aoaostar 全量合并 | A级 763 个 (39%)

## 目录结构

```
004书源/
├── README.md                     ← 本文件
├── SOURCES.md                    ← 书源途径总汇 + 平台探测报告
├── validate_sources.py           ← 精校脚本（A/B/F 分级）
├── raw/                          ← 原始拉取（保留来源）
│   ├── XIU2_Yuedu.json           26个（GitHub 直链）
│   ├── XIU2_Yuedu_cdn2.json      CDN 备份
│   ├── entr0pia_bookSource.json  55个（GitHub）
│   ├── aoaostar_full.json        3,911个全量（18.6MB）🔥
│   └── aoaostar_快照.md          全量快照说明
└── verified/                     ← 精校后可导入
    ├── 书源分类索引.md             📋 全量分类总表
    ├── 书源分类索引.json           📋 结构化索引
    │
    ├── 🔥 原精选分组（7个，代码前缀 精选_）
    │   ├── 精选_起点_qidian.json      1个
    │   ├── 精选_番茄_fanqie.json      1个
    │   ├── 精选_笔趣阁_biquge.json    21个
    │   ├── 精选_轻小说_lightnovel.json 7个（全A级🟢）
    │   ├── 精选_API_api.json          3个
    │   ├── 精选_垂直_vertical.json    3个
    │   └── 精选_综合_others.json     34个
    │
    ├── aoaostar/                  🔥 大合集（12个分组）
    │   ├── ALL_合并全量.json       全量 2,939 个单文件
    │   ├── aoaostar_已校验.json    1,636 个（社区校验通过）
    │   ├── aoaostar_其他综合.json   410 个
    │   ├── aoaostar_精选.json      169 个（手工精选）
    │   ├── aoaostar_小说综合.json   116 个
    │   ├── aoaostar_漫画.json       68 个
    │   ├── aoaostar_笔趣阁.json     63 个
    │   ├── aoaostar_正版.json       23 个
    │   └── ... 等
    │
    └── _legacy/                   旧版备份
```

## 📊 数据流水线

```
aoaostar 全量 (3,911)
    │
    ▼ validate_sources.py (0.4秒, 0 token)
    │
    ├── A级: 1,362
    ├── B级: 1,579
    └── F级: 970 → 淘汰
    │
    ▼ 有效: 2,941
    │
    ▼ 与现有精选去重 (142个重复)
    │
    ▼ 新增: 2,799 → 总计: 1,960 个独立书源
    │
    ▼ 按分组输出 → verified/
```

## 使用方式

### 快速上手（推荐）
Legado → 书源管理 → 本地导入 → `verified/aoaostar/ALL_合并全量.json`
> 全量 2,939 个，导入后按分组筛选

### 按需导入
1. **只想看轻小说** → `精选_轻小说_lightnovel.json`（7个全A级）+ `aoaostar/ALL_合并全量.json`
2. **只看网文** → `精选_笔趣阁_biquge.json` + `精选_综合_others.json`
3. **只要靠谱的** → `aoaostar/aoaostar_已校验.json`（1,636个社区校验通过）

### 网络导入（XIU2 直链）
```
https://raw.githubusercontent.com/XIU2/Yuedu/master/shuyuan
```

## 精校脚本

```bash
# 校验单个文件
python validate_sources.py raw/aoaostar_full.json

# 性能：3,911 个仅需 0.4 秒，零 token 消耗
```
