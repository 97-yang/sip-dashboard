/**
 * 生成测试销量数据 JSON，然后通过 lark-cli 批量写入飞书
 */

const BASE_TOKEN = 'Wa2lbJtJJaBnU8shuQicW6djnmd';
const SALES_TABLE = 'tblx3gI1tDNp3j6W';
const ANCHOR_REC_ID = 'recvmeGXI2V33H';  // 李佳琦
const BUYER_REC_ID = 'recvmeGXIsWdPE';    // B1OOK

const PRODUCTS = [
  { name: '收腰大衣', price: 1889, cost: 300, totalQty: 6000 },
  { name: '宫廷衬衫', price: 889,  cost: 180, totalQty: 8000 },
  { name: '直筒西裤', price: 789,  cost: 100, totalQty: 10000 },
];

const months = ['2026-03', '2026-04', '2026-05'];

function generate() {
  const records = [];

  for (const prod of PRODUCTS) {
    // 自营淘宝 - 大头
    const taobaoQty = Math.round(prod.totalQty * 0.50);
    addRecords(records, prod, '自营', '淘宝', taobaoQty);

    // 自营抖音
    const douyinQty = Math.round(prod.totalQty * 0.17);
    addRecords(records, prod, '自营', '抖音', douyinQty);

    // 自营小红书
    const xhsQty = Math.round(prod.totalQty * 0.08);
    addRecords(records, prod, '自营', '小红书', xhsQty);

    // 达播 - 李佳琦
    const anchorQty = Math.round(prod.totalQty * 0.15);
    addRecords(records, prod, '达播', '抖音', anchorQty, ANCHOR_REC_ID, null);

    // 买手店 - B1OOK
    const buyerQty = prod.totalQty - taobaoQty - douyinQty - xhsQty - anchorQty;
    addRecords(records, prod, '买手店', null, buyerQty, null, BUYER_REC_ID);
  }

  return records;
}

function addRecords(records, prod, channel, platform, totalQty, anchorId, buyerId) {
  const qtyPerMonth = Math.max(1, Math.round(totalQty / months.length));
  let remainder = totalQty;

  for (let i = 0; i < months.length; i++) {
    const qty = (i === months.length - 1) ? remainder : qtyPerMonth;
    remainder -= qty;
    if (qty <= 0) continue;

    const date = months[i] + '-15';
    const avgPrice = prod.price;

    // 模拟真实波动
    const salesAmount = Math.round(qty * avgPrice * rand(0.93, 0.98));
    const refundQty = Math.round(qty * rand(0.02, 0.05));
    const returnQty = Math.round(qty * rand(0.01, 0.03));
    const netQty = Math.max(0, qty - refundQty - returnQty);
    const refundAmount = Math.round(refundQty * avgPrice * 0.9);
    const returnAmount = Math.round(returnQty * avgPrice * 0.9);
    const netSales = Math.max(0, salesAmount - refundAmount - returnAmount);

    // 平台扣点 5%
    const platformRate = (channel === '自营') ? 5 : 0;
    const platformFee = Math.round(netSales * platformRate / 100);

    // 佣金（达播 25%）
    const commissionRate = (channel === '达播') ? 25 : 0;
    const commissionAmount = Math.round((netSales - platformFee) * commissionRate / 100);

    // 买手店结算（50%）
    const settlementRate = (channel === '买手店') ? 50 : 0;

    // 单件到手均价 & 毛利
    let avgPricePerUnit = 0;
    if (channel === '买手店') {
      avgPricePerUnit = Math.round(avgPrice * settlementRate / 100);
    } else if (channel === '自营') {
      avgPricePerUnit = Math.round((netSales - platformFee) / Math.max(1, netQty));
    } else if (channel === '达播') {
      avgPricePerUnit = Math.round((netSales - platformFee - commissionAmount) / Math.max(1, netQty));
    }
    const grossProfitPerUnit = Math.max(0, avgPricePerUnit - prod.cost);
    const grossMargin = avgPricePerUnit > 0 ? Math.round(grossProfitPerUnit / avgPricePerUnit * 100) : 0;

    const fields = {
      '款式名称': prod.name,
      '渠道': channel,
      '日期': date,
      '销售额': salesAmount,
      '销量件数': qty,
      '仅退款件数': refundQty,
      '退货退款件数': returnQty,
      '仅退款金额': refundAmount,
      '退货退款金额': returnAmount,
      '净销量': netQty,
      '净销售额': netSales,
      '平台扣点率': platformRate,
      '平台扣点金额': platformFee,
      '达人佣金率': (channel === '达播') ? commissionRate : 0,
      '达人佣金金额': commissionAmount,
      '结算比例(%)': settlementRate,
      '单件到手均价': avgPricePerUnit,
      '产品成本/件': prod.cost,
      '单件毛利': grossProfitPerUnit,
      '毛利率(%)': grossMargin,
      '数据负责人': '测试数据',
    };

    if (platform) fields['平台'] = platform;
    if (anchorId) fields['主播'] = [anchorId];
    if (buyerId) fields['买手店'] = [buyerId];

    records.push({ fields });
  }
}

function rand(min, max) {
  return min + Math.random() * (max - min);
}

// 生成并保存 JSON
const records = generate();
console.log(`Generated ${records.length} records`);

// 分批：每批 500 条，通过 lark-cli 批量写入
const fs = require('fs');
const BATCH = 200; // 飞书 batch_create 限制 500，我们保守点

(async () => {
  const cli = '/Users/yangyang/.workbuddy/binaries/node/versions/22.12.0/bin/node';
  const cliPath = '/Users/yangyang/.workbuddy/binaries/node/cli-connector-packages/bin/lark-cli';

  let created = 0;
  for (let i = 0; i < records.length; i += BATCH) {
    const batch = records.slice(i, i + BATCH);
    const tmpFile = `/tmp/feishu-batch-${Math.floor(i / BATCH)}.json`;
    fs.writeFileSync(tmpFile, JSON.stringify({ records: batch.map(r => ({ fields: r.fields })) }));

    const cmd = `${cli} ${cliPath} api POST '/open-apis/bitable/v1/apps/${BASE_TOKEN}/tables/${SALES_TABLE}/records/batch_create' --data "$(cat ${tmpFile})"`;
    
    const { execSync } = require('child_process');
    try {
      const result = execSync(cmd, { encoding: 'utf8', timeout: 30000 });
      const json = JSON.parse(result);
      if (json.code === 0) {
        created += json.data.records.length;
        console.log(`✅ Batch ${Math.floor(i / BATCH) + 1}: +${json.data.records.length} (total: ${created})`);
      } else {
        console.error(`❌ Batch ${Math.floor(i / BATCH) + 1} failed:`, json.msg);
      }
    } catch (e) {
      console.error(`❌ Batch ${Math.floor(i / BATCH) + 1} error:`, e.message);
    }
    fs.unlinkSync(tmpFile);
  }

  console.log(`\n🎉 Total created: ${created} sales records`);
})();
