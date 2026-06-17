#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import date, datetime, timedelta
from pathlib import Path, PurePosixPath

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")

TODAY = date.today().isoformat()
MANUAL_MARKER = "<!-- manual-notes:start -->"
LINKS_START = "<!-- finance-knowledge-links:start -->"
LINKS_END = "<!-- finance-knowledge-links:end -->"

CONCEPTS = [
    {
        "name": "国产替代",
        "keywords": ["国产替代", "对日替代", "去日化", "自主可控", "卡脖子", "半导体设备", "半导体材料", "半导体耗材", "芯片设备", "芯片材料", "光刻胶", "电子化学品", "涂胶显影", "探针台", "测试机", "划片机", "靶材"],
        "summary": "国产替代关注外部限制下，国内产业链能否通过设备、材料、订单和利润兑现形成长期主线。",
        "watch": ["外部限制是否持续", "国产设备材料订单是否兑现", "相关 ETF 或板块在回调后是否保持相对强势", "估值是否已经透支业绩"],
        "fail": ["订单和利润无法兑现", "国产替代进度低于预期", "板块持续弱于泛科技方向"],
        "entities": ["半导体设备", "半导体材料", "PCB材料"],
    },
    {
        "name": "涨价方向",
        "keywords": ["涨价", "价格", "现货", "毛利率", "碳酸锂", "小金属", "钨", "钼", "钽", "锗", "稀土", "覆铜板", "树脂", "铜箔", "六氟化钨", "电子特气"],
        "summary": "涨价方向关注价格能否传导到订单、毛利率和利润，而不是只看题材热度。",
        "watch": ["现货和期货价格是否持续上行", "公司毛利率是否改善", "涨价是否传导到半年报或订单", "高位品种是否出现放量滞涨"],
        "fail": ["涨价无法传导到业绩", "价格快速回落", "股价提前透支后持续放量破位"],
        "entities": ["半导体材料", "PCB材料", "锂矿", "黄金有色"],
    },
    {
        "name": "科技材料第二波",
        "keywords": ["第二波", "五日线", "趋势线", "半导体材料", "PCB材料", "电子化学品", "光刻胶", "MLCC", "陶瓷材料", "硅片", "玻璃基板", "电子特气"],
        "summary": "科技材料第二波关注第一波调整后的结构质量，核心是前低、五日线、趋势线和放量方式。",
        "watch": ["调整后是否不破前低", "是否重新站回五日线或趋势线", "是否放量修复而不是放量破位", "细分分支是否继续接力"],
        "fail": ["放量破位后不能修复", "第二波形态频繁失败", "外部风险导致市场直接破位"],
        "entities": ["半导体材料", "PCB材料", "半导体设备"],
    },
    {
        "name": "宏观事件窗口",
        "keywords": ["CPI", "美联储", "议息", "纳斯达克", "美股", "美伊", "战争", "加息", "降息", "外围", "风险事件"],
        "summary": "宏观事件窗口关注外部变量如何影响 A 股风险偏好，以及金融或防守方向是否托住指数。",
        "watch": ["事件落地前后指数是否放量破位", "金融或防守方向是否托住市场", "海外链和国产替代相对强弱", "科技主线是否仍有资金承接"],
        "fail": ["事件落地后指数放量破位", "金融护盘失效", "强势主线系统性退潮"],
        "entities": ["证券", "CPO光模块", "半导体材料"],
    },
    {
        "name": "仓位和交易纪律",
        "keywords": ["仓位", "减仓", "空仓", "加仓", "止盈", "止损", "观察仓", "利润垫", "交易纪律", "低成本", "轻仓", "高抛", "低吸"],
        "summary": "仓位和交易纪律关注在高不确定环境中，如何用仓位、利润垫和失效条件降低情绪化损失。",
        "watch": ["观察仓是否避免扩大亏损", "规则外补仓是否减少", "利润垫是否足够", "减仓后是否显著降低组合波动"],
        "fail": ["低仓位导致系统性踏空", "观察仓失败后继续无规则加仓", "止盈止损规则频繁造成无效损耗"],
        "entities": ["ETF定投", "高股息"],
    },
    {
        "name": "ETF定投",
        "keywords": ["ETF 定投", "定投", "微笑曲线", "止盈不止损", "成长宽基", "科创成长", "创业板成长", "成本线", "ETF", "指数成分", "科创半设", "科创芯片", "5G指数"],
        "summary": "ETF 定投关注用分批、无底仓起步和纪律止盈降低择时压力，但仍要验证标的长期逻辑。",
        "watch": ["成本线是否随下跌有效下降", "反弹后是否达到预设止盈区间", "重复暴露是否降低", "长期方向是否仍成立"],
        "fail": ["标的长期弱于现金或低波资产", "止盈纪律无法执行", "重复暴露造成组合回撤扩大"],
        "entities": ["ETF定投"],
    },
    {
        "name": "高股息和利率",
        "keywords": ["高股息", "分红", "银行", "电力", "煤炭", "利率上行", "利率下行", "国债", "类债", "无风险收益"],
        "summary": "高股息和利率关注类债资产的估值是否仍能覆盖利率变化和资金偏好变化。",
        "watch": ["国内外利率方向", "高股息指数相对强弱", "北向或机构资金是否持续流入", "分红提升能否抵消估值压力"],
        "fail": ["利率上行压制估值", "盈利和分红无法提升", "防守方向相对收益消失"],
        "entities": ["高股息", "证券"],
    },
    {
        "name": "科技主线轮动",
        "keywords": ["科技", "CPO", "PCB", "液冷", "电源", "算力", "AI电源", "自动化设备", "机器视觉", "半导体", "存储", "光模块", "AI应用", "高端制造", "消费电子"],
        "summary": "科技主线轮动关注科技内部资金从一个分支切到另一个分支时，哪些方向仍有结构和业绩支撑。",
        "watch": ["主线是否继续有分支接力", "强势分支是否放量滞涨", "海外链和国产替代相对强弱", "业绩链和概念链是否分化"],
        "fail": ["科技整体放量破位", "分支接力中断", "业绩链同步走弱"],
        "entities": ["AI电源", "CPO光模块", "半导体材料", "PCB材料"],
    },
    {
        "name": "黄金有色周期",
        "keywords": ["黄金", "有色", "铜", "伦敦金", "大黄", "钨", "钼", "锗", "钽", "小金属"],
        "summary": "黄金有色周期关注长期避险和资源品价格逻辑，但短期必须尊重趋势和关键位。",
        "watch": ["关键支撑位是否守住", "现货和期货价格是否共振", "资源品价格能否传导到权益端", "趋势是否重新形成"],
        "fail": ["关键位失守后不能修复", "资源价格上涨无法反映到股价或利润", "短期趋势继续恶化"],
        "entities": ["黄金有色"],
    },
    {
        "name": "十五五政策方向",
        "keywords": ["十五五", "低空经济", "商业航天", "新能源", "新材料", "政策方向"],
        "summary": "十五五政策方向关注政策、产业落地和资金承接是否共振，防止只看单日题材发酵。",
        "watch": ["政策方向是否有订单或业绩验证", "低位方向是否放量延续", "产业链是否扩散到材料端", "题材是否只停留在单日脉冲"],
        "fail": ["缺少订单和业绩验证", "放量后没有持续性", "题材只剩消息刺激"],
        "entities": ["低空经济", "新能源"],
    },
]

ENTITIES = [
    {"name": "半导体材料", "aliases": ["半导体耗材", "电子化学品", "光刻胶", "电子特气", "硅片", "玻璃基板"], "keywords": ["半导体材料", "半导体耗材", "电子化学品", "光刻胶", "电子特气", "硅片", "玻璃基板", "六氟化钨"], "focus": "国产替代、涨价和科技材料第二波的交汇点。"},
    {"name": "半导体设备", "aliases": ["芯片设备", "国产半导体设备"], "keywords": ["半导体设备", "芯片设备", "北方", "拓荆", "国产半导体设备"], "focus": "外部限制下的国产替代核心方向，重点看订单和利润兑现。"},
    {"name": "PCB材料", "aliases": ["覆铜板", "树脂", "铜箔"], "keywords": ["PCB", "PCB材料", "覆铜板", "树脂", "铜箔"], "focus": "算力链和材料涨价的交叉方向，重点看价格、订单和扩散持续性。"},
    {"name": "AI电源", "aliases": ["电源", "HVDC"], "keywords": ["AI电源", "电源", "HVDC", "800V", "Power Rack"], "focus": "算力基础设施中的高弹性方向，重点看量产节奏和预期证伪风险。"},
    {"name": "CPO光模块", "aliases": ["CPO", "光模块", "光纤"], "keywords": ["CPO", "光模块", "光纤", "1.6T", "800G"], "focus": "海外算力链和业绩链分化方向，重点看商用进度和龙头承接。"},
    {"name": "锂矿", "aliases": ["锂电", "碳酸锂"], "keywords": ["锂矿", "锂电", "碳酸锂", "电池"], "focus": "超跌反弹和周期价格修复方向，重点看期货现货和趋势扭转。"},
    {"name": "黄金有色", "aliases": ["黄金", "有色金属", "小金属"], "keywords": ["黄金", "有色", "铜", "钨", "钼", "锗", "钽", "稀土", "伦敦金"], "focus": "长期避险和资源约束方向，重点看趋势、关键位和价格传导。"},
    {"name": "证券", "aliases": ["券商", "大金融"], "keywords": ["证券", "券商", "大金融", "金融护盘"], "focus": "指数稳定和低位修复方向，重点看成交量、半年报和护盘持续性。"},
    {"name": "ETF定投", "aliases": ["ETF", "成长宽基"], "keywords": ["ETF 定投", "定投", "成长宽基", "科创成长", "创业板成长"], "focus": "降低择时压力的组合工具，重点看成本线、止盈纪律和长期方向。"},
    {"name": "高股息", "aliases": ["类债股", "银行", "电力", "煤炭"], "keywords": ["高股息", "类债", "银行", "电力", "煤炭", "分红"], "focus": "防守资产，重点看利率、分红和相对收益。"},
    {"name": "低空经济", "aliases": ["低空"], "keywords": ["低空经济", "低空"], "focus": "政策方向中的低位修复线，重点看订单和持续性。"},
    {"name": "新能源", "aliases": ["光伏", "新材料"], "keywords": ["新能源", "光伏", "新材料"], "focus": "政策和库存周期方向，重点看库存出清、价格和业绩确认。"},
]

RULE_CANDIDATES = [
    {
        "id": "P1",
        "rule": "大跌后的缩量反弹不能孤立判断，要结合位置、阳线力度和主线承接。",
        "sources": ["H-20260609-002"],
        "evidence_count": 2,
        "status": "观察中",
        "next_step": "继续收集大跌后第一段修复样本，区分低位修复和高位缩量上涨。",
        "gap": "缺少更多低位缩量修复和高位缩量失败的对照样本。",
    },
    {
        "id": "P2",
        "rule": "科技材料第二波需要同时看前低、五日线、趋势线和放量方式。",
        "sources": ["H-20260606-002", "H-20260611-001"],
        "evidence_count": 2,
        "status": "观察中",
        "next_step": "继续检查半导体材料和 PCB 材料的二波结构是否重复出现。",
        "gap": "缺少跨分支样本和失败反例，尤其是形态出现后继续破位的记录。",
    },
    {
        "id": "P3",
        "rule": "涨价和国产替代要用价格、订单、毛利率和半年报验证，不能只看题材记忆。",
        "sources": ["H-20260609-001", "H-20260611-002"],
        "evidence_count": 2,
        "status": "观察中",
        "next_step": "等待价格、订单、毛利率或半年报证据补齐。",
        "gap": "缺少半年报、订单和毛利率层面的硬证据。",
    },
    {
        "id": "P4",
        "rule": "高不确定阶段的核心不是预测日内涨跌，而是把仓位、利润垫和失效条件先写清楚。",
        "sources": ["H-20260529-001", "H-20260606-001", "H-20260607-002"],
        "evidence_count": 3,
        "status": "暂不晋级",
        "next_step": "2026-06-30 再复核跨作者证据、反例和组合动作。",
        "gap": "来源集中度偏高，缺少反例记录和明确组合动作。",
    },
]

CLOSED_HYPOTHESIS_STATUSES = {"已确认", "部分确认", "已证伪", "已降权", "降权", "证据不足降权", "已归档"}


def find_vault():
    env = os.environ.get("OBSIDIAN_VAULT", "")
    if env and Path(env).is_dir():
        return Path(env)
    obsidian_json = Path.home() / "Library/Application Support/obsidian/obsidian.json"
    if obsidian_json.is_file():
        text = obsidian_json.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r'"path":"([^"]+)"', text)
        if match and Path(match.group(1)).is_dir():
            return Path(match.group(1))
    fallback = Path.home() / "Documents/Obsidian Vault"
    if fallback.is_dir():
        return fallback
    raise SystemExit("knowledge_base_status=blocked\nreason=vault_not_found")


def read_text(path):
    return path.read_text(encoding="utf-8")


def hash_text(value):
    if not value:
        return ""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def remove_generated_links(content):
    if LINKS_START not in content or LINKS_END not in content:
        return content
    pattern = re.compile(r"\n## 知识库链接\n\n" + re.escape(LINKS_START) + r"[\s\S]*?" + re.escape(LINKS_END) + r"\n?", re.MULTILINE)
    return pattern.sub("\n", content)


def write_if_changed(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def preserve_manual(path, generated):
    manual = MANUAL_MARKER + "\n\n## 人工备注\n\n"
    if path.exists():
        old = read_text(path)
        if MANUAL_MARKER in old:
            manual = old[old.index(MANUAL_MARKER):]
    return generated.rstrip() + "\n\n" + manual.rstrip() + "\n"


def strip_code(content):
    content = re.sub(r"```[\s\S]*?```", "", content)
    return re.sub(r"`[^`\n]*`", "", content)


def wikilinks(content):
    return re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", strip_code(content))


def clean_title(title):
    return title.strip().strip("#").strip().strip("《》")


def extract_section(content, heading):
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(content)
    if not match:
        return ""
    start = match.end()
    next_match = re.search(r"^##\s+", content[start:], re.MULTILINE)
    end = start + next_match.start() if next_match else len(content)
    return content[start:end].strip()


def table_value(content, key):
    for line in content.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0] == key:
            return cells[1]
    return ""


def source_author(value):
    source = value.strip()
    for separator in [" - ", " — "]:
        if separator in source:
            return source.split(separator, 1)[0].strip()
    return source


def obsidian_link(root, path, label):
    rel = path.relative_to(root).with_suffix("").as_posix()
    return f"[[{rel}|{label}]]"


def match_catalog(text, catalog):
    hits = []
    text_lower = text.lower()
    for item in catalog:
        lookup_text = text_lower
        if item["name"] == "黄金有色周期" or item["name"] == "黄金有色":
            lookup_text = lookup_text.replace("黄金分割", "")
        if any(keyword.lower() in lookup_text for keyword in item["keywords"]):
            hits.append(item["name"])
    return hits


def parse_cards(root):
    cards = []
    for path in sorted((root / "source-cards").rglob("*.md")):
        content = read_text(path)
        analysis_content = remove_generated_links(content)
        title_match = re.search(r"^#\s+(.+)$", analysis_content, re.MULTILINE)
        published_match = re.search(r"^published:\s*(.+)$", analysis_content, re.MULTILINE)
        related_match = re.search(r"^related_notes:\s*(.+)$", analysis_content, re.MULTILINE)
        title = clean_title(title_match.group(1)) if title_match else path.stem
        published = published_match.group(1).strip() if published_match else ""
        raw_source = table_value(analysis_content, "来源")
        card = {
            "path": path,
            "title": title,
            "published": published,
            "date": published[:10],
            "source": source_author(raw_source),
            "related_notes": related_match.group(1).strip() if related_match else "",
            "thesis": extract_section(analysis_content, "核心观点"),
            "observe": extract_section(analysis_content, "可以怎么观察"),
            "invalid": extract_section(analysis_content, "什么情况说明错了"),
            "risk": extract_section(analysis_content, "风险和反面观点"),
            "pattern": extract_section(analysis_content, "可复用模式"),
            "content": content,
        }
        text = "\n".join([card["title"], card["source"], card["thesis"], card["observe"], card["invalid"], card["pattern"], analysis_content])
        card["concepts"] = match_catalog(text, CONCEPTS)
        card["entities"] = match_catalog(text, ENTITIES)
        cards.append(card)
    return cards


def parse_hypotheses(root):
    path = root / "state/hypothesis-ledger.md"
    if not path.exists():
        return []
    rows = []
    for line in read_text(path).splitlines():
        if not line.startswith("| H-"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 10:
            continue
        item = {
            "id": cells[0],
            "date": cells[1],
            "source": cells[2],
            "hypothesis": cells[3],
            "asset": cells[4],
            "period": cells[5],
            "confirm": cells[6],
            "invalid": cells[7],
            "review": cells[8],
            "status": cells[9],
            "line": line,
        }
        text = " ".join([item["source"], item["hypothesis"], item["asset"], item["confirm"], item["invalid"]])
        item["concepts"] = match_catalog(text, CONCEPTS)
        item["entities"] = match_catalog(text, ENTITIES)
        rows.append(item)
    return rows


def parse_review_date(value):
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def overdue_hypotheses(hypotheses):
    today = date.fromisoformat(TODAY)
    items = []
    for item in hypotheses:
        if item["status"] in CLOSED_HYPOTHESIS_STATUSES:
            continue
        review_date = parse_review_date(item["review"])
        if review_date and review_date <= today:
            items.append(item)
    return sorted(items, key=lambda item: (item["review"], item["id"]))


def hypothesis_by_id(hypotheses):
    return {item["id"]: item for item in hypotheses}


def rule_review_rows(hypotheses):
    by_id = hypothesis_by_id(hypotheses)
    rows = []
    for rule in RULE_CANDIDATES:
        due_sources = []
        open_sources = []
        for source_id in rule["sources"]:
            item = by_id.get(source_id)
            if not item:
                continue
            if item["status"] not in CLOSED_HYPOTHESIS_STATUSES:
                open_sources.append(source_id)
            review_date = parse_review_date(item["review"])
            if review_date and review_date <= date.fromisoformat(TODAY) and item["status"] not in CLOSED_HYPOTHESIS_STATUSES:
                due_sources.append(source_id)
        if rule["evidence_count"] >= 3 or due_sources:
            action = rule["next_step"] if rule["status"] == "暂不晋级" else ("进入晋级检查" if rule["evidence_count"] >= 3 else "先处理到期假设")
            rows.append([
                rule["id"],
                one_line(rule["rule"], 64),
                ", ".join(rule["sources"]),
                str(rule["evidence_count"]),
                rule["status"],
                action if not due_sources else f"{action}；到期：{', '.join(due_sources)}",
            ])
    return rows


def review_queue(hypotheses, days=30):
    today = date.fromisoformat(TODAY)
    items = []
    for item in hypotheses:
        if item["status"] in CLOSED_HYPOTHESIS_STATUSES:
            continue
        review_date = parse_review_date(item["review"])
        if not review_date:
            continue
        if review_date <= today or (review_date - today).days <= days:
            items.append(item)
    return sorted(items, key=lambda item: (item["review"], item["id"]))


def concept_counts(cards):
    rows = []
    for concept in CONCEPTS:
        count = sum(1 for card in cards if concept["name"] in card["concepts"])
        if count:
            rows.append((concept["name"], count, concept))
    return sorted(rows, key=lambda item: item[1], reverse=True)


def source_quality_rows(cards):
    grouped = {}
    for card in cards:
        source = card["source"] or "未知"
        grouped.setdefault(source, []).append(card)
    rows = []
    for source, source_cards in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        concepts = {}
        for card in source_cards:
            for name in card["concepts"]:
                concepts[name] = concepts.get(name, 0) + 1
        top_concepts = "、".join(name for name, _ in sorted(concepts.items(), key=lambda item: item[1], reverse=True)[:3]) or "待识别"
        if len(source_cards) >= 10:
            value = "高频来源，适合看反复出现的框架"
        elif len(source_cards) >= 5:
            value = "中频来源，适合补充主题证据"
        else:
            value = "样本偏少，先观察"
        risk = source_risk_summary(source_cards)
        rows.append([source, str(len(source_cards)), top_concepts, value, risk])
    return rows


def safe_page_name(value):
    name = re.sub(r"[\\/:*?\"<>|]+", "", value).strip()
    return name or "未知来源"


def counted_names(cards, key, limit=5):
    counts = {}
    for card in cards:
        for name in card[key]:
            counts[name] = counts.get(name, 0) + 1
    return sorted(counts.items(), key=lambda item: item[1], reverse=True)[:limit]


def source_risk_summary(cards):
    names = [name for name, _ in counted_names(cards, "concepts", 3)]
    text = " ".join(" ".join([card["title"], card["thesis"], card["observe"], card["invalid"], card["risk"]]) for card in cards)
    risks = []
    if any(word in text for word in ["高位", "追高", "冲高回落", "压力位", "放量滞涨"]):
        risks.append("容易受高位波动和追强情绪影响")
    if any(word in text for word in ["仓位", "减仓", "轻仓", "止盈", "卖飞", "定投"]):
        risks.append("仓位建议需要结合自己的成本和执行规则复核")
    if any(word in text for word in ["涨价", "订单", "毛利率", "半年报", "业绩"]):
        risks.append("主题判断必须回到价格、订单、毛利率和业绩验证")
    if any(word in text for word in ["CPI", "美联储", "议息", "美股", "纳斯达克", "外围"]):
        risks.append("宏观映射不能直接推导到 A 股分支")
    if names:
        risks.append(f"观点集中在{'、'.join(names)}，需要跨来源证据过滤")
    return "；".join(risks[:3]) if risks else "样本仍少，先按单篇假设处理"


def source_signal_rows(root, source_cards):
    rows = []
    for card in sorted(source_cards, key=lambda c: c["published"], reverse=True):
        signal = card["observe"] or card["pattern"] or card["thesis"]
        if not signal:
            continue
        verify = card["invalid"] or card["risk"] or "后续需要补市场结构、价格、订单或业绩证据。"
        rows.append([
            obsidian_link(root, card["path"], card["title"]),
            one_line(signal, 72),
            one_line(verify, 58),
        ])
        if len(rows) >= 6:
            break
    return rows


def source_blind_rows(root, source_cards):
    rows = []
    for card in sorted(source_cards, key=lambda c: c["published"], reverse=True):
        blind = card["risk"] or card["invalid"]
        if not blind:
            continue
        rows.append([
            obsidian_link(root, card["path"], card["title"]),
            one_line(blind, 72),
            one_line(card["invalid"] or "后续缺少验证时降权。", 58),
        ])
        if len(rows) >= 6:
            break
    if rows:
        return rows
    return [[obsidian_link(root, card["path"], card["title"]), "卡片里缺少明确反面观点。", "后续同类内容需要补失效条件。"] for card in source_cards[:3]]


def author_profile_pages(root, cards):
    grouped = {}
    for card in cards:
        source = card["source"] or "未知"
        grouped.setdefault(source, []).append(card)
    pages = []
    for source, source_cards in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        if len(source_cards) < 5 or source == "Lil Gator 小鳄鱼":
            continue
        top_concepts = counted_names(source_cards, "concepts", 5)
        top_entities = counted_names(source_cards, "entities", 6)
        concept_names = [name for name, _ in top_concepts]
        entity_names = [name for name, _ in top_entities]
        concept_links = [f"[[concepts/{name}|{name}]]" for name in concept_names]
        entity_links = [f"[[entities/{name}/profile|{name}]]" for name in entity_names]
        recent_rows = [[card["date"], obsidian_link(root, card["path"], card["title"]), one_line(card["thesis"], 58)] for card in sorted(source_cards, key=lambda c: c["published"], reverse=True)[:8]]
        next_review = (date.fromisoformat(TODAY) + timedelta(days=30)).isoformat()
        latest = max(card["date"] for card in source_cards)
        platform = "小红书" if all(card["related_notes"].startswith("xiaohongshu/") for card in source_cards) else "IMA/微信/本地文章卡片"
        concept_text = "、".join(f"{name}（{count}）" for name, count in top_concepts) if top_concepts else "待识别"
        entity_text = "、".join(f"{name}（{count}）" for name, count in top_entities) if top_entities else "待识别"
        relation_text = "、".join(concept_links + entity_links) if concept_links or entity_links else "暂未形成稳定链接"
        signal_rows = source_signal_rows(root, source_cards)
        blind_rows = source_blind_rows(root, source_cards)
        tracking_text = f"后续优先跟踪 {concept_names[0]} 相关的新文章。" if concept_names else "后续优先补足能写清确认信号和失效信号的新文章。"
        if len(concept_names) >= 2:
            tracking_text = f"后续优先跟踪 {concept_names[0]} 和 {concept_names[1]} 是否继续同时出现，并检查它们是否有市场数据或业绩证据。"
        generated = "\n".join([
            page_header(f"来源画像：{source}", "source-profile", "medium"),
            f"# 来源画像：{source}",
            "",
            "> 这里评估来源质量，不记录原文，不构成买卖建议。",
            "",
            "## 基本信息",
            "",
            render_table(["项目", "内容"], [
                ["平台", platform],
                ["作者", source],
                ["已读笔记", str(len(source_cards))],
                ["最近更新", latest],
                ["下次复核", next_review],
            ]),
            "",
            "## 反复出现的主题",
            "",
            f"这个来源反复围绕 {concept_text} 展开。具体落点集中在 {entity_text}。使用时先看这些主题是否连续出现，再回到市场数据和后续复盘确认。",
            "",
            "## 有用的信号",
            "",
            render_table(["文章", "可提取的信号", "需要怎么验证"], signal_rows),
            "",
            "## 盲点和噪音",
            "",
            render_table(["文章", "可能的盲点或噪音", "降权条件"], blind_rows),
            "",
            "## 和现有知识库的关系",
            "",
            f"当前最相关的知识库入口是 {relation_text}。这些链接说明该来源已经能补充知识库主题，但不代表这些主题已经成为正式规则。",
            "",
            "## 继续跟踪条件",
            "",
            f"{tracking_text} 若后续内容能持续给出可验证指标、反面条件和复盘结果，就保持观察；若大量内容变成单日情绪、无法验证的题材判断或缺少失效条件，则降低来源权重。",
            "",
            "## 最近样本",
            "",
            render_table(["日期", "文章", "核心线索"], recent_rows),
        ])
        pages.append((root / "source-profiles" / f"{safe_page_name(source)}.md", generated))
    return pages


def source_profile_rows(root, cards):
    rows = []
    for source, count, themes, value, risk in source_quality_rows(cards):
        if int(count) < 5:
            continue
        if source == "Lil Gator 小鳄鱼":
            path = root / "source-profiles" / f"xiaohongshu__{safe_page_name(source)}.md"
        else:
            path = root / "source-profiles" / f"{safe_page_name(source)}.md"
        status = "已生成" if path.exists() else "待生成"
        rows.append([obsidian_link(root, path, source), count, themes, value, status, risk])
    return rows


def one_line(text, limit=80):
    cleaned = re.sub(r"\s+", " ", text).strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1] + "…"


def page_header(title, page_type, confidence="medium"):
    return "\n".join([
        "---",
        f"title: {title}",
        f"type: {page_type}",
        "domain: [investing]",
        f"created: {TODAY}",
        f"updated: {TODAY}",
        f"confidence: {confidence}",
        "---",
        "",
    ])


def render_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    if rows:
        lines.extend("| " + " | ".join(row) + " |" for row in rows)
    else:
        lines.append("| " + " | ".join(["暂无"] * len(headers)) + " |")
    return "\n".join(lines)


def render_concept(root, concept, cards, hypotheses):
    name = concept["name"]
    related_cards = [card for card in cards if name in card["concepts"]]
    related_hypotheses = [item for item in hypotheses if name in item["concepts"]]
    entity_links = [f"[[entities/{entity}/profile|{entity}]]" for entity in concept["entities"]]
    source_rows = []
    for card in sorted(related_cards, key=lambda c: c["published"], reverse=True)[:8]:
        source_rows.append([card["date"], card["source"] or "未知", obsidian_link(root, card["path"], card["title"]), one_line(card["thesis"], 70)])
    hypo_rows = []
    for item in sorted(related_hypotheses, key=lambda h: h["date"], reverse=True):
        hypo_rows.append([item["id"], item["date"], one_line(item["hypothesis"], 72), item["status"], item["review"]])
    use_rows = [
        ["当前看法", concept["summary"]],
        ["适用场景", "只在来源、行情和验证信号能互相对上时使用，不能把单篇观点当成结论。"],
        ["优先确认", "；".join(concept["watch"][:3])],
        ["立即降权", "；".join(concept["fail"][:2])],
        ["下一步", "先处理关联假设里复盘日期最近的项目，再决定是否升级、延后或降权。"],
    ]
    lines = [page_header(name, "concept"), f"# {name}", "", f"> {concept['summary']}", "", "## 当前结论", ""]
    lines.append(f"截至 {TODAY}，这个主题共连接 {len(related_cards)} 张文章卡片和 {len(related_hypotheses)} 条假设。当前只作为研究框架，不直接构成买卖建议。")
    lines += ["", "## 投资使用摘要", "", render_table(["项目", "内容"], use_rows), "", "## 相关对象", "", ", ".join(entity_links) if entity_links else "暂无", "", "## 关联假设", "", render_table(["编号", "日期", "假设", "状态", "复盘日期"], hypo_rows), "", "## 来源卡片", "", render_table(["日期", "来源", "文章", "相关线索"], source_rows), "", "## 观察指标", ""]
    lines.extend(f"- {item}" for item in concept["watch"])
    lines += ["", "## 失效信号", ""]
    lines.extend(f"- {item}" for item in concept["fail"])
    lines += [
        "",
        "## 待解决问题",
        "",
        f"- {concept['watch'][0]} 是否已经有独立行情、订单或财务数据支持。",
        f"- 如果出现“{concept['fail'][0]}”，这个主题是否需要从重点观察降权。",
        "- 当前证据是否过度集中在少数作者或少数交易日。",
        "- 是否已经能写成明确仓位边界、观察条件或复盘动作。",
    ]
    return preserve_manual(root / "concepts" / f"{name}.md", "\n".join(lines))


def render_entity(root, entity, cards, hypotheses):
    name = entity["name"]
    related_cards = [card for card in cards if name in card["entities"]]
    related_hypotheses = [item for item in hypotheses if name in item["entities"]]
    concept_names = sorted({concept["name"] for concept in CONCEPTS if name in concept["entities"]})
    concept_links = [f"[[concepts/{concept}|{concept}]]" for concept in concept_names]
    source_rows = []
    for card in sorted(related_cards, key=lambda c: c["published"], reverse=True)[:20]:
        source_rows.append([card["date"], card["source"] or "未知", obsidian_link(root, card["path"], card["title"]), one_line(card["observe"] or card["thesis"], 72)])
    hypo_rows = []
    for item in sorted(related_hypotheses, key=lambda h: h["date"], reverse=True):
        hypo_rows.append([item["id"], item["date"], one_line(item["hypothesis"], 72), item["status"], item["review"]])
    header = "\n".join([
        "---",
        f"title: {name}",
        "type: entity",
        "domain: [investing]",
        f"created: {TODAY}",
        f"updated: {TODAY}",
        "confidence: medium",
        f"aliases: [{', '.join(entity['aliases'])}]",
        "judgment: watching",
        "---",
        "",
    ])
    lines = [header, f"# {name}", "", f"> {entity['focus']}", "", "## 当前判断", ""]
    lines.append(f"截至 {TODAY}，该对象关联 {len(related_cards)} 张文章卡片和 {len(related_hypotheses)} 条假设。结论仍需价格、订单、利润或市场结构继续验证。")
    lines += ["", "## 相关概念", "", ", ".join(concept_links) if concept_links else "暂无", "", "## 关联假设", "", render_table(["编号", "日期", "假设", "状态", "复盘日期"], hypo_rows), "", "## 证据来源", "", render_table(["日期", "来源", "文章", "观察线索"], source_rows), "", "## 跟踪清单", "", "- 价格或成交是否提供独立确认。", "- 订单、利润、半年报或政策是否补上验证。", "- 强势是否来自板块自身，还是只来自指数或情绪修复。", "- 如果跌破关键结构，是否需要从观察页降权。"]
    return preserve_manual(root / "entities" / name / "profile.md", "\n".join(lines))


def render_rules(root, hypotheses):
    rows = [[rule["id"], rule["rule"], ", ".join(rule["sources"]), str(rule["evidence_count"]), rule["status"]] for rule in RULE_CANDIDATES]
    review_rows = rule_review_rows(hypotheses)
    gap_rows = [[rule["id"], rule["status"], rule["gap"], rule["next_step"]] for rule in RULE_CANDIDATES]
    generated = "\n".join([
        page_header("投资规则", "meta", "medium"),
        "# 投资规则",
        "",
        "> 这里记录被重复证据支持、但仍需要复盘确认的投资规律。只有经过数据或多来源验证后，才进入正式规则。",
        "",
        "## 生命周期",
        "",
        "observation -> pattern（至少 2 次）-> rule（至少 3 次并完成复盘）-> under review -> retired 或 updated",
        "",
        "## 候选规则池",
        "",
        render_table(["编号", "候选规则", "来源假设", "证据次数", "状态"], rows),
        "",
        "## 晋级检查",
        "",
        render_table(["编号", "候选规则", "来源假设", "证据次数", "状态", "下一步"], review_rows),
        "",
        "晋级前必须确认：适用场景清楚、确认信号可观察、失效信号可执行、反例已经记录，且规则会改变仓位或买卖边界。",
        "",
        "## 缺口视图",
        "",
        render_table(["编号", "状态", "缺什么", "下一步"], gap_rows),
        "",
        "## 已确认规则",
        "",
        "| 编号 | 规则 | 首次确认 | 最近确认 | 适用边界 |",
        "| --- | --- | --- | --- | --- |",
        "| 暂无 | 需要样本检查或周复盘确认后再晋级。 |  |  |  |",
        "",
        "## 复核中规则",
        "",
        "- 暂无。",
        "",
        "## 已退役规则",
        "",
        "- 暂无。被证伪后保留在这里，不删除。",
    ])
    return preserve_manual(root / "rules.md", generated)


def render_false_beliefs(root):
    generated = "\n".join([
        page_header("被证伪或需要降权的认知", "meta", "medium"),
        "# 被证伪或需要降权的认知",
        "",
        "> 这里记录容易误导投资判断的旧认知。它们不一定永远错误，但必须写清楚适用边界。",
        "",
        "## 条目",
        "",
        "### FB1：低位长期不动可以处理所有仓位",
        "",
        "- 旧认知：只要位置够低，长期不动就能解决大部分问题。",
        "- 现实：只有低成本、基本面无硬伤、退出节点明确的仓位才适合长期处理；高波动成长仓和事件仓需要失效条件。",
        "- 来源：[[state/hypothesis-ledger|H-20260530-001]]",
        "- 适用范围：仓位管理、长线持仓、观察仓。",
        "",
        "### FB2：缩量反弹一定弱",
        "",
        "- 旧认知：反弹只要缩量，就可以直接判断失败。",
        "- 现实：大跌后的第一段反弹可能天然缩量，需要结合位置、阳线力度和主线承接；高位缩量创新高才更偏风险信号。",
        "- 来源：[[state/hypothesis-ledger|H-20260609-002]]、[[state/hypothesis-ledger|H-20260607-003]]",
        "- 适用范围：指数修复、科技主线回调后修复。",
        "",
        "### FB3：纳斯达克反弹就等于 A 股科技会跟",
        "",
        "- 旧认知：海外科技上涨后，A 股科技分支会自然跟涨。",
        "- 现实：A 股科技能否参与，取决于 CPO、PCB、半导体、自动化设备等分支自己的结构和资金承接。",
        "- 来源：[[state/hypothesis-ledger|H-20260608-001]]",
        "- 适用范围：海外链、科技分支轮动。",
        "",
        "### FB4：高股息可以无视利率变化",
        "",
        "- 旧认知：高股息因为有分红，任何时候都能作为稳定底仓。",
        "- 现实：高股息资产的优势依赖低利率环境；利率上行时，股价需要重新匹配无风险收益。",
        "- 来源：[[state/hypothesis-ledger|H-20260607-001]]",
        "- 适用范围：银行、电力、公用事业、类债股。",
    ])
    return preserve_manual(root / "false-beliefs.md", generated)


def render_source_quality(root, cards):
    rows = source_quality_rows(cards)
    generated = "\n".join([
        page_header("来源质量总表", "source-profile", "medium"),
        "# 来源质量总表",
        "",
        "> 这里记录不同作者适合提供哪类参考，以及使用时必须保留的验证边界。互动热度和更新频率不等于观点正确。",
        "",
        "## 来源速览",
        "",
        render_table(["来源", "卡片数", "主要主题", "适合怎么用", "风险"], rows),
        "",
        "## 使用规则",
        "",
        "- 高频来源只代表样本多，不代表结论更真。",
        "- 同一作者反复出现的观点，可以作为假设来源，但必须回到确认信号和失效信号。",
        "- 来源观点发生冲突时，优先写入主题页、规则缺口或错误认知页，不要直接删除旧判断。",
        "- 新作者至少读 5 篇后再建立来源画像，少于 5 篇只放在本表里观察。",
    ])
    return preserve_manual(root / "source-profiles" / "source-quality.md", generated)


def render_structure_review(root):
    generated = "\n".join([
        page_header("知识库结构复核", "meta", "medium"),
        "# 知识库结构复核",
        "",
        "> 这里记录结构优化时的外部审阅和待办。Mimo CLI 审阅结果用于校准可读性和可用性，不直接覆盖知识库。",
        "",
        "## 本轮目标",
        "",
        "| 项目 | 内容 |",
        "| --- | --- |",
        "| 优化方向 | 把知识库从证据沉淀库升级成投资参考驾驶舱 |",
        "| 重点页面 | overview、knowledge-attention、rules、concepts、source-profiles |",
        "| 验证要求 | 刷新后断链为 0，日期审计通过，GitHub 归档同步 |",
        "",
        "## Mimo 复核状态",
        "",
        "| 项目 | 状态 | 说明 |",
        "| --- | --- | --- |",
        "| CLI 可用性 | 已完成 | 已在 finance-analysis 目录内运行只读审阅 |",
        "| 审阅方式 | 只读 | 不让 Mimo 直接改文件 |",
        "| 采纳方式 | 人工合并 | Codex 根据审阅意见改生成脚本和派生页面 |",
        "",
        "## 已采纳建议",
        "",
        "| 建议 | 处理结果 |",
        "| --- | --- |",
        "| 首页缺少当前重点 | 已在 overview 增加复盘队列、高关注主题、规则状态、来源质量和最近新增 |",
        "| 概念页只有计数没有使用摘要 | 已增加“投资使用摘要”，并把来源卡片压缩到最近 8 条 |",
        "| 统一待解决问题像模板占位 | 已改为按主题生成具体问题 |",
        "| 来源评价只覆盖小红书作者 | 已增加来源质量总表，并为样本不少于 5 篇的作者生成来源画像 |",
        "| 规则页和注意事项重复 | 已将注意事项中的规则区改为缺口摘要，完整规则保留在 rules |",
        "",
        "## 延后处理",
        "",
        "| 建议 | 延后原因 |",
        "| --- | --- |",
        "| 给假设追踪清单增加优先级列 | 会影响现有审计和解析逻辑，先用复盘队列解决优先级问题 |",
        "| 合并 daily 和 source-cards 的重复内容 | 涉及历史 daily 页面和文章卡片契约，单独做迁移更稳 |",
        "| 区分短评卡片和策略卡片模板 | 需要先给卡片分类打标签，避免破坏已有卡片结构 |",
    ])
    return preserve_manual(root / "state" / "structure-review.md", generated)



def upsert_card_links(root, cards):
    changed = 0
    for card in cards:
        concept_links = [f"[[concepts/{name}|{name}]]" for name in card["concepts"]]
        entity_links = [f"[[entities/{name}/profile|{name}]]" for name in card["entities"]]
        rows = []
        if concept_links:
            rows.append("| 相关概念 | " + "、".join(concept_links) + " |")
        if entity_links:
            rows.append("| 相关对象 | " + "、".join(entity_links) + " |")
        if not rows:
            continue
        block = "\n".join(["", "## 知识库链接", "", LINKS_START, "| 类型 | 链接 |", "| --- | --- |", *rows, LINKS_END, ""])
        content = card["content"]
        if LINKS_START in content and LINKS_END in content:
            pattern = re.compile(r"\n## 知识库链接\n\n" + re.escape(LINKS_START) + r"[\s\S]*?" + re.escape(LINKS_END) + r"\n?", re.MULTILINE)
            new_content = pattern.sub(block.rstrip() + "\n", content)
        else:
            new_content = content.rstrip() + "\n" + block
        if write_if_changed(card["path"], new_content):
            changed += 1
    return changed


def parse_frontmatter(content):
    match = re.match(r"\A---\n([\s\S]*?)\n---", content)
    if not match:
        return {}
    data = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def source_url_hash(content):
    fm = parse_frontmatter(content)
    source = fm.get("source", "")
    if not source:
        return ""
    return hash_text(source)


def source_url(content):
    return parse_frontmatter(content).get("source", "")


def raw_note_path(vault, related_notes):
    if not related_notes or related_notes.startswith("xiaohongshu/"):
        return None
    candidate = vault / related_notes
    if candidate.is_file():
        return candidate
    return None


def asset_lookup(vault):
    roots = [vault / "ima" / "attachments", vault / "finance-analysis" / "source-evidence"]
    lookup = {}
    for root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_file():
                lookup.setdefault(path.name, path)
    return lookup


def source_asset_names(content):
    names = []
    for link in wikilinks(content):
        target = link.split("|", 1)[0].strip()
        name = PurePosixPath(target).name
        if re.search(r"\.(png|jpe?g|gif|webp|svg)$", name, re.IGNORECASE):
            names.append(name)
    return sorted(set(names))


def copy_source_assets(evidence_path, source_content, assets):
    rows = []
    for name in source_asset_names(source_content):
        source = assets.get(name)
        status = "未找到"
        link = name
        if source and source.is_file():
            target = evidence_path.parent / "assets" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists() or source.read_bytes() != target.read_bytes():
                shutil.copy2(source, target)
            status = "已归档"
            link = f"assets/{name}"
        rows.append([name, link, status])
    return rows


def strip_frontmatter(content):
    return re.sub(r"\A---\n[\s\S]*?\n---\n?", "", content, count=1)


def evidence_path_for_card(root, card):
    month = card["date"][:7] if re.match(r"^\d{4}-\d{2}", card["date"]) else "unknown"
    return root / "source-evidence" / month / card["path"].name


def render_source_evidence(vault, root, cards):
    changed = 0
    rows = []
    assets = asset_lookup(vault)
    for card in sorted(cards, key=lambda item: (item["date"], item["source"], item["title"])):
        note_path = raw_note_path(vault, card["related_notes"])
        evidence_link = "暂无"
        status = "无本地全文"
        body_hash = "暂无"
        url_hash = "暂无"
        if note_path:
            source_content = read_text(note_path)
            body = source_content.strip()
            raw_url = source_url(source_content)
            body_hash = hash_text(body) if body else "暂无"
            url_hash = source_url_hash(source_content) or "暂无"
            evidence_path = evidence_path_for_card(root, card)
            asset_rows = copy_source_assets(evidence_path, source_content, assets)
            evidence_link = obsidian_link(root, evidence_path, "原文")
            status = "已归档全文" if body else "原文为空"
            content = "\n".join([
                page_header(f"原文依据：{card['title']}", "source-evidence", "medium"),
                f"# 原文依据：{card['title']}",
                "",
                "> 这里保存本地原文全文和原始链接，用来追溯文章卡片和后续假设的底层依据。",
                "",
                "## 基本信息",
                "",
                render_table(["项目", "内容"], [
                    ["来源", card["source"] or "未知"],
                    ["发布时间", card["published"]],
                    ["文章卡片", obsidian_link(root, card["path"], card["title"])],
                    ["本地来源", card["related_notes"]],
                    ["正文指纹", body_hash],
                    ["原文链接指纹", url_hash],
                ]),
                "",
                "## 原始链接",
                "",
                "```text",
                raw_url,
                "```",
                "",
                "## 附件",
                "",
                render_table(["文件", "归档位置", "状态"], asset_rows),
                "",
                "## 原文全文",
                "",
                body.rstrip(),
                "",
            ])
            if write_if_changed(evidence_path, content):
                changed += 1
        rows.append([
            card["date"] or "未知",
            card["source"] or "未知",
            one_line(card["title"], 32),
            obsidian_link(root, card["path"], card["title"]),
            evidence_link,
            status,
            body_hash,
        ])
    index = "\n".join([
        page_header("原文依据索引", "source-evidence", "medium"),
        "# 原文依据索引",
        "",
        "> 这里是文章卡片背后的底层依据层。微信和本地文章会归档本地全文和原始链接；小红书等没有本地全文的来源，先保留卡片和笔记编号。",
        "",
        "## 速览",
        "",
        render_table(["项目", "内容"], [
            ["文章卡片", str(len(cards))],
            ["已归档全文", str(sum(1 for row in rows if row[5] == "已归档全文"))],
            ["无本地全文", str(sum(1 for row in rows if row[5] == "无本地全文"))],
            ["生成日期", TODAY],
        ]),
        "",
        "## 原文索引",
        "",
        render_table(["日期", "来源", "标题", "文章卡片", "原文", "状态", "正文指纹"], rows),
    ])
    changed += int(write_if_changed(root / "source-evidence" / "index.md", index))
    return changed


def page_title(path, content):
    fm = parse_frontmatter(content)
    if fm.get("title"):
        return fm["title"]
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if match:
        return clean_title(match.group(1))
    return path.stem


def page_type(root, path, content):
    fm = parse_frontmatter(content)
    if fm.get("type"):
        return fm["type"]
    rel = path.relative_to(root).as_posix()
    if rel.startswith("source-cards/"):
        return "source-card"
    if rel.startswith("source-evidence/"):
        return "source-evidence"
    if rel.startswith("daily/"):
        return "daily"
    if rel.startswith("strategy-candidates/"):
        return "strategy-candidate"
    if rel.startswith("concepts/"):
        return "concept"
    if rel.startswith("entities/"):
        return "entity"
    if rel.startswith("state/"):
        return "state"
    return "note"


def build_index(root):
    pages = []
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        if rel.startswith(".") or rel.endswith("_template.md"):
            continue
        content = read_text(path)
        pages.append({
            "path": rel,
            "title": page_title(path, content),
            "type": page_type(root, path, content),
            "links": wikilinks(content),
            "updated": TODAY,
        })
    aliases = {}
    for page in pages:
        path_no_ext = PurePosixPath(page["path"]).with_suffix("").as_posix()
        names = {path_no_ext, PurePosixPath(page["path"]).stem, page["title"]}
        parts = PurePosixPath(page["path"]).parts
        if len(parts) >= 3 and parts[0] in {"source-cards", "source-evidence"}:
            names.add(f"{parts[0]}/{PurePosixPath(page['path']).stem}")
        if PurePosixPath(page["path"]).name == "profile.md":
            names.add(PurePosixPath(page["path"]).parent.name)
            names.add(PurePosixPath(page["path"]).parent.as_posix())
        for name in names:
            aliases.setdefault(name.lower(), set()).add(page["path"])
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix == ".md":
            continue
        rel = path.relative_to(root).as_posix()
        path_no_ext = PurePosixPath(rel).with_suffix("").as_posix()
        names = {rel, path_no_ext, path.name, path.stem}
        for name in names:
            aliases.setdefault(name.lower(), set()).add(rel)
    inbound = {}
    broken = []
    for page in pages:
        resolved = set()
        for link in page["links"]:
            key = link.split("|", 1)[0].strip().removesuffix(".md").lower()
            matches = aliases.get(key, set())
            if matches:
                resolved.update(matches)
            else:
                broken.append({"from": page["path"], "link": link})
        page["resolved_links"] = sorted(resolved)
        for target in sorted(resolved):
            inbound.setdefault(target, []).append(page["path"])
    by_type = {}
    for page in pages:
        by_type.setdefault(page["type"], []).append(page["path"])
    inbound = {key: sorted(value) for key, value in sorted(inbound.items())}
    broken = sorted(broken, key=lambda item: (item["from"], item["link"]))
    return {"generated_at": TODAY, "total_pages": len(pages), "pages": pages, "by_type": by_type, "inbound": inbound, "broken_links": broken}


def render_overview(root, index, cards, hypotheses):
    concept_count = len(index["by_type"].get("concept", []))
    entity_count = len(index["by_type"].get("entity", []))
    source_count = len(index["by_type"].get("source-card", []))
    hypo_count = len(hypotheses)
    due_count = len(overdue_hypotheses(hypotheses))
    queue = review_queue(hypotheses, 30)
    queue_rows = [[item["review"], item["id"], one_line(item["hypothesis"], 54), item["status"]] for item in queue[:8]]
    concept_rows = [[f"[[concepts/{name}|{name}]]", str(count), one_line(concept["summary"], 52)] for name, count, concept in concept_counts(cards)[:8]]
    recent_rows = [[card["date"], card["source"] or "未知", obsidian_link(root, card["path"], card["title"]), one_line(card["thesis"], 50)] for card in sorted(cards, key=lambda c: c["published"], reverse=True)[:8]]
    rule_rows = [[rule["id"], rule["status"], rule["gap"], rule["next_step"]] for rule in RULE_CANDIDATES]
    source_rows = source_quality_rows(cards)[:8]
    lines = [
        page_header("投资知识库总览", "meta", "medium"),
        "# 投资知识库总览",
        "",
        "> 这是给投资复盘和后续提问使用的入口页。所有结论都应回到假设、证据、失效条件和复盘日期。",
        "",
        "## 速览",
        "",
        render_table(["项目", "数量", "入口"], [
            ["文章卡片", str(source_count), "source-cards/"],
            ["待验证假设", str(hypo_count), "[[state/hypothesis-ledger|假设追踪清单]]"],
            ["到期复盘", str(due_count), "[[state/knowledge-attention|知识库注意事项]]"],
            ["规则复核项", str(len(rule_review_rows(hypotheses))), "[[rules|投资规则]]"],
            ["概念页", str(concept_count), "[[concepts/国产替代|概念入口示例]]"],
            ["对象页", str(entity_count), "[[entities/半导体材料/profile|对象入口示例]]"],
        ]),
        "",
        "## 投资参考驾驶舱",
        "",
        "先看这里，再决定要不要进入具体主题页。这里不提供买卖指令，只提示当前最值得复盘和补证据的地方。",
        "",
        "### 复盘队列",
        "",
        render_table(["复盘日期", "编号", "假设", "状态"], queue_rows),
        "",
        "### 高关注主题",
        "",
        render_table(["主题", "文章卡片数", "当前用法"], concept_rows),
        "",
        "### 规则状态",
        "",
        render_table(["编号", "状态", "缺什么", "下一步"], rule_rows),
        "",
        "### 来源质量",
        "",
        render_table(["来源", "卡片数", "主要主题", "适合怎么用", "风险"], source_rows),
        "",
        "### 最近新增",
        "",
        render_table(["日期", "来源", "文章", "核心线索"], recent_rows),
        "",
        "## 优先查看",
        "",
        "- [[state/knowledge-attention|知识库注意事项]]：过期复盘、主题集中度和冲突提示。",
        "- [[rules|投资规则]]：已经反复出现、但仍需样本确认的候选规则。",
        "- [[false-beliefs|被证伪或需要降权的认知]]：避免重复犯错的页面。",
        "- [[concepts/国产替代|国产替代]]、[[concepts/涨价方向|涨价方向]]、[[concepts/科技材料第二波|科技材料第二波]]：当前证据最密集的主题。",
        "",
        "## 使用方式",
        "",
        "- 看单篇观点时，先读文章卡片，再顺着“知识库链接”进入相关概念和对象。",
        "- 做交易前，只把这里当作研究参考，不把任何作者观点直接当成买卖指令。",
        "- 每周复盘时优先处理过期假设和冲突观察，确认、降权或加入被证伪认知。",
    ]
    return "\n".join(lines).rstrip() + "\n"


def render_attention(root, cards, hypotheses):
    due = overdue_hypotheses(hypotheses)
    queue = review_queue(hypotheses, 30)
    concept_counts = []
    for concept in CONCEPTS:
        count = sum(1 for card in cards if concept["name"] in card["concepts"])
        if count:
            concept_counts.append((concept["name"], count))
    concept_counts.sort(key=lambda item: item[1], reverse=True)
    due_rows = [[item["id"], item["date"], one_line(item["hypothesis"], 64), item["review"], item["status"], "确认、降权、延后观察或写入错误认知"] for item in due]
    queue_rows = [[item["review"], item["id"], one_line(item["hypothesis"], 64), item["status"], "到期前准备证据，不能只保留观察中"] for item in queue[:12]]
    rule_rows = [[rule["id"], rule["status"], rule["gap"], rule["next_step"]] for rule in RULE_CANDIDATES]
    concept_rows = [[f"[[concepts/{name}|{name}]]", str(count), "需要保持证据和失效条件同步更新"] for name, count in concept_counts[:12]]
    source_rows = source_profile_rows(root, cards)
    lines = [
        page_header("知识库注意事项", "meta", "medium"),
        "# 知识库注意事项",
        "",
        f"> 自动生成于 {TODAY}。这里不提供买卖建议，只提示哪些地方需要复盘、降权或补证据。",
        "",
        "## 需要处理的复盘",
        "",
        render_table(["编号", "日期", "假设", "复盘日期", "状态", "处理动作"], due_rows),
        "",
        "## 规则晋级检查",
        "",
        render_table(["编号", "状态", "缺什么", "下一步"], rule_rows),
        "",
        "处理顺序：先处理到期假设，再决定候选规则是否晋级；证据不足时先降权或延后观察，不让旧判断长期停留在观察中。",
        "",
        "## 未来 30 天复盘队列",
        "",
        render_table(["复盘日期", "编号", "假设", "状态", "处理要求"], queue_rows),
        "",
        "## 主题集中度",
        "",
        render_table(["主题", "文章卡片数", "处理建议"], concept_rows),
        "",
        "## 来源画像覆盖",
        "",
        render_table(["来源", "卡片数", "主要主题", "适合怎么用", "画像状态", "使用风险"], source_rows),
        "",
        "## 冲突观察",
        "",
        "- 缩量反弹并不总是失败，但高位缩量上涨也可能是风险信号；后续复盘必须区分“大跌后第一段修复”和“高位缩量创新高”。",
        "- 轻仓能降低回撤，也可能在直接放量修复时踏空；后续复盘必须把事件窗口、利润垫和可执行补仓条件写清楚。",
        "- 国产替代和涨价方向当前证据密集，但不能只看叙事；需要继续用订单、价格、毛利率和半年报验证。",
        "",
        "## 下次刷新要检查",
        "",
        "- 过期假设是否已经确认、部分确认、证伪或需要延后。",
        "- 高频主题是否需要合并成正式规则，或拆成更窄的适用场景。",
        "- 文章卡片是否都能链接到至少一个概念或对象。",
    ]
    return "\n".join(lines).rstrip() + "\n"


def run(args):
    vault = Path(args.vault).expanduser() if args.vault else find_vault()
    root = vault / "finance-analysis"
    if not root.is_dir():
        raise SystemExit("knowledge_base_status=blocked\nreason=finance_analysis_not_found")
    for rel in ["concepts", "entities", "explorations", "decisions", "comparisons", "source-evidence", "state"]:
        (root / rel).mkdir(parents=True, exist_ok=True)
    cards = parse_cards(root)
    hypotheses = parse_hypotheses(root)
    changed = 0
    changed += upsert_card_links(root, cards)
    cards = parse_cards(root)
    changed += render_source_evidence(vault, root, cards)
    for concept in CONCEPTS:
        changed += int(write_if_changed(root / "concepts" / f"{concept['name']}.md", render_concept(root, concept, cards, hypotheses)))
    for entity in ENTITIES:
        changed += int(write_if_changed(root / "entities" / entity["name"] / "profile.md", render_entity(root, entity, cards, hypotheses)))
    changed += int(write_if_changed(root / "rules.md", render_rules(root, hypotheses)))
    changed += int(write_if_changed(root / "false-beliefs.md", render_false_beliefs(root)))
    changed += int(write_if_changed(root / "source-profiles" / "source-quality.md", render_source_quality(root, cards)))
    profile_pages = author_profile_pages(root, cards)
    changed_profiles = []
    for path, content in profile_pages:
        if write_if_changed(path, preserve_manual(path, content)):
            changed += 1
            changed_profiles.append(path.stem)
    changed += int(write_if_changed(root / "state" / "structure-review.md", render_structure_review(root)))
    preview_index = build_index(root)
    changed += int(write_if_changed(root / "overview.md", render_overview(root, preview_index, cards, hypotheses)))
    changed += int(write_if_changed(root / "state/knowledge-attention.md", render_attention(root, cards, hypotheses)))
    index = build_index(root)
    changed += int(write_if_changed(root / "state/knowledge-index.json", json.dumps(index, ensure_ascii=False, indent=2) + "\n"))
    print("knowledge_base_status=updated")
    print(f"cards={len(cards)}")
    print(f"hypotheses={len(hypotheses)}")
    print(f"concept_pages={len(CONCEPTS)}")
    print(f"entity_pages={len(ENTITIES)}")
    print(f"source_profiles={len(profile_pages)}")
    print(f"updated_source_profiles={','.join(changed_profiles) if changed_profiles else 'none'}")
    print(f"overdue_hypotheses={len(overdue_hypotheses(hypotheses))}")
    print(f"rule_review_items={len(rule_review_rows(hypotheses))}")
    print(f"changed_files_or_cards={changed}")
    print(f"broken_links={len(index['broken_links'])}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", default="")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
