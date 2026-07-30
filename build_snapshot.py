# -*- coding: utf-8 -*-
"""
生成静态快照 web/data.json（用于 GitHub Pages / CloudStudio / 任意静态托管公网部署）。
前提：本地先启动 server.py（python server.py），本脚本把 /api/all 导出成静态 JSON。
      在有外网的环境运行，即可把 Steam 社区指南 / Fextralife Wiki / YouTube 攻略视频 /
      Steam 官方资讯 / Reddit 讨论 等真实数据烘焙进快照；离线则自动回退样例。
用法：
    python server.py        # 先启动后端
    python build_snapshot.py # 再生成快照
然后重新部署 web/ 目录（含 data.json）即可。
"""
import json
import os
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "web", "data.json")
URL = "http://127.0.0.1:8000/api/all"


def main():
    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "curl/8"})
        data = urllib.request.urlopen(req, timeout=60).read()
        d = json.loads(data)
    except Exception as e:
        raise SystemExit(f"拉取 {URL} 失败：{e}\n请先启动 server.py（python server.py）。")
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)
    print(f"✅ 已生成 {OUT}")
    print(f"   游戏 {d['games']['count']} 款 | 新闻 live={d['news']['live']} | "
          f"攻略 live={d['guides']['live']} | YouTube live={d['yt']['live']}")
    print("   重新部署 web/ 目录即可让公网版本更新数据。")


if __name__ == "__main__":
    main()
