# AGENT_HANDOVER_LOG

- 创建时间：2026-07-05
- 最后更新：2026-07-06（简化 CI + 无签名构建可用）
- 项目：070503-阅读Sigma源码（桃子阅读魔改版）
- 基础：Luoyacheng/legado（阅读Sigma）→ fork → Hippo1096/taotao-reading
- 远端魔改仓库：https://github.com/Hippo1096/taotao-reading.git
- 上游原版：https://github.com/Luoyacheng/legado.git（已设 upstream remote）

## 项目来源合并日志

### 2026-07-06 — 合并 070502 项目
- 老项目 `070502-阅读Legado源码` 已移入 `00归档/070502-阅读Legado源码/`
- 提取并归入本项目的资源：
  - `004书源/` — 1,960个精校书源 + 全套校验工具
  - `003搜索工具/` — 番茄小说 API 搜索工具（fanqienovel-API-server）

## 魔改内容

### 1. 应用信息
- 应用名：桃子阅读
- 包名：`io.legado.peach`（release 版实际后缀 `io.legado.peach.release`）
- APK输出：`taotao_app_1.0.apk`

### 2. 内置书源
- 源文件：app/src/main/assets/defaultData/bookSources.json
- 内容：47个精选主流小说源（从 070502 项目导入）
- 来源：AI全链路精校验（搜索→目录→正文）

### 3. 图标
- 手绘风格：一本打开的小书 + 桃子
- 路径：app/src/main/res/mipmap-*/ic_launcher.png
- 密度：mdpi/hdpi/xhdpi/xxhdpi/xxxhdpi

### 4. 自动更新
- GitHub更新：指向 Hippo1096/deploy/releases
- Gitee更新：指向 Hippo1096/deploy/releases
- 注意：需要在 Hippo1096/deploy 仓库创建Release并上传APK

## 构建说明

### 本地构建
```bash
cd 070503-阅读Sigma源码
./gradlew assembleRelease
```
输出：`app/build/outputs/apk/release/taotao_app_1.0.apk`
需要 JDK 17 + Android SDK，签名需本地提供 jks。

### GitHub Actions 构建（推荐）
Workflow：`.github/workflows/release.yml`
- 手动触发（workflow_dispatch），选 `main` 分支
- CI 内 `keytool` 自动生成临时签名，**不需要任何 Secrets**
- 构建完成后在 Actions 页面下载 artifact APK

## 待继续

- [ ] 去 GitHub Actions 手动触发首次构建 → <https://github.com/Hippo1096/taotao-reading/actions/workflows/release.yml>
- [ ] 下载 APK 安装测试
- [ ] 验证内置书源是否正常搜索/阅读
