#!/usr/bin/env python3
"""生成测试销量数据批量写入飞书"""

import json, random, subprocess, time, urllib.request, urllib.error

BASE_TOKEN = 'Wa2lbJtJJaBnU8shuQicW6djnmd'
SALES_TABLE = 'tblx3gI1tDNp3j6W'
ANCHOR_ID = 'recvmeGXI2V33H'
BUYER_ID = 'recvmeGXIsWdPE'

PRODUCTS = [
    {'name': '收腰大衣', 'price': 1889, 'cost': 300, 'total': 6000},
    {'name': '宫廷衬衫', 'price': 889,  'cost': 180, 'total': 8000},
    {'name': '直筒西裤', 'price': 789,  'cost': 100, 'total': 10000},
]

# 渠道格式：飞书单选字段选项名
CHANNELS = {
    '自营_淘宝':   ('线上·自营·淘宝',   '淘宝',   0.50),
    '自营_抖音':   ('线上·自营·抖音',   '抖音',   0.17),
    '自营_小红书': ('线上·自营·小红书', '小红书', 0.08),
    '达播_抖音':   ('线上·达人直播·抖音', '抖音',  0.15),
    '买手店':     ('线上·买手店',       None,     0.10),
}

DATES_TS = {
    '2026-03': 1741977600000,
    '2026-04': 1744569600000,
    '2026-05': 1747248000000,
}

def gen_records():
    records = []
    for prod in PRODUCTS:
        for ch_key, (channel, platform, ratio) in CHANNELS.items():
            total_qty = int(round(prod['total'] * ratio))
            qty_per_month = max(1, total_qty // 3)
            rem = total_qty - qty_per_month * 3
            for i, (month_key, ts) in enumerate(DATES_TS.items()):
                qty = qty_per_month + (rem if i == 2 else 0)
                if qty <= 0:
                    continue
                sales_amt = int(qty * prod['price'] * random.uniform(0.93, 0.98))
                refund_qty = int(qty * random.uniform(0.02, 0.05))
                return_qty = int(qty * random.uniform(0.01, 0.03))
                refund_amt = int(refund_qty * prod['price'] * 0.9)
                return_amt = int(return_qty * prod['price'] * 0.9)

                fields = {
                    '款式名称': prod['name'],
                    '渠道': channel,
                    '日期': ts,
                    '销售额': sales_amt,
                    '销量件数': qty,
                    '仅退款件数': refund_qty,
                    '退货退款件数': return_qty,
                    '仅退款金额': refund_amt,
                    '退货退款金额': return_amt,
                    '平台扣点率': 0 if channel.startswith('线上·自营·淘宝') else (5 if platform in ('抖音','小红书') else 0),
                    '达人佣金率': 25 if '达人直播' in channel else 0,
                    '数据负责人': '小菜',
                }
                if platform:
                    fields['平台'] = platform
                if '达人直播' in channel:
                    fields['主播'] = [ANCHOR_ID]
                if '买手店' in channel:
                    fields['买手店'] = [BUYER_ID]
                    fields['结算比例(%)'] = 50
                    fields['买手店名称'] = 'B1OOK'

                records.append({'fields': fields})
    return records

def get_token():
    cli = '/Users/yangyang/.workbuddy/binaries/node/versions/22.12.0/bin/node'
    cli_path = '/Users/yangyang/.workbuddy/binaries/node/cli-connector-packages/bin/lark-cli'
    r = subprocess.run([cli, cli_path, 'auth', 'token', '--domain', 'base'],
                       capture_output=True, text=True, timeout=10)
    token = r.stdout.strip()
    if not token:
        raise Exception('No token. Run: lark-cli auth login --domain base')
    return token

def batch_create(token, records):
    url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{BASE_TOKEN}/tables/{SALES_TABLE}/records/batch_create'
    hdr = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    created = 0
    for i in range(0, len(records), 100):
        batch = [{'fields': r['fields']} for r in records[i:i+100]]
        data = json.dumps({'records': batch}).encode()
        req = urllib.request.Request(url, data=data, headers=hdr, method='POST')
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
            if result.get('code') == 0:
                n = len(result['data']['records'])
                created += n
                print(f'✅ Batch {i//100+1}: +{n} (total: {created})')
            else:
                print(f'❌ Batch {i//100+1} failed: {result}')
        except Exception as e:
            print(f'❌ Batch {i//100+1} error: {e}')
        time.sleep(0.3)
    return created

if __name__ == '__main__':
    print('Generating records...')
    recs = gen_records()
    print(f'{len(recs)} records to create')
    token = get_token()
    print('Token OK, writing...')
    n = batch_create(token, recs)
    print(f'\n🎉 Created {n} records!')
