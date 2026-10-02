# MIKU PV Workshop

《我的悲伤是水做的》初音未来人物替换 MV 的完整制作仓库，收录截至《花骨朵》项目开始之前的工作；不含《花骨朵》的素材、分镜、代码或成片。

工程已展开，解压后这一层就是仓库根目录。现有角色绘稿、原片、高清基线、修复逻辑、遮罩、曝光时序、提示词、验收记录、封面和历史版本均随包保留，无需再解开第二层工程 ZIP。

## 先看成果

成片链接是还原后的本地文件路径；在 GitHub 页面先运行下文的媒体还原步骤，再从本地打开视频。封面可直接在线查看。

- [高清修正版](deliverables/videos/我的悲伤是水做的_MIKU_高清修正版.mp4)
- [九处修复前后对照](deliverables/videos/我的悲伤是水做的_九处修复前后对照.mp4)
- [高清原版与修正版对照](deliverables/videos/我的悲伤是水做的_高清原版与修正版对照.mp4)
- [初音封面](cover/我的悲伤是水做的_MIKU_封面.png)

视频为 1920×1080、24 fps、5422 帧，约 3 分 46 秒。保留原唱与伴奏，初音为画面角色；不是初音翻唱音频。34 张独立角色稿是当前采用版本。

## 本地继续做

需要 Python 3.11+、FFmpeg / FFprobe；FFmpeg 要有 libx264 编码器和 drawtext 滤镜。

在仓库根目录打开 PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe verify_repository.py
.\.venv\Scripts\python.exe continue_local.py check
```

Linux / macOS 将 Python 路径换成 `.venv/bin/python`。无需运行旧交接包的解压准备脚本：本仓库已经包含展开的 `project/`、字体与输出路径。

修改绘稿或遮罩后：

```powershell
.\.venv\Scripts\python.exe continue_local.py render
.\.venv\Scripts\python.exe continue_local.py compare
.\.venv\Scripts\python.exe continue_local.py review
.\.venv\Scripts\python.exe continue_local.py verify
```

输出到 `project/output_repair/`，会覆盖其中的工作成片和检查文件；`deliverables/` 保留原交付备份。使用已有绘稿重新合成无需生图服务。新绘稿需另行使用可用的图像生成服务，不包含生图账号或密钥。

## 制作入口

| 路径 | 内容 |
| --- | --- |
| `project/work_repair/compose_repair.py` | 当前采用的修复合成逻辑 |
| `project/work_repair/masks.json` | 头发、头部、杯子、水层等归属遮罩 |
| `project/work_repair/final_exposures.json` | 最终曝光时序 |
| `project/work_repair/delivery_manifest.json` | 34 张采用稿及源片、基线映射 |
| `project/work_repair/assets/` | 本次修复新增绘稿与提示词 |
| `project/work_hd/` | 高清旧稿、参考源帧与旧合成依赖 |
| `project/output_hd/` | 修复依赖的旧高清基线与历史输出 |
| `project/output_repair/` | 最新修正版与对照工作输出 |
| `sources/` | 低清原 MV、高清原 MV、原始伴奏 |
| `references/feedback/` | 用户指出缺陷的八张参考图 |
| `assets/history/` | 历史生成稿，非全部采用 |
| `cover/` | 原封面参考、Miku 封面、实际提示词 |
| `tools/pv-character-replacement/` | 用户提供的制作技能完整源码、参考文档与工具 |
| `docs/WORKFLOW.md` | 从分析到合成、返修与验收的流程 |
| `docs/history/` | 可恢复对话、历史交接、来源和验收记录 |
| `resources/` | 使用过的图像生成流程说明、字体与字体许可证 |
| `manifest.json` | 本仓库的逐文件 SHA-256 清单 |

## GitHub 版本与完整媒体

本仓库已上传至公开仓库 `guchang233/miku-pv-workshop`。当前上传接口无法直接接收较大的原始媒体，因此超过 8 MiB 的文件按原始字节拆成分块，存放在 `media_parts/`。文件内容没有转码、压缩或删减；路径、大小和完整 SHA-256 记录在 `media_parts/manifest.json`。

克隆后，在仓库根目录执行：

```bash
git clone https://github.com/guchang233/miku-pv-workshop.git
cd miku-pv-workshop
python prepare_media.py
```

脚本不需要网络或额外依赖，按分块恢复源视频、原始伴奏和已有成片，并核对完整 SHA-256。恢复后按上文安装依赖、检查或续做。`continue_local.py` 和 `verify_repository.py` 也会自动恢复缺失媒体。已存在的文件不会被覆盖，因此后续新渲染结果可以继续用于对照与验收。如需重新恢复全部原始媒体，可显式运行 `python prepare_media.py --force`，这会覆盖对应的八个本地文件。

此 GitHub 版本使用普通 Git 存储真实绘稿和媒体分块，没有只上传未配套数据的 LFS 指针。之前交付的完整 ZIP 包保留原始完整文件与 Git LFS 上传配置，仍可直接使用。两种版本恢复后的源片、绘稿和成片一致。

修改大型媒体时，用新的分块或另外配置 Git LFS；当前自动还原后的大文件已忽略，避免误把大型完整文件直接提交。修改合成脚本、遮罩、绘稿与流程文档可照常提交。

## 已验证范围

仓库重整展开工程、移动交接资料、补充仓库入口、拆分大媒体并替换两个比较脚本的 Linux 字体路径，未更改绘稿、遮罩或合成逻辑。已核对文件哈希、源片与基线、全部采用稿及 Python 语法；详见 `docs/REPOSITORY_CHECKS.json`。没有为此次打包重新渲染整片。

原成片已做全片解码、AAC 一致性与编码后静帧检查，未做真实播放器原速观看。对话档案包含能恢复的原文与独立摘要，不是完整原生聊天导出。历史交接中的旧路径仅作存档，当前路径以本 README 与 `docs/repository_conversion.json` 为准。

本仓库没有为原曲、角色、原 MV 或导入技能统一追加开源许可证；已有字体许可证原样保留。来源与署名见 `docs/RIGHTS_AND_SOURCES.md`。
