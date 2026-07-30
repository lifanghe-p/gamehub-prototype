// 全球游戏热点聚合站 · 原型前端逻辑
const state = { region: "", platform: "", genre: "", q: "" };
const $ = (s) => document.querySelector(s);

async function getJSON(url) {
  const r = await fetch(url);
  return await r.json();
}

function fmtPlayers(n) {
  if (n >= 1e8) return (n / 1e8).toFixed(1) + "亿";
  if (n >= 1e4) return (n / 1e4).toFixed(1) + "万";
  return n;
}

function renderGames(list) {
  const el = $("#games");
  el.innerHTML = list.map((g, i) => {
    const tags = [g.region, ...(g.platform || []), g.genre, ...(g.tags || [])]
      .slice(0, 5)
      .map(t => `<span class="tag ${t.startsWith("中国") || t === "全球" || t === "日本" || t === "欧美" ? "r-" + t : ""}">${t}</span>`)
      .join("");
    const tr = g.trend >= 0 ? `<span class="trend up">▲ ${g.trend}%</span>` : `<span class="trend down">▼ ${Math.abs(g.trend)}%</span>`;
    return `<div class="gcard">
      <span class="rank">#${i + 1}</span>
      <div class="row1"><span class="emoji">${g.emoji || "🎮"}</span>
        <div><div class="nm">${g.name}</div><div class="en">${g.name_en || ""}</div></div></div>
      <div class="meta">${tags}</div>
      <div class="stats">
        <div><div class="score">${g.hotScore}<small> 热度分</small></div>
          <div class="players">约 ${fmtPlayers(g.players)} 活跃 · ${tr}</div></div>
      </div></div>`;
  }).join("");
}

function renderTrends(list) {
  const max = Math.max(...list.map(t => Math.abs(t.momentum || 0)), 1);
  $("#trends").innerHTML = list.map(t => {
    const m = t.momentum || 0;
    const w = Math.min(100, Math.abs(m) / max * 100);
    return `<div class="titem">
      <div class="topic">${t.topic}</div>
      <div class="bar"><i style="width:${w}%"></i></div>
      <div class="mom ${m < 0 ? "neg" : ""}">${m >= 0 ? "+" : ""}${m}</div>
      <div class="src">${t.source}<br><span style="opacity:.7">${t.detail || ""}</span></div>
    </div>`;
  }).join("");
}

function renderNews(list) {
  $("#news").innerHTML = list.map(n => `<div class="nitem">
    <div class="t">${n.title}</div>
    <div class="m"><span>${n.source} · ${n.region}</span>
      <span><span class="lang">${n.lang}</span> ${n.ts || ""}</span></div></div>`).join("");
}

// 攻略来源图标元数据（按 source 名称映射，稳定）
const SOURCE_META = {
  "YouTube":         { cls: "youtube",        ic: "▶",  label: "YouTube" },
  "Steam 官方":       { cls: "steam",          ic: "🎮", label: "Steam 官方" },
  "Steam 社区":       { cls: "steam-community", ic: "💬", label: "Steam 社区" },
  "Fextralife Wiki":  { cls: "fextra",         ic: "📖", label: "Fextralife" },
  "Fextralife":       { cls: "fextra",         ic: "📖", label: "Fextralife" },
  "Reddit":           { cls: "reddit",         ic: "👽", label: "Reddit" },
};
function srcMeta(s) { return SOURCE_META[s] || { cls: "other", ic: "🔗", label: s }; }

function renderGuides(list) {
  if (!list || !list.length) {
    $("#guides").innerHTML = `<div class="yt-note">暂无攻略数据（可在本机运行后端获取实时攻略）。</div>`;
    return;
  }
  $("#guides").innerHTML = list.map(g => {
    const m = srcMeta(g.source);
    return `<a class="nitem guide" href="${g.url || "#"}" target="_blank" rel="noopener">
    <div class="t">${g.title}</div>
    <div class="m"><span>
      <span class="src-badge ${m.cls}"><span class="ic">${m.ic}</span>${m.label}</span>
      <span class="tp ${g.type}">${g.type}</span>
      ${g.game}
    </span>
    <span>${(g.ts || "").slice(0, 16)}</span></div></a>`;
  }).join("");
}

function renderYT(list) {
  if (!list || !list.length) {
    $("#yt").innerHTML = `<div class="yt-note">🎬 实时攻略视频需联网获取，当前暂不可用（已回退图文攻略）。</div>`;
    return;
  }
  $("#yt").innerHTML = list.map(v => `<a class="vcard" href="${v.url}" target="_blank" rel="noopener">
    ${v.thumb ? `<img src="${v.thumb}" loading="lazy" alt="" onerror="this.style.display='none'">` : `<div style="height:86px;background:linear-gradient(135deg,#ff5a5f,#2f80ed)"></div>`}
    <div class="vt">${v.title}</div>
    <div class="vc">${v.channel}${v.published ? " · " + v.published : ""}</div>
  </a>`).join("");
}

function setLive(on, txt) {
  const dot = $("#liveDot");
  dot.className = "dot " + (on ? "on" : "off");
  $("#liveText").textContent = txt;
}

let BUNDLE = null;
let STATIC = false;

async function load() {
  if (!BUNDLE) {
    try {
      BUNDLE = await getJSON("./api/all");
    } catch (e) {
      BUNDLE = await getJSON("./data.json");
      STATIC = true;
    }
  }
  renderAll();
}

function renderAll() {
  if (!BUNDLE) return;
  renderTrends(BUNDLE.trends.data);
  renderNews(BUNDLE.news.data);
  renderGuides(BUNDLE.guides.data);
  renderYT(BUNDLE.yt.data);
  applyFilters();
  $("#trendHint").textContent = BUNDLE.trends.live ? "实时(Reddit)" : "样例";
  $("#guideHint").textContent = BUNDLE.guides.live ? "实时聚合" : "样例";
  $("#ytHint").textContent = BUNDLE.yt.live ? "实时(YouTube)" : "样例/暂不可用";
  const liveAny = BUNDLE.trends.live || BUNDLE.news.live || BUNDLE.yt.live;
  setLive(liveAny, STATIC ? "静态快照(公网)" : (liveAny ? "实时数据" : "样例数据(离线)"));
}

function applyFilters() {
  const all = (BUNDLE && BUNDLE.games && BUNDLE.games.data) || [];
  const f = all.filter(g => {
    if (state.region && g.region !== state.region) return false;
    if (state.platform && !(g.platform || []).includes(state.platform)) return false;
    if (state.genre && g.genre !== state.genre) return false;
    if (state.q) {
      const hay = (g.name + " " + (g.name_en || "") + " " + (g.tags || []).join(" ")).toLowerCase();
      if (!hay.includes(state.q.toLowerCase())) return false;
    }
    return true;
  });
  renderGames(f);
  $("#stat").innerHTML = `📊 当前筛选结果<br><b>${f.length}</b> 款游戏<br>地区 ${state.region || "全部"} · 平台 ${state.platform || "全部"}`;
  $("#gamesHint").textContent = `共 ${f.length} 款 · ${BUNDLE.games.live ? "实时" : "样例"}`;
}

// 筛选交互
function bindChips(id, key) {
  document.querySelectorAll(`#${id} .chip`).forEach(c => {
    c.addEventListener("click", () => {
      document.querySelectorAll(`#${id} .chip`).forEach(x => x.classList.remove("active"));
      c.classList.add("active");
      state[key] = c.dataset.v;
      load();
    });
  });
}
bindChips("f-region", "region");
bindChips("f-platform", "platform");
bindChips("f-genre", "genre");

$("#search").addEventListener("input", (e) => { state.q = e.target.value.trim(); load(); });
$("#refresh").addEventListener("click", load);
document.querySelectorAll(".nav a").forEach(a => a.addEventListener("click", () => {
  document.querySelectorAll(".nav a").forEach(x => x.classList.remove("active"));
  a.classList.add("active");
}));

load().then(() => { if (!STATIC) setInterval(load, 60000); }); // 静态快照模式不自动刷新
