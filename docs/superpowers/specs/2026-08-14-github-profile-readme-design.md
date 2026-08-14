# chu0119 GitHub Profile README 设计文档

日期:2026-08-14
状态:已获用户批准
范围:创建 `chu0119/chu0119` profile README 仓库,终端黑客风 + 霓虹点缀(A+B 融合),含自动动态更新;另更新置顶项目(单独确认)。

## 需求决策记录

| 决策点 | 用户选择 |
|--------|---------|
| 风格 | 黑客/安全风 + 霓虹标题融合(终端骨架) |
| 动态内容 | GitHub 统计卡片、成就/连击徽章、访客计数器、自动最新项目动态(全选) |
| 语言 | 英文为主 |
| 身份定位 | Security Researcher & Tool Builder |

## 布局(自上而下)

1. **霓虹终端标题** — 内嵌 SVG:仿终端窗口栏,青色 #00E5FF 霓虹描边,打字机动画 `$ whoami`
2. **身份定位** — 终端输出样式 3 行
3. **精选武器库** — 4 个项目 2×2:zhidun / fscan-toolkit / DarkForest-Hunter / xingchuan-ti
4. **技术栈** — badge 分组:Languages / Security / AI & Automation
5. **数据面板** — github-readme-stats(tokyonight 主题)+ streak + top langs
6. **成就** — github-profile-trophy
7. **实时动态** — GitHub Actions 每日更新,写入 `<!-- BEGIN ACTIVITY -->` 块
8. **访客 & 联系** — Komarev 计数器 + 联系 badge

## 视觉规范

- 深浅模式自适应;深色青色霓虹 + 品红点缀,浅色降级为深青/深红
- 动画仅限 SVG 内部(GitHub 不支持 README CSS animation)
- 等宽字体仅用于标题 SVG 和终端样式段落

## 内容文案(英文为主)

- 定位:`Security Researcher & Tool Builder` — focused on offensive security, threat intelligence, and AI-powered automation.
- 精选项目取 star 最高的 4 个自建项目(排除 fork)。

## 技术实现

1. gh CLI 创建 public 仓库 `chu0119/chu0119`(本地已登录,token 有 repo + workflow 权限)
2. README.md:全文 + 内嵌 SVG 标题
3. `.github/workflows/update-activity.yml`:每日 UTC 00:17 跑 Python 脚本拉取最近 push 仓库与 star 增量,替换注释块内内容,有变化才 commit
4. 推送后线上抓取验收

## 置顶项目更新(需单独点头)

fscan-toolkit / DarkForest-Hunter / zhidun / tg-monitor-v2 / xingchuan-ti / qingshaonian

## 风险

- 第三方 stats 服务偶发限流,卡片短暂空白,刷新恢复
- 访客计数器为外部服务数据
- GitHub README 样式硬限制:动画只能内嵌 SVG
