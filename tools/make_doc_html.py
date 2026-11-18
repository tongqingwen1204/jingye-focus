#!/usr/bin/env python3
"""把交接文档.md 渲染成一份可直接阅读/打印的 HTML。

Markdown 是给 AI 和 GitHub 看的，HTML 是给人看的：表格宽、行距松、
打印时不会把表格切成两页。
"""
import pathlib

import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent

CSS = """
:root{
  --ink:#1a1c22; --ink-2:#4a5160; --ink-3:#6b7280;
  --line:#e4e8ee; --bg:#ffffff; --soft:#f7f9fc; --accent:#3c82d6;
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--bg); color:var(--ink);
  font:16px/1.75 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  -webkit-font-smoothing:antialiased;
}
.page{max-width:860px;margin:0 auto;padding:64px 28px 120px}
h1{font-size:34px;line-height:1.3;margin:0 0 8px;letter-spacing:-.01em;font-weight:700}
h2{font-size:23px;margin:56px 0 14px;padding-top:20px;border-top:1px solid var(--line);font-weight:700;letter-spacing:-.01em}
h3{font-size:17px;margin:34px 0 10px;font-weight:600;color:var(--ink)}
p{margin:0 0 16px}
strong{font-weight:600}
a{color:var(--accent);text-decoration:none;border-bottom:1px solid rgba(60,130,214,.3)}
blockquote{
  margin:18px 0; padding:14px 18px; background:var(--soft);
  border-left:3px solid var(--accent); border-radius:0 8px 8px 0; color:var(--ink-2);
}
blockquote p:last-child{margin-bottom:0}
table{border-collapse:collapse;width:100%;margin:20px 0;font-size:14px}
th,td{border:1px solid var(--line);padding:9px 12px;text-align:left;vertical-align:top;overflow-wrap:break-word}
th{background:var(--soft);font-weight:600;color:var(--ink)}
tr:nth-child(even) td{background:#fcfdff}
td code,th code{overflow-wrap:anywhere}
code{
  background:#f2f5f9; padding:2px 6px; border-radius:5px;
  font:13.5px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; color:#2c3340;
}
pre{
  background:#1d2430; color:#e6ebf2; padding:18px 20px; border-radius:12px;
  overflow-x:auto; margin:20px 0; font-size:13.5px; line-height:1.6;
}
pre code{background:none;color:inherit;padding:0;font-size:inherit}
hr{display:none}  /* 章节分隔交给 h2 的上边框，避免双线 */
ul,ol{margin:0 0 16px;padding-left:24px}
li{margin:5px 0}
li>p{margin:0}
input[type=checkbox]{margin-right:6px}
@media (max-width:640px){
  .page{padding:36px 18px 80px}
  h1{font-size:27px} h2{font-size:20px}
  table{font-size:13px} th,td{padding:7px 9px}
}
@media print{
  .page{max-width:none;padding:0}
  h2{break-after:avoid} table,pre{break-inside:avoid}
}
"""


def main():
    src = ROOT / "交接文档.md"
    body = markdown.markdown(
        src.read_text(encoding="utf-8"),
        extensions=["tables", "fenced_code", "sane_lists", "toc"],
    )
    out = (
        '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>静叶 · 专注入口 — 项目交接文档</title>\n"
        f"<style>{CSS}</style>\n</head>\n<body>\n<div class=\"page\">\n{body}\n</div>\n</body>\n</html>\n"
    )
    (ROOT / "交接文档.html").write_text(out, encoding="utf-8")
    print("交接文档.html", len(out), "bytes")


if __name__ == "__main__":
    main()
