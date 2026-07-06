# 书源途径总汇

> 最后更新：2026-07-05 | 精校：70个精选 + aoaostar 全量3,911个 | 零重叠完美互补

---

## 📊 平台探测结果（2026-07-05 实测）

| 平台 | 状态 | 书源量 | 接口类型 | 推荐度 |
|------|:----:|--------|----------|:------:|
| **aoaostar/legado** | 🟢 活跃 | 3,911个 | 直链JSON + GitHub | ⭐⭐⭐⭐⭐ |
| **yckceo 源仓库** | 🟢 活跃 | 100+个 | Web下载(JS渲染) | ⭐⭐⭐⭐ |
| **XIU2/Yuedu** | 🟢 活跃 | 26个精选 | 直链JSON | ⭐⭐⭐⭐⭐ |
| **entr0pia** | 🟡 维护中 | 55个 | GitHub JSON | ⭐⭐⭐ |
| **Yiove 书源仓库** | 🟡 SPA | 未知 | 纯前端,无API | ⭐⭐ |
| **shidahuilang** | 🔴 失效 | - | 404 | ⭐ |

## 平台详情

### ✅ aoaostar/legado — 最大书源平台
- **网页**：https://legado.aoaostar.com（支持一键导入到 Legado）
- **GitHub**：https://github.com/aoaostar/legado
- **全量直链**：`https://legado.aoaostar.com/sources/b778fe6b.json`（18.6MB）
- **数据量**：3,911 个书源，204 个分组
- **质量分层**：约 1,511 个 A级(纯CSS) / 1,039 个含JS / 1,690 个需Cookie
- **已存档**：`004书源/raw/aoaostar_full.json` + 快照 `aoaostar_快照.md`

### ✅ yckceo 源仓库
- **地址**：https://www.yckceo.com/yuedu/shuyuan
- **书源数**：100+ 个（页面 JS 动态渲染）
- **下载方式**：浏览器打开 → 点"下载JSON" → 本地导入 Legado
- **特色**：有点赞/评论，社区活跃，版本更新及时
- **注意**：无直链 API，需浏览器手动下载

### ✅ XIU2/Yuedu
- **直链**：`https://raw.githubusercontent.com/XIU2/Yuedu/master/shuyuan`
- **特色**：26 个手工精选，质量最高，规则最稳定

### 🟡 Yiove 书源仓库
- **地址**：https://shuyuan.yiove.com/
- **性质**：纯 SPA 前端应用，无公开 JSON API
- **第三方统计脚本**：`data.apiuno.com/script.js`
- **限制**：不能通过脚本直接拉取，需浏览器操作

### 🔴 shidahuilang/shuyuan
- **jinghua.json**：HTTP 404（2026-07-05 实测）
- **替代**：https://github.com/shidahuilang/shuyuan-bak（备份仓库，未测试）

## 📊 精校结果（管道：aoaostar全量 → 精校 → 去重）

| 来源 | 原始 | 通过 | F淘汰 | A级 | B级 | 特点 |
|------|------|------|------|-----|-----|------|
| XIU2/Yuedu | 26 | 25 | 1 | 6 | 19 | 综合站点 |
| entr0pia | 55 | 45 | 10 | 9 | 36 | 轻小说/二次元/日轻 |
| aoaostar 全量 | 3,911 | 2,941 | 970 | 1,362 | 1,579 | 社区大合集 |
| **合并去重** | **3,992** | **3,011** | **981** | **763** | **1,197** | **零重叠，1,960 个独立书源** |

### 🔥 管道性能
- 精校 3,911 个：**0.4 秒**，**零 token 消耗**（纯本地 Python）
- 淘汰 F 级 970 个（24.8%），多数因 `ruleSearch.author` 为空
- 去重：142 个与现有精选重复

---

## 一、GitHub 书源仓库

### ✅ XIU2/Yuedu
- **地址**：https://github.com/XIU2/Yuedu
- **直链**：`https://raw.githubusercontent.com/XIU2/Yuedu/master/shuyuan`
- **CDN**：`https://bitbucket.org/xiu2/yuedu/raw/master/shuyuan`
- **内容**：26个精选书源（起点、晋江、笔趣阁等）
- **起点**：含「起点中文」书源，自动JS处理cookie验证
- **用法**：Legado → 网络导入 → 粘贴直链

### 🔗 shidahuilang/shuyuan
- **地址**：https://github.com/shidahuilang/shuyuan
- **分支**：`shuyuan`（非main/master）
- **文件**：`jinghua.json`（精华）、`UZ.json`（阅读3.0）
- **状态**：raw直链返回404（2026-07-05），需通过GitHub页面手动下载
- **替代**：https://github.com/shidahuilang/shuyuan-bak（备份仓库）

### 🔗 aoaostar/legado
- **地址**：https://github.com/aoaostar/legado
- **平台**：https://legado.aoaostar.com（网页版，支持一键导入）
- **说明**：GitHub仓库不含书源合集，书源在网页平台上管理
- **用法**：访问 legado.aoaostar.com → 选择书源 → 一键导入Legado

### 🔗 liufuyou/read
- **地址**：https://github.com/liufuyou/read
- **说明**：整理各大佬书源合集（自用），包含 XIU2 + shidahuilang 的汇总

---

## 二、书源平台网站

### ✅ 源仓库 (yckceo.com)
- **地址**：https://www.yckceo.com/yuedu/shuyuan
- **起点书源**：

| ID | 名称 | 特点 | 地址 |
|----|------|------|------|
| 6310 | 起点(部分可看) | 每天30章VIP，最新修复 | [链接](https://www.yckceo.com/yuedu/shuyuan/content/id/6310.html) |
| 6937 | 起点中文(按钮筛选) | m.qidian.com | [链接](https://www.yckceo.com/yuedu/shuyuan/content/id/6937.html) |
| 6442 | 起点中文 | www.qidian.com，需登录 | [链接](https://www.yckceo.com/yuedu/shuyuan/content/id/6442.html) |

- **用法**：打开页面 → 「下载JSON文件」→ 本地导入Legado
- **注意**：有跳转验证，浏览器打开后点击下载

### 🔗 Yiove 书源仓库
- **地址**：https://shuyuan.yiove.com/
- **特色**：综合书源库 + 书源校验，SPA应用
- **说明**：无JSON直链，需网页操作后导出

### ❌ source.zgqinc.gq
- **地址**：https://source.zgqinc.gq/
- **状态**：2026-07-05 返回HTML页面，JSON直链已失效

---

## 三、Legado 书源规则参考

### 规则文档
- **官方规则说明**：https://celeter.github.io/
- **社区教程**：https://mgz0227.github.io/The-tutorial-of-Legado/Rule/source.html
- **书源制作记录**：https://www.cnblogs.com/Mozhiqin/p/18703637

### 书源校验工具
- **moercat/booksource-tool**：https://github.com/moercat/booksource-tool
  - 去重、校验、清理书源JSON

---

## 四、按平台分类

### 起点中文网 (qidian.com)
| 来源 | 方式 | cookie处理 |
|------|------|-----------|
| XIU2直链 | 网络导入 | JS自动 |
| 源仓库6310 | 下载JSON导入 | WebView手动 |
| 源仓库6442 | 下载JSON导入 | 需登录 |

### 番茄小说 (fanqienovel.com)
> 见 `003搜索工具/番茄小说-API/`，需本地Python服务解码

### 其他平台（晋江、笔趣阁等）
> XIU2合集已覆盖常用平台，网络导入即可

---

## 五、导入方式速查

| 方式 | 操作 |
|------|------|
| **网络导入** | Legado → 书源管理 → ⋮ → 网络导入 → 粘贴URL |
| **本地导入** | 下载JSON → Legado → 书源管理 → ⋮ → 本地导入 |
| **二维码导入** | 源仓库扫码 → Legado自动识别 |
| **一键导入** | legado://import/bookSource?src=URL（需APP已安装） |
