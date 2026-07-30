# 🌐 全球游戏热点聚合站 · MVP 原型

一个网页，点进去就能看**全球游戏热门榜 + 实时热点 + 最新攻略**（含 Twitch 直播热度、YouTube 攻略视频）。
主攻**全球视角**（全球 / 欧美 / 日本 / 韩国），含已全球发行的国产大作与出海手游。

> 设计说明文档：`全球游戏热点聚合站_设计方案.html`（在上级目录）。

---

## 一、本地运行（实时模式）

```bat
cd gamehub-prototype
python server.py
```
浏览器打开 http://127.0.0.1:8000/

- 有后端时，数据走 `/api/*` 实时聚合（Steam 官方资讯 / Reddit 讨论 / RSS 新闻 等尽力实时拉取，失败回退样例）。
- 本机局域网访问：双击 `start.bat` 会自动探测本机 IP 并绑定（适合 DHCP 环境），同网段手机/电脑可访问。

### 让攻略真正“实时”
攻略聚合了 5 类来源，联网即真实、离线回退样例：
- **YouTube 攻略视频**：免 key，联网访问 youtube.com 即真实。
- **Steam 社区指南**：免 key，按游戏 appid 抓取社区攻略列表（HTML 解析）。
- **Fextralife Wiki**：免 key，深度抓取对应游戏维基首页的词条/攻略链接。
- **Steam 官方资讯**：免 key（ISteamNews）。
- **Reddit 社区讨论**：免 key（search.json）。

---

## 二、发布到 GitHub Pages（公网）

GitHub Pages 是**纯静态托管**，不能跑 Python 后端。本项目用「快照模式」：
本机先跑后端把实时数据烘焙进 `web/data.json`，再把 `web/` 作为静态站发布。

### 方式 A：一键发布（推荐，最简单）

> **已有 GitHub 仓库？** 直接用就行——不需要新建。只要你的仓库是空的（没有冲突文件），把下面第 1 步跳过，第 2 步的 `git remote add origin` 换成你自己的仓库地址即可。也可以双击 `push_code.bat`（先把里面的 `REPO_URL` 改成你的地址），它会自动设远程并推 `main`；再双击 `publish.bat` 推 `gh-pages`。

1. 在 GitHub 新建一个空仓库（如 `game-hub`）——*已有仓库可跳过此步*。
2. 在本机执行（首次需先关联远程）：
   ```bat
   cd gamehub-prototype
   git remote add origin https://github.com/你的用户名/你的仓库.git
   git push -u origin main
   python server.py          &   :: 另一个终端启动后端（联网环境）
   publish.bat                   :: 构建快照 + 推送到 gh-pages 分支
   ```
3. 仓库 Settings → Pages → Source 选 **gh-pages** 分支 / **(root)**，保存。
4. 几分钟后访问 `https://你的用户名.github.io/你的仓库/`。

> `publish.bat` 会：① 运行 `build_snapshot.py` 生成最新快照（需后端在跑）② 用 `git subtree` 把 `web/` 推到 `gh-pages` 分支。
> 想更新数据？重新跑 `publish.bat` 即可（建议先在联网环境启动 `server.py` 以烘焙真实攻略）。

### 方式 B：GitHub Actions 自动部署（每次 push 自动重新构建+发布）

仓库已附带 `.github/workflows/pages.yml`。推送 `main` 分支后，Action 会自动：
启动后端 → 生成快照（联网环境下会拉取**真实** Steam/YouTube/Reddit 攻略）→ 部署到 Pages。

只需在仓库 Settings → Pages → Source 选 **GitHub Actions** 即可。

---

## 三、项目结构

```
gamehub-prototype/
├── server.py            # 后端聚合层（标准库零依赖，python server.py 即跑）
├── build_snapshot.py    # 把 /api/all 导出成 web/data.json 静态快照
├── start.bat            # 本机一键启动（自动探测局域网 IP，DHCP 友好）
├── push_code.bat        # 一键设远程 + 推 main 分支（代码备份）
├── publish.bat          # 一键构建快照 + 推送到 gh-pages
├── web/                 # 前端 + 静态站（GitHub Pages 发布内容）
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── data.json        # 静态快照（构建时生成）
├── .github/workflows/pages.yml   # GitHub Actions 自动部署
└── README.md
```

## 四、数据来源

| 维度 | 来源 |
|---|---|
| 🔥 热门榜单 | 内置精选样例（30 款，全球向） |
| ⚡ 实时热点 | Reddit r/Games（尽力实时，失败回退样例） |
| 📰 最新资讯 | IGN / GameSpot / Gematsu / PCGamer / VG247 / Polygon RSS |
| 🎬 YouTube 攻略视频 | YouTube 公开 search RSS（免 key，联网即真实） |
| 📘 Steam 社区指南 | Steam 社区指南列表（免 key，HTML 解析，联网即真实） |
| 📗 Fextralife Wiki | Fextralife 维基首页深度抓取（免 key，联网即真实） |
| 📘 攻略（实时化） | YouTube 视频 + Steam 社区指南 + Fextralife Wiki + Steam 官方资讯 + Reddit 讨论，按时间聚合 |

> 合规：遵守各源 ToS 与 robots.txt，标注来源与原文链接，控制请求频率。
