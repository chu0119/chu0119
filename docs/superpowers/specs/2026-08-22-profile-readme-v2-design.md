# chu0119 GitHub Profile README v2 设计文档

日期:2026-08-22
状态:已获用户批准
范围:在现有 `chu0119/chu0119` profile 仓库基础上扩充完善(方案 A:自绘管线扩展),不改变仓库与 workflow 架构。

## 需求决策记录

| 决策点 | 用户选择 |
|--------|---------|
| 视觉方向 | 保留终端/赛博朋克风格并精修 |
| 方案 | A:自绘管线扩展,零外部服务依赖 |
| 语言 | 中英双语(英文为主、中文对照) |
| 新增板块 | 项目卡片升级 / 成就连击区 / 研究焦点区 / 联系方式区(全选) |
| 联系邮箱 | chu0119@foxmail.com |

## 布局(自上而下)

1. **Banner v2**(SVG 动画)— 终端窗口多命令打字循环:`whoami → nmap -sV target → ./exploit`,保留霓虹青 `#00E5FF`/品红 `#FF2E97` 渐变描边与 glow 滤镜
2. **身份区** `$ cat identity.txt` — 英文定位一行 + 中文对照一行
3. **研究焦点区** `$ cat focus.txt`(新增)— 3 条当前状态:SRC 漏洞挖掘中 / 安全工具开发中 / AI 安全自动化探索,中英对照
4. **武器库 v2** — 6 个项目双列卡片(替代原 4 行表格):fscan-toolkit、zhidun、DarkForest-Hunter、xingchuan-ti、tg-monitor-v2、edusrc-hunter;每格含可点击项目名 + 英文一句话简介 + star 徽章 + 语言徽章(Markdown 实现,保证链接可点)
5. **技术栈** — 保留现有三组徽章(Languages / Security / AI & Automation)
6. **数据面板** — 保留现有 `assets/stats.svg`、`assets/langs.svg`
7. **成就面板**(新增)— `assets/achievements.svg`:终端风 "ACHIEVEMENTS UNLOCKED" 徽章网格,含总星数/仓库数/连击(current+longest)/年度贡献数;由 `generate_stats.py` 用已有 GraphQL 数据自绘,零外部依赖
8. **实时动态** — 保留 `<!-- BEGIN ACTIVITY -->` 自动更新块
9. **联系区** `$ ping me`(新增)— mailto 邮箱 badge + GitHub badge
10. **访客计数器** — 保留页脚 Komarev 计数

## 视觉规范

- 配色延续 v1:青 `#00E5FF` + 品红 `#FF2E97` + 底色 `#0D1117`,辅助灰 `#8B949E`
- 区块标题统一 `$ command` 终端命令风格,等宽字体
- 动画仅允许存在于 SVG 内部(GitHub README 硬限制)
- 成就面板格子使用同款霓虹描边卡片,与整体风格一致
- 成就面板图标点缀色:金星 `#FFC94D` 与绿 `#27C93F`(与 banner `[+]` 同款绿)为认可用色

## 技术实现

1. `README.md`:按新布局重写(双语文案)
2. `assets/banner.svg`:重绘为多命令打字循环动画
3. `scripts/generate_stats.py`:新增 `render_achievements()`,复用 `fetch_stats()` / `fetch_streak()` 已有数据,输出 `assets/achievements.svg`
4. workflow 不新增:`generate-stats.yml` 每日任务顺带产出成就图
5. 失败策略不变:脚本异常保留旧 SVG,仅在有 diff 时 commit

## 验收

- 推送后 Actions 运行绿色,`achievements.svg` 正常产出
- 线上抓取渲染检查:banner 动画、卡片排版、徽章显示正常
- 双语文案无乱码,链接全部可点击

## 风险

- SVG 内 emoji 渲染依赖查看端字体,成就面板图标改用自绘矢量图形兜底
- star 数为快照数据,每日 Actions 刷新,存在最长 24h 延迟
