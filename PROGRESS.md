# 项目进度快照（2026-11-04 15:00 更新）

> 本文件是沙箱回收后的**恢复锚点**。上一份概要中的"CC 扩展发不出数据"问题**已经解决**，v2 成片**已完成并推送**。此文档记录最终状态 + 完整环境恢复步骤。

## 一、当前状态总览

| 事项 | 状态 |
| --- | --- |
| 12 行日奈配音（F5-TTS 克隆） | ✅ 完成，`vo/wavs/l01-l12.wav`（与 workspace/vo_out md5 一致） |
| Competitive Companion 抓题管线 | ✅ **已打通**（曾卡壳，见下文证据链） |
| 6 段实拍（install/grab/run/detail/lang/teaser） | ✅ `footage2/` |
| v2 成片 + 字幕 + 简介 | ✅ `final/final_mv.mp4`、`final/subs.ass`、`final/视频简介.txt` |
| BGM（用户上传 2:19） | ✅ `assets/bgm.m4a` |
| 环境快照（本仓库 `env/`） | ✅ 2026-11-04 新增，见第三节 |

## 二、CC 扩展问题的结论（重要，避免重走弯路）

**问题**：点击扩展 / Ctrl+Shift+U 后插件收不到数据，parse 在 content script 中报错但被 `.catch(noop)` 吞掉。

**已解决**。修复后给 `content.js` / `background.js` 注入了调试日志（`CC_ENTRY`、`BG_MSG`、`BG_SENDTASK_START`、`PARSE_ENTRY`、`SEND_BEGIN`、`SEND_MSG_SENT`、`TASK_SENT_OK`、`PARSE_DONE`、`__sink`），证据链三环齐全：

1. **页面解析 OK**：`env/logs/plog3.txt` → `GPTU_MATCHED 95 LuoguProblemParser`（洛谷页解析器命中）
2. **后台发送 OK**：`env/logs/bglog.txt` → 三次完整 `PARSE_ENTRY → SEND_BEGIN → SEND_MSG_SENT → TASK_SENT_OK → PARSE_DONE`
3. **插件接收 OK**：`env/logs/aca-companion.log` → 12:36–13:15 共 **7 次成功 incoming**（P17831 crystal，tests=2，建文件到 /home/z/demo/cp/）

**当前可工作的扩展**在 `env/cc_ext/`（v2.65.0，端口 12345 已通过扩展 storage 的 `customPorts` 写入；默认端口列表里没有 12345，必须保留 storage 或重新设置）。Chrome profile 里已固化该配置，见 `env/chromeprof/`。

## 三、环境恢复指南（新沙箱从零到可拍摄）

### 3.1 目录约定（本仓库 = workspace/mv_repo2）
```
env/cc_ext/            可工作的 CC 扩展 v2.65.0（含调试日志）
env/plugin-source/     Algorithm Competition Assistant 插件完整源码
env/sublime-app/       Sublime Text 4192（opt+usr 布局，51M）
env/sublime-config/    ~/.config/sublime-text 关键部分（Installed Packages
                       含 ACA.sublime-package + Package Control；User 设置；Log）
env/x11-tools/         xdotool 等 X11 工具
env/chromeprof/        Chrome profile（已固定扩展图标、customPorts=12345、
                       洛谷可访问；ShaderCache 等已剔除）
env/demo/              /home/z/demo 快照（cp/ + ref/，exe 已删）
env/logs/              调试日志（plog3 / bglog / aca-companion / chrome）
scripts/               全部拍摄与调试脚本（90+ 个）
tools/bootstrap_voice.sh  TTS 环境一键恢复（模型较大，不随仓库走）
assets/                hina_ref.m4a（参考音频）、ref_w1_24k.wav、bgm.m4a、demo 素材
docs/                  v2_requirements.md / video_script.md / voice_pipeline.md
final/                 成片 v2 + 字幕 + 简介
footage2/              6 段实拍
```

### 3.2 恢复步骤
1. **X 环境**：`Xvfb :99 -screen 0 1920x1080x24`（scripts/ensure_x.sh / fresh_x.sh）
2. **Sublime**：
   ```bash
   mkdir -p ~/apps && cp -r env/sublime-app ~/apps/sublime
   ~/apps/sublime/opt/sublime_text/sublime_text --command new_window   # 或正常启动
   mkdir -p ~/.config/sublime-text
   cp -r env/sublime-config/Installed\ Packages env/sublime-config/Packages env/sublime-config/Log ~/.config/sublime-text/
   ```
   插件无需重装 —— 已在 Installed Packages 里（正是"Package Control 安装"演示的形态）。设置含字体/无边框等拍摄配置。
3. **Chrome（Testing 131.0.6778.204，未随仓库，339M）**：
   ```bash
   # 下载：https://googlechromelabs.github.io/chrome-for-testing/  → chrome-linux64 131.0.6778.204
   # 或: https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.204/linux64/chrome-linux64.zip
   mkdir -p ~/apps && unzip chrome-linux64.zip -d ~/apps
   ~/apps/chrome-linux64/chrome --user-data-dir=/tmp/chromeprof \
     --load-extension=$REPO/env/cc_ext --no-sandbox \
     --window-position=0,0 --window-size=1920,1080 https://www.luogu.com.cn/problem/P17831
   ```
   首次可直接 `cp -r env/chromeprof /tmp/chromeprof`，端口 12345 / 固定图标 / 会话全部还原，无需手动配置扩展。
4. **插件监听验证**：`curl -X POST http://localhost:12345/ -d '<problem json>'`，看 `~/.config/sublime-text/Log/aca-companion.log` 出现 `incoming`。
5. **TTS（仅当需要重新生成配音时）**：`bash tools/bootstrap_voice.sh`（F5-TTS v1 CPU，参考 `scripts/hina_tts.py`，参考音频截取 hina_ref.wav 39.16–44.0s；12 行已定稿，一般不需要再生成）。
6. **拍摄脚本入口**：`scripts/takeB.py`、`scripts/run_take.py`、`scripts/record_demo.py`；对轴/合成：`scripts/assemble_final.py`、`scripts/final_encode.py`、`scripts/chunk_burn.py`。演示目录每次拍摄前清空 `/home/z/demo/cp`。

### 3.3 Chrome 扩展端口机制（排查备忘）
`background.js` → `getHosts()` = 默认端口 `[1327,4244,6174,10042,10043,10045,27121]` ∪ `config.get("customPorts")`。**12345 不在默认列表**，来自扩展 storage（`env/chromeprof/Default/Local Extension Settings/ckjfmlpnpcpncplbcmipoolchbpjcbfg/`）。若 chromeprof 丢失：扩展选项页把 12345 加入 custom ports 即可，或改插件监听端口。

## 四、制作规则备忘（v2 已落实，改片时沿用）
- 配音=日奈克隆声；BGM=assets/bgm.m4a；无音效、无放大聚焦、无图标动画
- 口播不读题目名/插件名（"这个插件/这道题"），**字幕显示实名**（"Algorithm Competition Assistant"、"crystal"）
- 结尾实话实说：基于 FastOlympicCoding 开发、参考 cph-ng / FastOlympicCodingHook；已被官方 Package Control 收录（真）
- 演示代码逐字保留（含 `// (^. .^)ʃ` 注释、Tab 缩进），DejaVu Sans Mono，贴编辑器最下方
- 鼠标全程可见（x11grab 原生捕获，已验证）
- 中英文界面各演示一遍；开头演示 Package Control 安装

## 五、其他
- `/home/z/my-project/.git`（3.0G 无 remote 的本地死仓）已于本次清理删除；`workspace/apps`（0.7G 重复副本）已删；`/tmp/my-project`（3.8G 过期镜像）已删。仓库唯一备份 = 本仓库（origin 已同步）。
- Chrome 二进制（339M）与 F5-TTS 模型/venv（约 2.8G）未入库，按 3.2 节恢复。
- `scripts/` 内多数 `.log` 仅为过程日志，可忽略。
