# 本工程的续做约定

- 本仓库只收录《花骨朵》之前的《我的悲伤是水做的》制作工作。
- 先读 `README.md`、`docs/WORKFLOW.md` 与 `project/work_repair/delivery_manifest.json`。
- 当前主入口是 `continue_local.py` 和 `project/work_repair/`。`work_hd/` 是旧基线依赖；不要仅重跑旧高清合成作为最终修正版。
- 修改 MV 时遵循 `tools/pv-character-replacement/skills/pv-character-replacement/SKILL.md`。当前案例保留原镜头、原时序、字幕、道具、鸟群和音轨，只替换角色。新的用户指令可另行改变范围。
- 工程代码与绘稿已经展开；大媒体运行 `python prepare_media.py` 即可按原始字节自动还原；历史交接文档中的 `prepare_local.py` 是旧包准备步骤，不适用于当前仓库。
- 人物绘稿的采用关系由清单决定；历史绘稿不是默认采用稿。新稿必须写入实际资产目录并更新清单和生成记录。
- 优先检查头发补色与遮挡、脸部水面归属、杯子边缘、脖子及衣领、码头真实三稿曝光和钓鱼淡出尾部。
- 修后执行适用的合成、对照、静帧、全片解码和音轨校验。实际做过静态检查就报告静态检查，不得声称做过播放器原速观看。
- 字体使用随包 `project/local_support/DejaVuSans.ttf`；代码以文件所在位置或仓库根目录定位，不重新引入旧临时绝对路径。
- 更新文件后可运行 `python verify_repository.py --refresh` 更新当前快照清单，再运行 `python verify_repository.py` 检查。保留原交付备份、历史说明与原有署名。
