# 桃子阅读

基于 [Luoyacheng/legado](https://github.com/Luoyacheng/legado)（阅读Sigma）魔改的轻量阅读器。

- 应用名：`桃子阅读`
- 包名：`io.legado.peach`
- 版本：`1.0`
- APK：`taotao_app_1.0.apk`

## 已包含

- 内置 47 个精选主流小说书源（AI 全链路精校验）
- 手绘风格启动图标
- 自动更新指向 `Hippo1096/taotao-reading` 的 GitHub Releases

## 构建

```bash
./gradlew assembleRelease
```

输出：`app/build/outputs/apk/release/taotao_app_1.0.apk`

## 注意

- 首次构建需要 Android SDK / JDK 17
- Release 签名通过 GitHub Actions Secrets 注入
