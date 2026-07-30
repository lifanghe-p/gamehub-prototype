# -*- coding: utf-8 -*-
"""
生成静态快照 web/data.json（用于 GitHub Pages / CloudStudio / 任意静态托管公网部署）。

用法（二选一）：
    python server.py        # 先启动后端（可选）
    python build_snapshot.py # 生成快照

实现说明：
- 默认优先直连本地后端 http://127.0.0.1:8000/api/all（保证与线上预览完全一致）。
- 若连不上本地后端（没启动、或端口被旧进程占用），则**直接 import 后端模块**调用各接口函数，
  用当前最新代码烘焙，无需先起服务器。这样在用户本机双击运行 publish.bat / build_snapshot.py
  即可拿到真实数据，避免"连到陈旧后端进程"导致快照不是最新代码的问题。
- 在有外网的环境运行，会把 Steam 社区指南 / Fextralife Wiki / YouTube 攻略视频 /
  Steam 官方资讯 / Reddit 讨论 等真实数据烘焙进快照；离线则自动回退样例。
"""
import json
import os
import sys
import importlib

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "web", "data.json")
URL = "http://127.0.0.1:8000/api/all"


def _from_server():
    """尝试从运行中的后端拉取 /api/all（用当前代码烘焙的真实数据）。"""
    import urllib.request
    req = urllib.request.Request(URL, headers={"User-Agent": "curl/8"})
    data = urllib.request.urlopen(req, timeout=90).read()
    return json.loads(data)


def _from_module():
    """后端没起时，直接 import 后端模块调用接口函数（始终用最新代码）。"""
    sys.path.insert(0, BASE)
    import server
    importlib.reload(server)  # 强制重载，避免缓存旧代码
    qs = {}
    return {
        "games": server.api_games(qs),
        "trends": server.api_trends(qs),
        "news": server.api_news(qs),
        "guides": server.api_guides(qs),
        "yt": server.api_yt(qs),
    }


def main():
    d = None
    # 优先用后端模块直调（保证是最新代码，且无需先起服务器）；
    # 仅当模块导入失败时，才回退到运行中的本地后端。
    try:
        d = _from_module()
        src = "backend module (direct import, no server needed)"
    except Exception as e:
        try:
            d = _from_server()
            src = "running server (127.0.0.1:8000)"
        except Exception as e2:
            raise SystemExit(f"❌ 两种方式都失败：\n  module: {e}\n  server: {e2}")
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)
    print(f"✅ 已生成 {OUT}")
    print(f"   来源: {src}")
    print(f"   游戏 {d['games']['count']} 款 | 新闻 live={d['news']['live']} | "
          f"攻略 live={d['guides']['live']} | YouTube live={d['yt']['live']}")
    print("   重新部署 web/ 目录即可让公网版本更新数据。")


if __name__ == "__main__":
    main()
