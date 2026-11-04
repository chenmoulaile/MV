# MV v2 需求清单（最终版，2026-11-01）

## 素材
- `assets/hina_ref.m4a`：空崎日奈中文语音参考（5:36，用于声音克隆）— 用户上传，不可再生
- `assets/bgm.m4a`：BGM（2:19）— 用户上传，直接使用，不换

## 用户最新指令（合并全部历史要求）
1. 配音 = 空崎日奈的中文声音（用参考音频克隆）
2. BGM = 用户提供的音乐（assets/bgm.m4a）
3. 用 Competitive Companion 浏览器扩展抓取样例，并**演示怎么抓**（Chrome 打开题目页 → 点扩展 → Sublime 建文件）
4. 宣传大片质感 + 轻度口语
5. **以插件开发者身份**发布，不是小编安利腔
6. 鼠标每一秒都要出现（全程可见）
7. 中英文界面各演示一遍
8. 开头演示怎么下载（Package Control 搜索 → 安装成功），成功后才继续
9. 结尾实话实说：插件好处、基于什么开发（FastOlympicCoding 的 fork）、参考了什么（cph-ng 显示方式、FastOlympicCodingHook 浏览器导入思路）
10. 口播不读题目名/插件名 → 用"这个插件/这道题"代称；**字幕显示实名**（Algorithm Competition Assistant / crystal）
11. 无任何特殊音效
12. 无放大/聚焦特效
13. 删掉非插件图标；不强调开源
14. 弃用旧片头片尾界面，另想新方式
15. 结尾/简介说"已被官方 Package Control 收录"
16. 演示代码逐字保留（含 // (^. .^)ʃ 注释、Tab 缩进、freopen 注释），DejaVu Sans Mono，贴在编辑器最下方
17. 题目：CSP-S 2026 T1 crystal（洛谷 P17831 已抓取，demo_snapshot/tests 有真实样例）

## 技术要点
- 插件：Sublime Text 4 插件 Algorithm Competition Assistant
  - 安装：Package Control: Install Package → 搜 "Algorithm Competition Assistant"
  - 语言切换：命令面板 "Switch to English" / 中文
  - Companion：Sublime 启动自动监听 12345 端口；扩展端口列表需含 12345
    - Ctrl+Alt+L：一题一文件（新建 <题名>.cpp 带样例）
    - Ctrl+Alt+F：送进当前文件并运行
  - freopen 题：View → Algorithm Competition Assistant → This problem reads/writes files
  - Ctrl+Alt+B 运行测试，卡片显示 verdict/用时/内存，详情页有输入/期望/实际/差异
- 录制：Xvfb + ffmpeg x11grab，鼠标指针强制常显（xcursor 或 GD_CURSOR 方案）
- 结尾致谢口径：基于 FastOlympicCoding（Jatana）开发；判题显示参考 cph-ng（langningchen）；浏览器导入参考 FastOlympicCodingHook（DrSchwad）

## 交付
- 成片 → final/ 目录 + 推送本仓库（沙箱 2h 重置，每阶段必推）
