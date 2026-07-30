# -*- coding: utf-8 -*-
"""
全球游戏热点聚合站 · MVP 可运行原型 (后端)
- 标准库实现，无需任何第三方依赖，python server.py 即可运行
- 数据策略：内置"中文圈 + 全球 + 手游"精选样例；对 Steam / Reddit / RSS 做
  "尽力实时拉取，失败则回退样例"，保证原型离线也能跑、联网时尽量真实。
- 访问： http://192.168.0.79:8000/  （host/port 可用环境变量 HOST / PORT 覆盖）
"""
import json
import os
import urllib.request
import urllib.error
import concurrent.futures
from datetime import datetime as _dt
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

BASE = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE, "web")
PORT = int(os.environ.get("PORT", "8000"))
HOST = os.environ.get("HOST", "0.0.0.0")

# ----------------------------- 精选样例数据 -----------------------------
# region: 中国 / 全球 / 日本 / 欧美 ; platform: PC / 主机 / 移动
SAMPLE_GAMES = [
    {"id":"gta","name":"侠盗猎车手VI","name_en":"GTA VI","region":"欧美","platform":["PC","主机","移动"],"genre":"开放世界","emoji":"🚗","players":2000000,"trend":40,"tags":["Rockstar","未发售期待"]},
    {"id":"genshin","name":"原神","name_en":"Genshin Impact","region":"全球","platform":["PC","主机","移动"],"genre":"开放世界RPG","emoji":"🌟","players":1800000,"trend":12,"tags":["米哈游","二次元"]},
    {"id":"mc","name":"我的世界","name_en":"Minecraft","region":"全球","platform":["PC","主机","移动"],"genre":"沙盒","emoji":"⛏️","players":2500000,"trend":1,"tags":["微软","常青"]},
    {"id":"roblox","name":"Roblox","name_en":"Roblox","region":"全球","platform":["PC","主机","移动"],"genre":"沙盒UGC","emoji":"🧱","players":3000000,"trend":6,"tags":["元宇宙","UGC"]},
    {"id":"lol","name":"英雄联盟","name_en":"League of Legends","region":"全球","platform":["PC"],"genre":"MOBA","emoji":"🏆","players":1500000,"trend":2,"tags":["拳头","电竞"]},
    {"id":"rivals","name":"漫威争锋","name_en":"Marvel Rivals","region":"全球","platform":["PC"],"genre":"团队射击","emoji":"🦸","players":1100000,"trend":20,"tags":["网易","新作"]},
    {"id":"cs2","name":"反恐精英2","name_en":"Counter-Strike 2","region":"全球","platform":["PC"],"genre":"FPS","emoji":"🔫","players":980000,"trend":3,"tags":["V社","电竞"]},
    {"id":"wuwa","name":"鸣潮","name_en":"Wuthering Waves","region":"全球","platform":["PC","移动"],"genre":"开放世界ACT","emoji":"🌊","players":950000,"trend":26,"tags":["库洛","新晋黑马"]},
    {"id":"hsr","name":"崩坏：星穹铁道","name_en":"Honkai: Star Rail","region":"全球","platform":["PC","移动"],"genre":"回合制RPG","emoji":"🚄","players":1400000,"trend":18,"tags":["米哈游","新版本"]},
    {"id":"fortnite","name":"堡垒之夜","name_en":"Fortnite","region":"欧美","platform":["PC","主机","移动"],"genre":"大逃杀","emoji":"🏰","players":1200000,"trend":8,"tags":["Epic","联动"]},
    {"id":"pubgm","name":"PUBG Mobile","name_en":"PUBG Mobile","region":"全球","platform":["移动"],"genre":"大逃杀","emoji":"🪂","players":1600000,"trend":4,"tags":["Krafton","出海"]},
    {"id":"freefire","name":"自由之火","name_en":"Free Fire","region":"全球","platform":["移动"],"genre":"大逃杀","emoji":"🔥","players":1400000,"trend":7,"tags":["Garena","东南亚"]},
    {"id":"apex","name":"Apex英雄","name_en":"Apex Legends","region":"全球","platform":["PC","主机","移动"],"genre":"大逃杀","emoji":"🎯","players":800000,"trend":5,"tags":["EA","重生"]},
    {"id":"cod","name":"使命召唤：黑色行动6","name_en":"Call of Duty: BO6","region":"欧美","platform":["PC","主机"],"genre":"射击","emoji":"💥","players":900000,"trend":10,"tags":["动视","年货"]},
    {"id":"delta","name":"三角洲行动","name_en":"Delta Force","region":"全球","platform":["PC","移动"],"genre":"战术射击","emoji":"🎯","players":1300000,"trend":31,"tags":["腾讯","搜打撤"]},
    {"id":"valorant","name":"无畏契约","name_en":"VALORANT","region":"全球","platform":["PC"],"genre":"战术FPS","emoji":"🎯","players":760000,"trend":6,"tags":["拳头","电竞"]},
    {"id":"zzz","name":"绝区零","name_en":"Zenless Zone Zero","region":"全球","platform":["PC","移动"],"genre":"都市ACT","emoji":"⚡","players":1100000,"trend":9,"tags":["米哈游","潮酷"]},
    {"id":"helldivers","name":"绝地潜兵2","name_en":"Helldivers 2","region":"全球","platform":["PC","主机"],"genre":"合作射击","emoji":"🪖","players":600000,"trend":8,"tags":["索尼","Arrowhead"]},
    {"id":"ow2","name":"守望先锋2","name_en":"Overwatch 2","region":"全球","platform":["PC","主机"],"genre":"团队射击","emoji":"🛡️","players":700000,"trend":4,"tags":["暴雪","电竞"]},
    {"id":"mhwilds","name":"怪物猎人：荒野","name_en":"Monster Hunter Wilds","region":"日本","platform":["PC","主机"],"genre":"动作","emoji":"🐉","players":870000,"trend":22,"tags":["卡普空","新作"]},
    {"id":"ffxiv","name":"最终幻想XIV","name_en":"Final Fantasy XIV","region":"日本","platform":["PC","主机"],"genre":"MMORPG","emoji":"🗡️","players":500000,"trend":3,"tags":["SE","长青"]},
    {"id":"wukong","name":"黑神话：悟空","name_en":"Black Myth: Wukong","region":"全球","platform":["PC","主机"],"genre":"动作RPG","emoji":"🐒","players":680000,"trend":7,"tags":["游戏科学","国产3A"]},
    {"id":"elden","name":"艾尔登法环","name_en":"Elden Ring","region":"全球","platform":["PC","主机"],"genre":"魂系ARPG","emoji":"🔥","players":540000,"trend":5,"tags":["黄金树幽影","DLC"]},
    {"id":"bg3","name":"博德之门3","name_en":"Baldur's Gate 3","region":"欧美","platform":["PC","主机"],"genre":"CRPG","emoji":"🎲","players":420000,"trend":2,"tags":["拉瑞安","回合制"]},
    {"id":"lostark","name":"命运方舟","name_en":"Lost Ark","region":"韩国","platform":["PC"],"genre":"MMORPG","emoji":"⚔️","players":550000,"trend":5,"tags":["亚马逊","韩系"]},
    {"id":"dota2","name":"刀塔2","name_en":"Dota 2","region":"全球","platform":["PC"],"genre":"MOBA","emoji":"🛡️","players":610000,"trend":-1,"tags":["V社","电竞"]},
    {"id":"cyberpunk","name":"赛博朋克2077","name_en":"Cyberpunk 2077","region":"欧美","platform":["PC","主机"],"genre":"RPG","emoji":"🌃","players":480000,"trend":4,"tags":["CDPR"]},
    {"id":"whiteout","name":"寒霜启示录","name_en":"Whiteout Survival","region":"全球","platform":["移动"],"genre":"策略生存","emoji":"❄️","players":690000,"trend":15,"tags":["点点互动","出海手游"]},
    {"id":"coc","name":"部落冲突","name_en":"Clash of Clans","region":"全球","platform":["移动"],"genre":"策略","emoji":"⚔️","players":900000,"trend":3,"tags":["Supercell"]},
    {"id":"royal","name":"Royal Match","name_en":"Royal Match","region":"欧美","platform":["移动"],"genre":"三消","emoji":"👑","players":720000,"trend":11,"tags":["DreamGames","休闲出海"]},
]

SAMPLE_NEWS = [
    {"title":"GTA VI 发售日官宣，全球社媒瞬间引爆","source":"IGN","region":"欧美","lang":"英","ts":"2026-07-29 15:20","url":"#"},
    {"title":"Marvel Rivals 新赛季登顶 Steam 热玩榜","source":"GameSpot","region":"全球","lang":"英","ts":"2026-07-29 15:02","url":"#"},
    {"title":"Monster Hunter Wilds 大型更新公布，新增地图","source":"Famitsu","region":"日本","lang":"日","ts":"2026-07-29 14:40","url":"#"},
    {"title":"Black Myth: Wukong 全球销量突破 2500 万","source":"Eurogamer","region":"欧美","lang":"英","ts":"2026-07-29 14:15","url":"#"},
    {"title":"Helldivers 2 新战场上线，玩家回流","source":"IGN","region":"全球","lang":"英","ts":"2026-07-29 13:50","url":"#"},
    {"title":"Final Fantasy XIV 新资料片公布，预约开启","source":"Gematsu","region":"日本","lang":"英","ts":"2026-07-29 13:20","url":"#"},
    {"title":"Lost Ark 西服大版本更新引发回归潮","source":"Polygon","region":"韩国","lang":"英","ts":"2026-07-29 12:50","url":"#"},
    {"title":"Elden Ring 新作传闻再起，社区热议","source":"Reddit r/Eldenring","region":"全球","lang":"英","ts":"2026-07-29 12:20","url":"#"},
    {"title":"Apex Legends 新赛季平衡性调整争议","source":"Reddit r/apexlegends","region":"全球","lang":"英","ts":"2026-07-29 11:45","url":"#"},
    {"title":"Cyberpunk 2077 再度更新，老玩家回流","source":"PCGamer","region":"欧美","lang":"英","ts":"2026-07-29 11:10","url":"#"},
]

SAMPLE_GUIDES = [
    {"game":"艾尔登法环","title":"黄金树幽影 全 Boss 无伤路线","type":"视频","source":"YouTube","lang":"英","ts":"2026-07-29 15:05","url":"#"},
    {"game":"黑神话：悟空","title":"全成就解锁条件清单","type":"图文","source":"Fextralife","lang":"英","ts":"2026-07-29 14:40","url":"#"},
    {"game":"博德之门3","title":"邪念通关 Build 与关键抉择","type":"图文","source":"Fextralife Wiki","lang":"英","ts":"2026-07-29 14:10","url":"#"},
    {"game":"怪物猎人：荒野","title":"新地图生态与素材采集点","type":"视频","source":"YouTube","lang":"英","ts":"2026-07-29 13:35","url":"#"},
    {"game":"漫威争锋","title":"新英雄配队与counter思路","type":"图文","source":"Game8","lang":"英","ts":"2026-07-29 13:00","url":"#"},
    {"game":"无畏契约","title":"新特工技能详解与上分攻略","type":"图文","source":"IGN Guides","lang":"英","ts":"2026-07-29 12:30","url":"#"},
    {"game":"绝地潜兵2","title":"最高难度虫潮配装与战术","type":"视频","source":"YouTube","lang":"英","ts":"2026-07-29 12:00","url":"#"},
    {"game":"命运方舟","title":"职业 Build 与刻印优先级","type":"图文","source":"Game8","lang":"英","ts":"2026-07-29 11:25","url":"#"},
]

SAMPLE_TRENDS = [
    {"topic":"#GTA6 #","momentum":+48,"source":"Twitter/X","detail":"发售日官宣引爆全网"},
    {"topic":"Marvel Rivals new season","momentum":+30,"source":"Reddit r/marvelrivals","detail":"新赛季登顶热玩"},
    {"topic":"Monster Hunter Wilds 更新","momentum":+24,"source":"Twitter/X","detail":"新地图话题发酵"},
    {"topic":"Black Myth Wukong DLC 传闻","momentum":+19,"source":"Reddit r/gaming","detail":"销量里程碑带动二创"},
    {"topic":"Helldivers 2 新战场","momentum":+17,"source":"Twitch","detail":"直播观看走高"},
    {"topic":"Lost Ark 西服更新","momentum":+13,"source":"Reddit r/lostark","detail":"老玩家回归潮"},
    {"topic":"Free Fire 新赛季","momentum":+11,"source":"YouTube","detail":"短视频热度上升"},
    {"topic":"Cyberpunk 2077 更新","momentum":+9,"source":"Steam","detail":"老玩家回流"},
]

SAMPLE_TWITCH = [
    {"game":"Just Chatting","viewers":285000,"streams":4200},
    {"game":"League of Legends","viewers":198000,"streams":3100},
    {"game":"VALORANT","viewers":142000,"streams":2400},
    {"game":"GTA V","viewers":121000,"streams":1900},
    {"game":"Counter-Strike 2","viewers":98000,"streams":1600},
    {"game":"Fortnite","viewers":87000,"streams":1400},
    {"game":"Marvel Rivals","viewers":76000,"streams":1200},
    {"game":"Elden Ring","viewers":64000,"streams":980},
    {"game":"Minecraft","viewers":59000,"streams":1500},
    {"game":"Apex Legends","viewers":51000,"streams":870},
]


def hot_score(g):
    """综合热度分：在线人数(对数) + 趋势权重 + 平台覆盖"""
    import math
    base = math.log10(max(g.get("players", 0), 1)) * 10  # 约 60~70
    trend_w = g.get("trend", 0) * 0.8
    plat_w = len(g.get("platform", [])) * 1.5
    return round(base + trend_w + plat_w, 1)


# ----------------------------- 实时适配器（尽力拉取） -----------------------------
UA = {"User-Agent": "GameHubPrototype/1.0 (educational demo)"}


def _http_get(url, timeout=4, is_json=True):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read().decode("utf-8", "ignore")
        return json.loads(data) if is_json else data
    except Exception:
        return None


def fetch_steam_featured():
    """Steam 公开 featured 接口（无需 key），返回热门/新游名称列表"""
    d = _http_get("https://store.steampowered.com/api/featuredcategories", timeout=4)
    if not d:
        return None
    names = []
    try:
        for cat in ("top_sellers", "new_releases"):
            for it in d.get(cat, {}).get("items", []):
                names.append(it.get("name"))
    except Exception:
        return None
    return names[:12] if names else None


def fetch_reddit_hot():
    """Reddit 公开 JSON（无需登录），返回热点标题/分数"""
    d = _http_get("https://www.reddit.com/r/Games/hot.json?limit=10", timeout=4)
    if not d:
        return None
    out = []
    try:
        for c in d["data"]["children"]:
            p = c["data"]
            out.append({"topic": p.get("title", ""), "momentum": int(p.get("score", 0) / 100),
                        "source": "Reddit r/Games", "detail": f"{p.get('num_comments',0)} 评论"})
    except Exception:
        return None
    return out or None


RSS_FEEDS = [
    ("https://feeds.feedburner.com/ign/all", "IGN", "欧美", "英"),
    ("https://www.gamespot.com/feeds/all/", "GameSpot", "欧美", "英"),
    ("https://www.gematsu.com/feed", "Gematsu", "日本", "英"),
    ("https://www.pcgamer.com/rss/", "PCGamer", "欧美", "英"),
    ("https://www.vg247.com/feed", "VG247", "欧美", "英"),
    ("https://www.polygon.com/rss/index.xml", "Polygon", "欧美", "英"),
]


def fetch_rss_news():
    import xml.etree.ElementTree as ET
    out = []
    for url, src, region, lang in RSS_FEEDS:
        txt = _http_get(url, timeout=4, is_json=False)
        if not txt:
            continue
        try:
            root = ET.fromstring(txt)
            for item in root.iter("item"):
                title = item.findtext("title") or ""
                pub = item.findtext("pubDate") or ""
                if title:
                    out.append({"title": title[:60], "source": src, "region": region,
                                "lang": lang, "ts": pub[:16], "url": "#"})
        except Exception:
            continue
    return out or None


# ----------------------------- Twitch 实时直播热度（需凭证） -----------------------------
import time as _time
_CACHE = {}  # 简单内存缓存：key -> (expire_ts, data)


def _cache_get(key, ttl=300):
    v = _CACHE.get(key)
    if v and v[0] > _time.time():
        return v[1]
    return None


def _cache_set(key, data, ttl=300):
    _CACHE[key] = (_time.time() + ttl, data)


TWITCH_CID = os.environ.get("TWITCH_CLIENT_ID", "")
TWITCH_SEC = os.environ.get("TWITCH_CLIENT_SECRET", "")


def fetch_twitch_token():
    if not (TWITCH_CID and TWITCH_SEC):
        return None
    cached = _cache_get("twitch_token", ttl=3600)
    if cached:
        return cached
    try:
        url = (f"https://id.twitch.tv/oauth2/token?client_id={TWITCH_CID}"
               f"&client_secret={TWITCH_SEC}&grant_type=client_credentials")
        req = urllib.request.Request(url, data=b"", method="POST", headers=UA)
        with urllib.request.urlopen(req, timeout=5) as r:
            d = json.loads(r.read().decode("utf-8", "ignore"))
        tok = d.get("access_token")
        if tok:
            _cache_set("twitch_token", tok, ttl=3600)
        return tok
    except Exception:
        return None


def fetch_twitch_live():
    """按观看人数聚合 top 直播游戏（取 top 100 直播流汇总 game_name）。"""
    tok = fetch_twitch_token()
    if not tok:
        return None
    cached = _cache_get("twitch_live", ttl=180)
    if cached:
        return cached
    try:
        url = "https://api.twitch.tv/helix/streams?first=100"
        req = urllib.request.Request(url, headers={
            "Client-Id": TWITCH_CID, "Authorization": f"Bearer {tok}"})
        with urllib.request.urlopen(req, timeout=6) as r:
            d = json.loads(r.read().decode("utf-8", "ignore"))
        agg = {}
        for s in d.get("data", []):
            g = s.get("game_name") or "其他"
            a = agg.setdefault(g, {"game": g, "viewers": 0, "streams": 0})
            a["viewers"] += s.get("viewer_count", 0)
            a["streams"] += 1
        out = sorted(agg.values(), key=lambda x: x["viewers"], reverse=True)[:10]
        _cache_set("twitch_live", out, ttl=180)
        return out or None
    except Exception:
        return None


# ----------------------------- YouTube 攻略视频（免 key，search RSS） -----------------------------
def fetch_youtube_guides(queries, per=2):
    """用 YouTube 公开 search RSS 拉取真实攻略视频，无需 API key。"""
    ck = "yt_" + "|".join(queries)
    cached = _cache_get(ck, ttl=600)
    if cached is not None:
        return cached
    import xml.etree.ElementTree as ET
    out = []
    for q in queries:
        url = "https://www.youtube.com/feeds/videos.xml?search_query=" + urllib.parse.quote(q)
        txt = _http_get(url, timeout=5, is_json=False)
        if not txt:
            continue
        try:
            root = ET.fromstring(txt)
            ns = "{http://www.w3.org/2005/Atom}"
            yt = "{http://www.youtube.com/xml/schema/2015}"
            for e in root.findall(ns + "entry")[:per]:
                vid = e.find(yt + "videoId")
                title = e.find(ns + "title")
                pub = e.find(ns + "published")
                author = e.find(ns + "author")
                aname = author.find(ns + "name") if author is not None else None
                if vid is None or title is None:
                    continue
                out.append({
                    "title": (title.text or "")[:70],
                    "videoId": vid.text,
                    "channel": aname.text if aname is not None else "",
                    "published": (pub.text or "")[:10] if pub is not None else "",
                    "thumb": f"https://i.ytimg.com/vi/{vid.text}/hqdefault.jpg",
                    "url": f"https://www.youtube.com/watch?v={vid.text}",
                    "query": q,
                })
        except Exception:
            continue
    _cache_set(ck, out, ttl=600)
    return out


# ----------------------------- Steam 官方资讯 / Reddit 社区讨论（攻略实时化） -----------------------------
# 仅 Steam 平台游戏有 appid，用于拉取官方新闻/更新作为图文攻略来源
STEAM_APPID = {
    "rivals": 2767030, "cs2": 730, "apex": 1172470, "cod": 1938090,
    "delta": 2507950, "helldivers": 553850, "mhwilds": 2246340,
    "wukong": 2358720, "elden": 1245620, "bg3": 1086940, "dota2": 570,
    "cyberpunk": 1091500, "pubg": 578080,
}


def _iso(ts_raw):
    try:
        return _dt.utcfromtimestamp(int(ts_raw)).strftime("%Y-%m-%dT%H:%M")
    except Exception:
        return "1970-01-01T00:00"


def fetch_steam_news(appid, limit=3):
    """Steam 公开新闻接口（无需 key），返回官方更新/公告，作为图文攻略来源。"""
    ck = "steamnews_" + str(appid)
    cached = _cache_get(ck, ttl=600)
    if cached is not None:
        return cached
    url = (f"https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/"
           f"?appid={appid}&count={limit}&l=english")
    d = _http_get(url, timeout=4)
    out = []
    if d:
        try:
            for n in d.get("appnews", {}).get("newsitems", []):
                out.append({"title": (n.get("title") or "")[:60],
                            "url": n.get("url") or "#",
                            "ts_raw": int(n.get("date", 0))})
        except Exception:
            out = []
    _cache_set(ck, out, ttl=600)
    return out or None


def fetch_reddit_search(query, limit=3):
    """Reddit 公开搜索 JSON（无需登录），返回社区攻略/讨论帖。"""
    ck = "reddit_" + query
    cached = _cache_get(ck, ttl=600)
    if cached is not None:
        return cached
    q = f"{query} guide OR tips OR walkthrough OR build"
    url = ("https://www.reddit.com/search.json?q=" + urllib.parse.quote(q) +
           f"&sort=new&limit={limit}&type=link")
    d = _http_get(url, timeout=4)
    out = []
    if d:
        try:
            for c in d.get("data", {}).get("children", []):
                p = c["data"]
                out.append({"title": (p.get("title") or "")[:60],
                            "url": "https://www.reddit.com" + (p.get("permalink") or ""),
                            "ts_raw": int(p.get("created_utc", 0))})
        except Exception:
            out = []
    _cache_set(ck, out, ttl=600)
    return out or None


# ----------------------------- 聚合接口 -----------------------------
def api_games(params):
    games = []
    for g in SAMPLE_GAMES:
        g = dict(g)
        g["hotScore"] = hot_score(g)
        games.append(g)
    games.sort(key=lambda x: x["hotScore"], reverse=True)
    # 地区/平台/类型过滤
    region = params.get("region", [""])[0]
    plat = params.get("platform", [""])[0]
    genre = params.get("genre", [""])[0]
    kw = params.get("q", [""])[0].lower()
    if region:
        games = [g for g in games if g["region"] == region]
    if plat:
        games = [g for g in games if plat in g["platform"]]
    if genre:
        games = [g for g in games if genre in g["genre"]]
    if kw:
        games = [g for g in games if kw in g["name"].lower() or kw in g["name_en"].lower() or kw in ",".join(g.get("tags", [])).lower()]
    return {"updated": "now", "live": False, "count": len(games), "data": games}


def api_trends(params):
    live = fetch_reddit_hot()
    data = live if live else SAMPLE_TRENDS
    return {"updated": "now", "live": bool(live), "count": len(data), "data": data}


def api_news(params):
    live = fetch_rss_news()
    data = live if live else SAMPLE_NEWS
    # 按样例/实时混合：实时在前
    return {"updated": "now", "live": bool(live), "count": len(data), "data": data[:12]}


def api_guides(params):
    """攻略实时化：并行聚合 YouTube 视频攻略 + Steam 官方资讯 + Reddit 社区讨论，
    按时间倒序；任一真实源成功即标记 live=True，否则回退样例。"""
    games = sorted(SAMPLE_GAMES, key=hot_score, reverse=True)[:14]
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as ex:
        f_yt = {g["id"]: ex.submit(fetch_youtube_guides, [f"{g['name_en']} guide"], per=1) for g in games}
        f_steam = {gid: ex.submit(fetch_steam_news, aid)
                   for gid, aid in STEAM_APPID.items() if any(g["id"] == gid for g in games)}
        f_rd = {g["id"]: ex.submit(fetch_reddit_search, g["name_en"]) for g in games}
        for gid, f in f_yt.items():
            results.setdefault(gid, {})["yt"] = f.result()
        for gid, f in f_steam.items():
            results.setdefault(gid, {})["steam"] = f.result()
        for gid, f in f_rd.items():
            results.setdefault(gid, {})["reddit"] = f.result()

    items = []
    for g in games:
        gid, name = g["id"], g["name"]
        r = results.get(gid, {})
        yt = r.get("yt")
        if yt:
            for v in yt:
                items.append({"game": name, "title": v.get("title", ""),
                              "type": "视频", "source": "YouTube", "lang": "英",
                              "ts": (v.get("published") or "")[:16], "url": v.get("url", "")})
        steam = r.get("steam")
        if steam:
            for n in steam:
                items.append({"game": name, "title": n.get("title", ""),
                              "type": "图文", "source": "Steam 官方", "lang": "英",
                              "ts": _iso(n.get("ts_raw", 0)).replace("T", " "), "url": n.get("url", "")})
        rd = r.get("reddit")
        if rd:
            for n in rd:
                items.append({"game": name, "title": n.get("title", ""),
                              "type": "图文", "source": "Reddit", "lang": "英",
                              "ts": _iso(n.get("ts_raw", 0)).replace("T", " "), "url": n.get("url", "")})

    live = len(items) > 0
    if not live:
        items = SAMPLE_GUIDES
    else:
        items.sort(key=lambda x: (x.get("ts") or ""), reverse=True)
        items = items[:18]
    return {"updated": "now", "live": live, "count": len(items), "data": items}


def api_twitch(params):
    data = fetch_twitch_live()
    live = data is not None
    if not live:
        data = SAMPLE_TWITCH
    return {"updated": "now", "live": live, "count": len(data), "data": data}


def api_yt(params):
    top = SAMPLE_GAMES[:8]
    queries = [f"{g['name_en']} guide" for g in top]
    data = fetch_youtube_guides(queries, per=2)
    if not data:
        # 离线/无网络回退：给出指向 YouTube 搜索的可用卡片（点击即真实搜索）
        data = [{
            "title": f"{g['name']} 攻略 / guide",
            "videoId": "", "channel": "YouTube 搜索", "published": "", "thumb": "",
            "url": f"https://www.youtube.com/results?search_query={urllib.parse.quote(g['name_en'] + ' guide')}",
            "query": g['name_en'],
        } for g in top]
    return {"updated": "now", "live": any(d.get("videoId") for d in data), "count": len(data), "data": data}


# ----------------------------- HTTP 服务 -----------------------------
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)
        if path in ("/", "/index.html"):
            return self._serve_file(os.path.join(WEB_DIR, "index.html"), "text/html; charset=utf-8")
        if path.startswith("/static/"):
            fp = os.path.join(WEB_DIR, os.path.basename(path))
            return self._serve_file(fp)
        # GitHub Pages / 项目页兼容：支持相对路径托管根目录静态资源
        if path in ("/style.css", "/app.js", "/data.json"):
            return self._serve_file(os.path.join(WEB_DIR, path.lstrip("/")))
        if path == "/favicon.ico":
            return self._send(204, b"")
        if path == "/api/games":
            return self._send(200, api_games(qs))
        if path == "/api/trends":
            return self._send(200, api_trends(qs))
        if path == "/api/news":
            return self._send(200, api_news(qs))
        if path == "/api/guides":
            return self._send(200, api_guides(qs))
        if path == "/api/twitch":
            return self._send(200, api_twitch(qs))
        if path == "/api/yt":
            return self._send(200, api_yt(qs))
        if path == "/api/all":
            return self._send(200, {
                "games": api_games(qs), "trends": api_trends(qs),
                "news": api_news(qs), "guides": api_guides(qs),
                "twitch": api_twitch(qs), "yt": api_yt(qs)})
        self._send(404, {"error": "not found"})

    def _serve_file(self, fp, ctype=None):
        if not os.path.isfile(fp):
            return self._send(404, {"error": "file not found"})
        ext = os.path.splitext(fp)[1]
        ct = ctype or {
            ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8", ".svg": "image/svg+xml"}.get(ext, "application/octet-stream")
        with open(fp, "rb") as f:
            self._send(200, f.read(), ct)


def main():
    try:
        srv = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError as e:
        print(f"❌ 无法绑定到 {HOST}:{PORT} —— {e}")
        print(f"   原因：本机并没有 IP 地址 {HOST}（该地址属于别的机器）。")
        print(f"   解决：把 HOST 改成你本机的真实 IP，或用 0.0.0.0 监听所有网卡：")
        print(f"         set HOST=0.0.0.0   （或本机真实 IP，如 192.168.0.79）")
        print(f"         python server.py")
        return
    print(f"🎮 GameHub 原型已启动: http://{HOST}:{PORT}/")
    print("   局域网访问：同一 WiFi/网段下的设备用你本机 IP 打开，例如 http://192.168.0.79:8000/")
    print("   按 Ctrl+C 停止。")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")


if __name__ == "__main__":
    main()
