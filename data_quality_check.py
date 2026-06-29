#!/usr/bin/env python3
# SIP CLASS 飞书数据质量检查脚本
import json
from collections import defaultdict, Counter
from datetime import datetime

DATA_PATH = '/Users/yangyang/Desktop/sip-dashboard/data.json'


def load_data(path=DATA_PATH):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def check_all(data=None):
    if data is None:
        data = load_data()

    prods = data['tables']['products']['records']
    sales = data['tables']['sales']['records']
    inv = data['tables']['inventory']['records']
    anchors = data['tables']['anchors']['records']
    buyers = data['tables']['buyers']['records']

    report = []
    report.append('=' * 60)
    report.append('SIP CLASS 数据质量检查报告')
    report.append(f'生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    report.append('=' * 60)

    # 1. 产品资料库
    report.append('\n【产品资料库】')
    report.append(f'  记录数：{len(prods)}')
    prod_sku_map = {}
    dup_skus = []
    for p in prods:
        sku = p.get('SKU编码')
        if sku:
            if sku in prod_sku_map:
                dup_skus.append(sku)
            prod_sku_map[sku] = p
    report.append(f'  SKU重复：{dup_skus if dup_skus else "无"}')

    missing = []
    for p in prods:
        if not p.get('款式名称'):
            missing.append(('款式名称缺失', p.get('SKU编码')))
        if not p.get('SKU编码'):
            missing.append(('SKU编码缺失', p.get('款式名称')))
        if p.get('吊牌价') is None:
            missing.append(('吊牌价缺失', p.get('SKU编码')))
        if p.get('成本价/件') is None:
            missing.append(('成本价缺失', p.get('SKU编码')))
    report.append(f'  必填字段缺失：{missing[:5] if missing else "无"}')

    # 2. 销售数据
    report.append('\n【销售数据】')
    report.append(f'  记录数：{len(sales)}')
    sku_set = set(prod_sku_map.keys())
    unknown_skus = set()
    unknown_styles = set()
    channel_issues = []
    date_issues = []
    negative_issues = []
    refund_records = []
    sales_records = []
    channel_dist = defaultdict(int)

    for s in sales:
        sku = s.get('SKU编码')
        style_lookup = s.get('🔗 款式名称')
        style_name = s.get('款式名称') or style_lookup
        channel = (s.get('渠道') or '').strip()
        date = s.get('销售日期')
        amt = s.get('销售额')
        qty = s.get('销量件数')
        refund_week = s.get('退款周次')

        is_refund = bool((sku and str(sku).startswith('R-')) or refund_week)
        if is_refund:
            refund_records.append(s)
        else:
            sales_records.append(s)

        if sku and sku not in sku_set:
            unknown_skus.add(sku)
        if style_name and style_name not in [p.get('款式名称') for p in prods]:
            unknown_styles.add(style_name)
        if not channel:
            channel_issues.append(('渠道为空', sku, date))
        else:
            channel_dist[channel] += 1
        if date and not str(date).startswith('20'):
            date_issues.append(('日期异常', sku, date))
        try:
            if amt is not None and float(amt) < 0:
                negative_issues.append(('销售额为负', sku, amt))
            if qty is not None and float(qty) < 0:
                negative_issues.append(('销量为负', sku, qty))
        except Exception:
            pass

    report.append(f'  渠道分布：{dict(channel_dist)}')
    report.append(f'  销售记录：{len(sales_records)} 条')
    report.append(f'  退款记录：{len(refund_records)} 条')
    report.append(f'  未知SKU（{len(unknown_skus)} 个）：{list(unknown_skus)[:10] if unknown_skus else "无"}')
    report.append(f'  未知款式：{list(unknown_styles)[:10] if unknown_styles else "无"}')
    report.append(f'  渠道为空：{len(channel_issues)} 条')
    report.append(f'  日期异常：{date_issues[:3] if date_issues else "无"}')
    report.append(f'  负值异常：{negative_issues[:3] if negative_issues else "无"}')

    # 3. 库存数据
    report.append('\n【库存数据】')
    report.append(f'  记录数：{len(inv)}')
    inv_unknown_skus = set()
    inv_dup_skus = []
    inv_seen = set()
    inv_date_issues = []
    for i in inv:
        sku = i.get('SKU编码')
        if sku:
            if sku in inv_seen:
                inv_dup_skus.append(sku)
            inv_seen.add(sku)
            if sku not in sku_set:
                inv_unknown_skus.add(sku)
        date = i.get('入库日期')
        if date and not str(date).startswith('20'):
            inv_date_issues.append(('入库日期异常', sku, date))

    report.append(f'  SKU重复（同一SKU多次入库）：{inv_dup_skus[:10] if inv_dup_skus else "无"}')
    report.append(f'  重复SKU数：{len(inv_dup_skus)}')
    report.append(f'  未知SKU：{list(inv_unknown_skus)[:10] if inv_unknown_skus else "无"}')
    report.append(f'  入库日期异常：{inv_date_issues[:3] if inv_date_issues else "无"}')

    # 4. 主播资料库
    report.append('\n【主播资料库】')
    report.append(f'  记录数：{len(anchors)}')
    anchor_names = [a.get('直播间名称') for a in anchors if a.get('直播间名称')]
    report.append(f'  直播间名称缺失：{len(anchors) - len(anchor_names)} 条')
    anchor_dups = [n for n, c in Counter(anchor_names).items() if c > 1]
    report.append(f'  直播间名称重复：{anchor_dups if anchor_dups else "无"}')

    # 5. 买手店资料库
    report.append('\n【买手店资料库】')
    report.append(f'  记录数：{len(buyers)}')
    buyer_names = [b.get('买手店名称') for b in buyers if b.get('买手店名称')]
    report.append(f'  买手店名称缺失：{len(buyers) - len(buyer_names)} 条')
    buyer_dups = [n for n, c in Counter(buyer_names).items() if c > 1]
    report.append(f'  买手店名称重复：{buyer_dups if buyer_dups else "无"}')

    # 6. 交叉检查
    sales_skus = set(s.get('SKU编码') for s in sales_records
                     if s.get('SKU编码') and not str(s.get('SKU编码')).startswith('R-'))
    inv_skus = set(i.get('SKU编码') for i in inv if i.get('SKU编码'))
    report.append('\n【交叉检查】')
    report.append(f'  销售SKU总数：{len(sales_skus)}')
    report.append(f'  有库存的SKU数：{len(sales_skus & inv_skus)}')
    report.append(f'  销售了但无库存的SKU：{list(sales_skus - inv_skus)[:10] if sales_skus - inv_skus else "无"}')
    report.append(f'  有库存但无销售的SKU数：{len(inv_skus - sales_skus)}')
    if inv_skus - sales_skus:
        report.append(f'  有库存但无销售的SKU(前10)：{list(inv_skus - sales_skus)[:10]}')

    report.append('\n' + '=' * 60)
    return '\n'.join(report)


if __name__ == '__main__':
    print(check_all())
