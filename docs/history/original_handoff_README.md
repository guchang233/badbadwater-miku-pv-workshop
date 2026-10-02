# 《我的悲伤是水做的》MIKU 本地续做包

这是本项目当前保存的素材、成片、历史绘稿、可复现工程与对话交接资料。最新主片为 `02_videos/我的悲伤是水做的_MIKU_高清修正版.mp4`，最新封面为 `06_cover/我的悲伤是水做的_MIKU_封面.png`。

## Windows 本地启动

先完整解压此包。建议放在路径较短、磁盘空间充足的目录。在解压后的 `miku_handoff` 文件夹打开 PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe prepare_local.py
.\.venv\Scripts\python.exe continue_local.py check
```

要求 Python 3.11 或以上，以及能在 PATH 中找到的 `ffmpeg` 和 `ffprobe`。FFmpeg 必须包含 `libx264` 编码器和 `drawtext` 滤镜。安装依赖需要网络；使用已有绘稿重新合成不需要生图服务。macOS/Linux 可把 Python 路径换成 `.venv/bin/python`。

准备脚本会解开原始修复工程到 `project/`，恢复成片位置，解开用户提供的技能包，并把对照脚本里的 Linux 字体路径改为随包字体的相对路径。原工程 ZIP 保留不变，修改前脚本另存为 `.py.original`。已经存在的工程代码和绘稿不会被准备脚本覆盖。

不改素材时无需重新渲染，直接查看已有成片。修改后运行：

```powershell
.\.venv\Scripts\python.exe continue_local.py render
.\.venv\Scripts\python.exe continue_local.py compare
.\.venv\Scripts\python.exe continue_local.py review
.\.venv\Scripts\python.exe continue_local.py verify
```

重新输出到 `project/output_repair/`；这四个步骤会覆盖该工作目录中的对应成片、检查图和检查报告。`02_videos/` 中的交付备份保持不变。`review` 生成静帧检查板，仍需实际查看；脚本本身不能代替人工审美验收或播放器观看。

## 文件位置

| 位置 | 内容 |
| --- | --- |
| `00_docs/` | 可恢复的对话原文、早期会话摘要、工程交接状态、下一位 Agent 提示、文件来源清单 |
| `01_sources/` | 最早低清原 MV、高清原 MV、原始伴奏 WAV |
| `02_videos/` | 最新修正版、全片原版对照、九处修复对照、此前转场检查短片 |
| `03_refs/` | 用户发来的八张问题参考图，保留原文件名 |
| `04_project/` | 原封不动的高清修复工程 ZIP；含旧高清基线、34张当前采用稿、此前绘稿、遮罩、源帧、曝光时序、代码、生图记录和验收图 |
| `05_skills/` | 用户提供的 PV 技能原 ZIP、用过的内置图像生成技能说明、对照字体和许可证 |
| `06_cover/` | 封面原始参考、刚生成的 Miku 封面、完整生成提示词 |
| `07_historical_images/` | 本 MV 项目已保存的历史生图素材与版本，便于追回旧方案；采用关系以工程清单为准 |
| `manifest.json` | 本包逐文件 SHA-256、大小和来源 |
| `verify_package.py` | 检查解压后的交接包是否缺失或损坏 |

工程 ZIP 本身含269个条目，已检验完整性。独立素材目录保留了89个已保存文件和当前封面，未把其他项目的文件混入。历史图不等于当前采用图，当前采用列表是 `project/work_repair/delivery_manifest.json`。

## 对话记录范围

`00_docs/对话记录_可恢复原文.md` 收录当前能准确恢复的消息和最近封面对话。更早会话已被系统压缩，检索只恢复了约束摘要，无法取得完整逐字导出；摘要独立存放在 `00_docs/早期会话摘要.md`，没有冒充原文。本包也不是可直接导入 Codex CLI 的原生会话数据库；给本地 Agent 阅读交接提示即可接着做。没有包含账号凭据、环境密钥、其他会话或系统内部指令。

## 当前成果及限制

视频为1920×1080、24fps、5422帧；原始洛天依唱声与伴奏保留。修的是画面人物，不是换声翻唱。用户反馈九处已返修，另补齐钓鱼人物在1:06淡出尾部的替换。已做全片解码、原AAC一致性、编码后静帧与边界检查，尚未进行真实播放器原速观看；请在本地补完这一步。

封面以用户给的灰蓝色标题封面为参考，已把右侧角色换成初音双马尾。PNG 保留生成工具的原生尺寸，未强行改成1920×1080；若用于平台封面，后续可另导出平台要求尺寸。

本地工作前先读 `00_docs/本地续做交接.md`。不要从旧高清稿的杯子矩形遮罩、两稿码头误判或短钓鱼曝光重新开始。
