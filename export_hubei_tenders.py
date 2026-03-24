import io
import json
import re
import ssl
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

from openpyxl import Workbook
try:
    from pypdf import PdfReader
except ModuleNotFoundError:
    # 兼容在项目内 vendor 依赖的场景
    import sys

    vendor = Path(__file__).resolve().parents[1] / ".vendor" / "python"
    sys.path.insert(0, str(vendor))
    from pypdf import PdfReader


BASE_URL = "https://caigou.chinatelecom.com.cn"
CTX = ssl._create_unverified_context()


def _post_json(path: str, payload: dict) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, context=CTX, timeout=90) as resp:
        return json.loads(resp.read().decode("utf-8", "ignore"))


def _download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=120) as resp:
        return resp.read()


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def _norm_dt(s: str) -> str:
    s = _clean(s)
    if not s:
        return ""
    s = (
        s.replace("年", "-")
        .replace("月", "-")
        .replace("日", " ")
        .replace("：", ":")
        .replace("时", ":")
        .replace("分", "")
        .replace("/", "-")
        .replace(".", "-")
    )
    m = re.search(r"(20\d{2}-\d{1,2}-\d{1,2})(?:\s*(\d{1,2}:\d{1,2}(?::\d{1,2})?))?", s)
    if not m:
        return ""
    try:
        d = datetime.strptime(m.group(1), "%Y-%m-%d").strftime("%Y-%m-%d")
    except Exception:
        return ""
    t = (m.group(2) or "").strip()
    if t and len(t.split(":")) == 2:
        t += ":00"
    return (d + (" " + t if t else "")).strip()


def _parse_area(title: str, text: str) -> str:
    t = f"{title} {text}"
    # 优先市/区/县关键词
    m = re.search(
        r"(襄阳市[^，。；\s]{0,10}(?:区|县)?)|"
        r"(黄冈市[^，。；\s]{0,10}(?:区|县)?)|"
        r"(荆州市[^，。；\s]{0,10}(?:区|县)?)|"
        r"(天门市)|"
        r"(武汉市[^，。；\s]{0,10}(?:区|县)?)",
        t,
    )
    if m:
        for g in m.groups():
            if g:
                return g
    m2 = re.search(r"(麻城市|红安县|团风县|大悟县)", t)
    if m2:
        return m2.group(1)
    return "湖北省（未细化市区）"


def _summarize(text: str, title: str) -> str:
    for p in [
        r"(?:项目概况|采购内容|招标范围|建设内容)[:：]\s*(.{20,220})",
        r"(?:本项目|本次招标)\s*(.{20,220})",
    ]:
        m = re.search(p, text, re.S)
        if m:
            return _clean(m.group(1))[:180]
    return _clean(title)[:180]


def export(days: int = 7) -> tuple[Path, int]:
    # 列表：湖北 + 招标公告（noticeSummary=1）
    items: list[dict] = []
    for page in range(1, 20):
        res = _post_json(
            "/portal/base/announcementJoin/queryListNew",
            {
                "pageNum": page,
                "pageSize": 10,
                "type": "e2no",  # 招标公告
                "provinceCode": "06",  # 湖北
                "companyCode": "",
                "noticeSummary": "1",
            },
        )
        lst = (((res.get("data") or {}).get("pageInfo") or {}).get("list") or [])
        if not lst:
            break
        items.extend(lst)

    now = datetime.now()
    start = now - timedelta(days=days)

    rows: list[dict] = []
    seen: set[tuple[str, str]] = set()

    for it in items:
        title = _clean(it.get("docTitle", ""))
        if not title:
            continue

        publish = _norm_dt(it.get("createDate", "")) or _norm_dt(it.get("pStartDate", ""))
        deadline = _norm_dt(it.get("pEndDate", ""))
        if not (publish and deadline):
            continue
        try:
            pub_d = datetime.strptime(publish[:10], "%Y-%m-%d")
            ddl_d = datetime.strptime(deadline[:10], "%Y-%m-%d")
        except Exception:
            continue
        if ddl_d < pub_d:
            continue
        if pub_d < start or pub_d > now:
            continue

        key = (title, deadline)
        if key in seen:
            continue
        seen.add(key)

        doc_id = str(it.get("docId") or "")
        sec = str(it.get("securityViewCode") or "")
        if not (doc_id and sec):
            continue

        # 附件列表 -> 下载 PDF -> 抽取核心需求
        pdf_text = ""
        source_link = f"{BASE_URL}/DeclareDetails?id={doc_id}&type=1&docTypeCode=TenderAnnouncement&securityViewCode={sec}"
        try:
            files = _post_json(
                "/portal/base/listNoticeFile",
                {"id": doc_id, "securityViewCode": sec, "type": "6"},
            )
            fl = (((files.get("data") or {}).get("list") or []) or [])
            if fl:
                f = fl[0]
                fid = str(f.get("id") or "")
                fsec = str(f.get("securityCode") or "")
                if fid and fsec:
                    pdf_url = f"{BASE_URL}/portal/base/filedownload/?id={fid}&securityCode={fsec}"
                    b = _download(pdf_url)
                    if b[:4] == b"%PDF":
                        rd = PdfReader(io.BytesIO(b))
                        pdf_text = "\n".join((p.extract_text() or "") for p in rd.pages[:6])
                        source_link = pdf_url
        except Exception:
            pass

        area = _parse_area(title, pdf_text)
        content = _summarize(pdf_text, title)
        if not (area and content and source_link):
            continue

        rows.append(
            {
                "招标标题": title,
                "招标地区（精确到市/区）": area,
                "招标内容（核心需求简述）": content,
                "发布时间": publish,
                "投标截止时间": deadline,
                "信息来源链接": source_link,
            }
        )

    out = Path(__file__).resolve().parents[1] / f"湖北近一周招标公告_{now.strftime('%Y%m%d')}.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "湖北招标公告"
    headers = [
        "招标标题",
        "招标地区（精确到市/区）",
        "招标内容（核心需求简述）",
        "发布时间",
        "投标截止时间",
        "信息来源链接",
    ]
    ws.append(headers)
    for r in sorted(rows, key=lambda x: x["发布时间"], reverse=True):
        ws.append([r[h] for h in headers])
    wb.save(out)
    return out, len(rows)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="导出湖北招标公告（中国电信阳光采购网）到 Excel")
    ap.add_argument("--days", type=int, default=7, help="仅保留最近 N 天发布时间（默认 7）")
    args = ap.parse_args()

    path, count = export(days=args.days)
    print(json.dumps({"file": str(path), "count": count}, ensure_ascii=False, indent=2))

