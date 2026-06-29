#!/usr/bin/env python3
# 重建 SIP CLASS 仪表盘 HTML（适配新 5 表结构）
import json, re

html_path = '/Users/yangyang/Desktop/SIP_CLASS_销售仪表盘_2026.html'
data_path = '/Users/yangyang/Desktop/sip-dashboard/data.json'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

with open(data_path, 'r', encoding='utf-8') as f:
    data_json = json.load(f)

# 保留 <style> 之前的内容（含 head 和 style）
style_end = html.find('</style>') + len('</style>')
head_part = html[:style_end]

# 保留 body 开始到 Chart.js script 之前的内容
body_start = html.find('<body>')
script_start = html.find('<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>')
body_part = html[body_start:script_start]

# ========== 修改 body_part ==========

# 筛选栏：年份 + 周期粒度 + 具体范围
filter_html = '''    <!-- FILTER BAR -->
    <div class="filter-bar">
      <div class="filter-section" style="flex-wrap:wrap;row-gap:8px">
        <span class="filter-label">时间</span>
        <select id="yearSel" class="fsel"></select>
        <div class="period-granularity" style="display:flex;gap:4px">
          <button class="fbtn active" data-filter="period" data-val="day">日</button>
          <button class="fbtn" data-filter="period" data-val="week">周</button>
          <button class="fbtn" data-filter="period" data-val="month">月</button>
          <button class="fbtn" data-filter="period" data-val="quarter">季</button>
          <button class="fbtn" data-filter="period" data-val="year">年</button>
        </div>
        <select id="monthSel" class="fsel" style="display:none">
          <option value="1">1月</option><option value="2">2月</option><option value="3">3月</option>
          <option value="4">4月</option><option value="5">5月</option><option value="6">6月</option>
          <option value="7">7月</option><option value="8">8月</option><option value="9">9月</option>
          <option value="10">10月</option><option value="11">11月</option><option value="12">12月</option>
        </select>
        <div id="quarterSel" class="dim-toggle" style="display:none">
          <button class="dim-btn" data-q="1">Q1</button>
          <button class="dim-btn" data-q="2">Q2</button>
          <button class="dim-btn" data-q="3">Q3</button>
          <button class="dim-btn" data-q="4">Q4</button>
        </div>
        <select id="weekSel" class="fsel" style="display:none"></select>
        <span id="weekRangeHint" class="sub-text" style="display:none;margin-left:6px;color:#6B6A65"></span>
        <input type="date" id="dayStart" class="fsel" style="display:none">
        <input type="date" id="dayEnd" class="fsel" style="display:none">
      </div>
      <div class="filter-sep"></div>
      <div class="filter-section">
        <span class="filter-label">渠道</span>
        <button class="fbtn active" data-filter="channel" data-val="all">全部</button>
        <button class="fbtn sub" data-filter="channel" data-val="自营">自营</button>
        <button class="fbtn sub" data-filter="channel" data-val="达播">达播</button>
        <button class="fbtn sub" data-filter="channel" data-val="买手店">买手店</button>
      </div>
      <div class="filter-sep" id="platformSep"></div>
      <div class="filter-section" id="platformFilter">
        <span class="filter-label">平台</span>
        <button class="fbtn sub active" data-filter="platform" data-val="all">全部</button>
        <button class="fbtn sub" data-filter="platform" data-val="淘宝">淘宝</button>
        <button class="fbtn sub" data-filter="platform" data-val="抖音">抖音</button>
        <button class="fbtn sub" data-filter="platform" data-val="小红书">小红书</button>
      </div>
      <div class="filter-sep" id="buyerTypeSep" style="display:none"></div>
      <div class="filter-section" id="buyerTypeFilter" style="display:none">
        <span class="filter-label">买手店类型</span>
        <button class="fbtn sub active" data-filter="buyerType" data-val="all">全部</button>
        <button class="fbtn sub" data-filter="buyerType" data-val="线上">线上</button>
        <button class="fbtn sub" data-filter="buyerType" data-val="线下">线下</button>
      </div>
    </div>
'''
body_part = re.sub(
    r'<!-- FILTER BAR -->.*?<!-- KPI -->',
    filter_html.strip() + '\n\n    <!-- KPI -->',
    body_part,
    flags=re.DOTALL
)

# 销量趋势增加总/净销量切换
body_part = body_part.replace(
    '<div class="card-head">\n          <div><div class="card-title">销量趋势</div><div class="card-sub">按月展示净销量 · 点选款式图例切换显示</div></div>\n          <span class="card-period" id="salesPeriod"></span>\n        </div>',
    '<div class="card-head">\n          <div><div class="card-title">销量趋势</div><div class="card-sub">点选款式图例切换显示</div></div>\n          <div style="display:flex;gap:8px;align-items:center">\n            <div class="dim-toggle" id="salesQtyToggle"><button class="dim-btn active" data-qty="net">净销量</button><button class="dim-btn" data-qty="gross">总销量</button></div>\n            <span class="card-period" id="salesPeriod"></span>\n          </div>\n        </div>'
)

# 退款监控增加切换按钮
body_part = body_part.replace(
    '<div class="card-head">\n          <div><div class="card-title">退款率趋势</div><div class="card-sub">仅退款率 vs 退货退款率（按月汇总）· 点选款式图例切换</div></div>\n          <span class="card-period" id="returnPeriod"></span>\n        </div>\n        <div class="legend-row" id="returnLegend"></div>\n        <div class="cw h200"><canvas id="returnChart"></canvas></div>',
    '<div class="card-head">\n          <div><div class="card-title">退款监控</div><div class="card-sub">退款金额/件数 + 总退款/仅退款/退货退款 + 周/月</div></div>\n          <span class="card-period" id="returnPeriod"></span>\n        </div>\n        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px">\n          <div class="dim-toggle" id="refundMetricToggle"><button class="dim-btn active" data-metric="amount">金额</button><button class="dim-btn" data-metric="qty">件数</button></div>\n          <div class="dim-toggle" id="refundTypeToggle"><button class="dim-btn active" data-rtype="total">总退款</button><button class="dim-btn" data-rtype="only">仅退款</button><button class="dim-btn" data-rtype="return">退货退款</button></div>\n          <div class="dim-toggle" id="refundTimeToggle"><button class="dim-btn active" data-tunit="week">周</button><button class="dim-btn" data-tunit="month">月</button></div>\n        </div>\n        <div class="legend-row" id="returnLegend"></div>\n        <div class="cw h200"><canvas id="returnChart"></canvas></div>'
)

# 热力图说明更新
body_part = body_part.replace(
    '<div class="card-sub">每个数字=日均销量(件/天) · 深色=卖得快需补货 · 浅色=卖得慢需促销</div>',
    '<div class="card-sub">每个数字=日均销量(件/天) · 按日维度统一 · 仅含自营数据 · 深色=卖得快需补货 · 浅色=卖得慢需促销</div>'
)

# 底部数据说明更新
body_part = body_part.replace(
    '<strong>五表结构：</strong>产品资料库 · 供应链 · 月度销量 · 主播资料库 · 买手店资料库<br>',
    '<strong>五表结构：</strong>产品资料库_新 · 库存情况_新 · 销售数据_新 · 主播资料库 · 买手店资料库<br>'
)
body_part = body_part.replace(
    '<strong>关键指标：</strong>净销售额(GSV)=销售额-仅退款金额-退货退款金额 · 单件到手均价按渠道区分 · 毛利率(%)=单件毛利÷单件到手均价×100<br>',
    '<strong>关键指标：</strong>净销量/退款件数由前端估算（退款金额÷实际成交单价）· 净销售额(GSV)=销售额-仅退款金额-退货退款金额 · 毛利率(%)=单件毛利÷到手价×100<br>'
)
body_part = body_part.replace(
    '<strong>买手店销售额：</strong>到手价=吊牌价×结算比例(%)×净销量（非GMV）<br>',
    '<strong>买手店销售额：</strong>录入为到手价，净销售额=到手价×净销量<br>'
)

# ========== 生成 JavaScript ==========
JS_CODE = '''
var FALLBACK_DATA = __FALLBACK_DATA__;

var DB = null;
var CHARTS = {};
var curPeriod = 'day';
var curYear = new Date().getFullYear();
var curQuarter = Math.floor(new Date().getMonth() / 3) + 1;
var curMonth = new Date().getMonth() + 1;
var curWeek = 1;
var curDateStart = '';
var curDateEnd = '';
var curPlatform = 'all';
var curBuyerType = 'all';
var profitDimension = 'channel';
var salesQtyType = 'net';
var refundMetric = 'amount';
var refundType = 'total';
var refundTimeUnit = 'week';
var selectedChannels = new Set(['自营', '达播', '买手店']);
var salesChartActiveStyles = null;
var DATA_VERSION = 2;

var STYLE_COLORS = ['#534AB7','#0F6E56','#D85A30','#993556','#185FA5','#E65100','#7B1FA2','#1565C0'];
var MONTH_LABELS = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'];
var QUARTER_MONTHS = { q1:[0,1,2], q2:[3,4,5], q3:[6,7,8], q4:[9,10,11] };
var CHANNEL_COLORS = { '自营': '#534AB7', '达播': '#0F6E56', '买手店': '#D85A30' };
var PLATFORM_COLORS = { '淘宝': '#FF6A00', '抖音': '#1A1A1A', '小红书': '#FE2C55', '线下': '#4A7C59' };

function num(v) {
  if (v === null || v === undefined || v === '') return 0;
  if (Array.isArray(v)) { return num(v.length > 0 ? v[0] : 0); }
  if (typeof v === 'object' && v !== null) {
    if (v.text !== undefined) return num(v.text);
    if (v.value !== undefined) return num(v.value);
    return 0;
  }
  if (typeof v === 'number') return v;
  var n = parseFloat(v);
  return isNaN(n) ? 0 : n;
}

function firstText(v) {
  if (!v) return null;
  if (typeof v === 'string') return v;
  if (Array.isArray(v)) return v.length > 0 ? firstText(v[0]) : null;
  if (typeof v === 'object') return v.text || v.name || null;
  return String(v);
}

function fmtMoney(v) {
  if (Math.abs(v) >= 10000) return '¥' + (v / 10000).toFixed(1) + '万';
  return '¥' + v.toLocaleString('zh-CN');
}

function getStyleColor(name, idx) {
  return STYLE_COLORS[idx % STYLE_COLORS.length];
}

function getChannelShort(channel) {
  if (!channel) return '未知';
  if (channel.indexOf('自营') >= 0) return '自营';
  if (channel.indexOf('达播') >= 0) return '达播';
  if (channel.indexOf('买手店') >= 0) return '买手店';
  return channel;
}

function getPlatformFromChannel(channel) {
  if (!channel) return null;
  if (channel.indexOf('淘宝') >= 0) return '淘宝';
  if (channel.indexOf('抖音') >= 0) return '抖音';
  if (channel.indexOf('小红书') >= 0) return '小红书';
  return null;
}

function getBuyerTypeFromChannel(channel) {
  if (!channel) return null;
  if (channel.indexOf('线上') >= 0) return '线上';
  if (channel.indexOf('线下') >= 0) return '线下';
  return null;
}

function parseDate(d) {
  if (!d) return null;
  if (typeof d === 'string') {
    var parts = d.match(/^(\\d{4})[\\/-](\\d{1,2})[\\/-](\\d{1,2})/);
    if (parts) return new Date(parseInt(parts[1]), parseInt(parts[2]) - 1, parseInt(parts[3]));
  }
  if (d instanceof Date) return d;
  return null;
}

function getMonthFromDate(d) {
  var dt = parseDate(d);
  return dt ? dt.getMonth() : -1;
}

function getYearFromDate(d) {
  var dt = parseDate(d);
  return dt ? dt.getFullYear() : null;
}

function getWeekKey(d) {
  var dt = parseDate(d);
  if (!dt) return null;
  var year = dt.getFullYear();
  var start = new Date(year, 0, 1);
  var diff = dt - start + ((start.getDay() + 6) % 7) * 86400000;
  var week = Math.floor(diff / 604800000) + 1;
  return year + '-W' + String(week).padStart(2, '0');
}

function formatDate(d) {
  if (!d) return '';
  var y = d.getFullYear();
  var m = String(d.getMonth() + 1).padStart(2, '0');
  var day = String(d.getDate()).padStart(2, '0');
  return y + '-' + m + '-' + day;
}

function getWeekDateRange(year, week) {
  var jan1 = new Date(year, 0, 1);
  var jan1Day = (jan1.getDay() + 6) % 7;
  var monday = new Date(year, 0, 1 + (week - 1) * 7 - jan1Day);
  var sunday = new Date(monday.getTime() + 6 * 86400000);
  return { start: monday, end: sunday };
}

function getMonthDateRange(year, month) {
  var start = new Date(year, month - 1, 1);
  var end = new Date(year, month, 0);
  return { start: start, end: end };
}

function getQuarterDateRange(year, quarter) {
  var startMonth = (quarter - 1) * 3;
  var start = new Date(year, startMonth, 1);
  var end = new Date(year, startMonth + 3, 0);
  return { start: start, end: end };
}

function getYearDateRange(year) {
  return { start: new Date(year, 0, 1), end: new Date(year, 11, 31) };
}

function getCurrentRange() {
  var year = parseInt(document.getElementById('yearSel').value);
  if (curPeriod === 'day') {
    var start = parseDate(document.getElementById('dayStart').value);
    var end = parseDate(document.getElementById('dayEnd').value);
    if (!start || !end) {
      var today = new Date();
      end = today;
      start = new Date(today.getTime() - 29 * 86400000);
    }
    return { start: start, end: end };
  }
  if (curPeriod === 'week') {
    var week = parseInt(document.getElementById('weekSel').value);
    return getWeekDateRange(year, week);
  }
  if (curPeriod === 'month') {
    var month = parseInt(document.getElementById('monthSel').value);
    return getMonthDateRange(year, month);
  }
  if (curPeriod === 'quarter') {
    return getQuarterDateRange(year, curQuarter);
  }
  return getYearDateRange(year);
}

function getPrevRange() {
  var range = getCurrentRange();
  var start = range.start, end = range.end;
  if (curPeriod === 'year') return getYearDateRange(start.getFullYear() - 1);
  if (curPeriod === 'quarter') {
    var y = parseInt(document.getElementById('yearSel').value);
    if (curQuarter === 1) return getQuarterDateRange(y - 1, 4);
    return getQuarterDateRange(y, curQuarter - 1);
  }
  if (curPeriod === 'month') {
    var m = parseInt(document.getElementById('monthSel').value), y = parseInt(document.getElementById('yearSel').value);
    if (m === 1) return getMonthDateRange(y - 1, 12);
    return getMonthDateRange(y, m - 1);
  }
  if (curPeriod === 'week') {
    var w = parseInt(document.getElementById('weekSel').value), y = parseInt(document.getElementById('yearSel').value);
    if (w === 1) return getWeekDateRange(y - 1, 52);
    return getWeekDateRange(y, w - 1);
  }
  var diff = end.getTime() - start.getTime();
  var prevEnd = new Date(start.getTime() - 86400000);
  var prevStart = new Date(prevEnd.getTime() - diff);
  return { start: prevStart, end: prevEnd };
}

function inDateRange(d, range) {
  var dt = parseDate(d);
  if (!dt || !range || !range.start || !range.end) return false;
  var s = new Date(range.start.getFullYear(), range.start.getMonth(), range.start.getDate());
  var e = new Date(range.end.getFullYear(), range.end.getMonth(), range.end.getDate());
  return dt >= s && dt <= e;
}

function getActiveMonths() {
  var range = getCurrentRange();
  if (!range.start || !range.end) return [0,1,2,3,4,5,6,7,8,9,10,11];
  var months = [];
  for (var y = range.start.getFullYear(); y <= range.end.getFullYear(); y++) {
    var mStart = (y === range.start.getFullYear()) ? range.start.getMonth() : 0;
    var mEnd = (y === range.end.getFullYear()) ? range.end.getMonth() : 11;
    for (var m = mStart; m <= mEnd; m++) {
      var mi = m;
      if (months.indexOf(mi) === -1) months.push(mi);
    }
  }
  return months.sort(function(a,b){return a-b;});
}

function getStockStatus(turnover, stockoutDays, stock) {
  if (stock === 0 || turnover > 60 || stockoutDays > 3) return { label: '🔴 短缺', cls: 'shortage' };
  if (turnover >= 30 || stockoutDays >= 1) return { label: '🟡 预警', cls: 'warning' };
  return { label: '🟢 健康', cls: 'healthy' };
}

function salesSpeedColor(v) {
  if (v <= 0) return '#F1EFE8';
  if (v <= 5) return '#EEEDFE';
  if (v <= 15) return '#CECBF6';
  if (v <= 30) return '#AFA9EC';
  if (v <= 50) return '#9E97E8';
  if (v <= 80) return '#7F77DD';
  return '#534AB7';
}

function getPeriodText() {
  var year = document.getElementById('yearSel').value;
  if (curPeriod === 'year') return year + '全年';
  if (curPeriod === 'quarter') return year + '年 Q' + curQuarter;
  if (curPeriod === 'month') return year + '年' + document.getElementById('monthSel').value + '月';
  if (curPeriod === 'week') {
    var week = document.getElementById('weekSel').value;
    return year + '年第' + week + '周';
  }
  if (curPeriod === 'day') {
    var start = document.getElementById('dayStart').value;
    var end = document.getElementById('dayEnd').value;
    return start + ' 至 ' + end;
  }
  return year + '年';
}

async function loadData() {
  var loadingBox = document.getElementById('loadingBox');
  var emptyBox = document.getElementById('emptyBox');
  var errorBox = document.getElementById('errorBox');
  var dashboardContent = document.getElementById('dashboardContent');
  var refreshBtn = document.getElementById('refreshBtn');
  var dataStatus = document.getElementById('dataStatus');

  loadingBox.style.display = 'flex';
  emptyBox.style.display = 'none';
  errorBox.style.display = 'none';
  dashboardContent.style.display = 'none';
  refreshBtn.style.display = 'none';
  dataStatus.textContent = '正在加载数据...';

  var json = null;
  var dataSource = '';
  try {
    var resp;
    var paths = ['sip-dashboard/data.json', 'data.json'];
    for (var i = 0; i < paths.length; i++) {
      try { resp = await fetch(paths[i] + '?t=' + Date.now()); if (resp.ok) break; } catch(e) { continue; }
    }
    if (resp && resp.ok) { json = await resp.json(); dataSource = 'live'; }
  } catch(e) {}

  if (!json && typeof FALLBACK_DATA !== 'undefined') {
    json = FALLBACK_DATA;
    dataSource = 'embedded';
  }

  try {
    if (!json) throw new Error('找不到 data.json 文件');
    if (!json.tables) throw new Error('data.json 格式无效');
    DB = processRawData(json);
    var fetchedAt = json.fetchedAt ? new Date(json.fetchedAt).toLocaleString('zh-CN') : '未知时间';
    dataStatus.textContent = '数据更新：' + fetchedAt + (dataSource === 'embedded' ? '（内嵌数据）' : '');
    refreshBtn.style.display = 'inline-block';

    var totalRecords = 0;
    for (var k in DB) { if (Array.isArray(DB[k])) totalRecords += DB[k].length; }
    if (totalRecords === 0) {
      loadingBox.style.display = 'none';
      emptyBox.style.display = 'flex';
      return;
    }

    loadingBox.style.display = 'none';
    dashboardContent.style.display = 'block';
    initFilters(json);
    renderAll();
  } catch(e) {
    loadingBox.style.display = 'none';
    errorBox.style.display = 'flex';
    document.getElementById('errorMsg').textContent = e.message;
    refreshBtn.style.display = 'inline-block';
    dataStatus.textContent = '数据加载失败';
  }
}

function processRawData(json) {
  var tables = json.tables;
  var db = {
    products: tables.products ? (tables.products.records || []) : [],
    sales: tables.sales ? (tables.sales.records || []) : [],
    inventory: tables.inventory ? (tables.inventory.records || []) : [],
    anchors: tables.anchors ? (tables.anchors.records || []) : [],
    buyers: tables.buyers ? (tables.buyers.records || []) : [],
    productMap: {},
    productMapByStyleCode: {},
    inventoryMap: {},
    anchorMap: {},
    buyerMap: {}
  };

  db.products.forEach(function(p) {
    var sku = p['SKU编码'];
    var styleCode = p['款式编码'];
    if (sku) db.productMap[sku] = p;
    if (styleCode) db.productMapByStyleCode[styleCode] = p;
  });

  db.inventory.forEach(function(inv) {
    var sku = inv['SKU编码'];
    if (sku) db.inventoryMap[sku] = inv;
  });

  db.anchors.forEach(function(a) {
    var name = a['直播间名称'];
    if (name) db.anchorMap[name] = a;
  });

  db.buyers.forEach(function(b) {
    var name = b['买手店名称'];
    if (name) db.buyerMap[name] = b;
  });

  // 分离销售记录与退款记录
  var salesRecords = [];
  var refundRecords = [];
  db.sales.forEach(function(s) {
    var sku = s['SKU编码'];
    var refundWeek = s['退款周次'];
    if ((sku && sku.startsWith('R-')) || refundWeek) {
      refundRecords.push(s);
      return;
    }
    salesRecords.push(s);
  });
  db.sales = salesRecords;
  db.refunds = refundRecords;

  db.sales.forEach(function(s) {
    var channel = s['渠道'];
    s._channel = getChannelShort(channel);
    s._platform = getPlatformFromChannel(channel);
    s._buyerType = getBuyerTypeFromChannel(channel);

    var sku = s['SKU编码'];
    var styleCode = s['🔗 款式编码'];
    var prod = null;
    if (sku) prod = db.productMap[sku];
    if (!prod && styleCode) prod = db.productMapByStyleCode[styleCode];
    s._product = prod;
    s['款式名称'] = prod ? prod['款式名称'] : (s['🔗 款式名称'] || sku || '未知');
    s['款式编码'] = prod ? prod['款式编码'] : (styleCode || '');
    s['吊牌价'] = prod ? num(prod['吊牌价']) : 0;
    if (!s['🔗 产品成本/件'] && prod) s['🔗 产品成本/件'] = num(prod['成本价/件']);

    var gm = num(s['销售额']);
    var qty = num(s['销量件数']);
    var refundTotal = num(s['退款总金额（款式级）']);
    var refundReturn = num(s['退货退款金额（款式级）']);
    var refundOnly = num(s['仅退款金额（款式级）']);
    var feeRate = num(s['平台扣点率(%)']);
    var commRate = num(s['达人佣金率(%)']);
    var settleRate = num(s['结算比例(%)']);
    var cost = num(s['🔗 产品成本/件']);

    var gsv = gm - refundOnly - refundReturn;
    var avgPrice = qty > 0 ? gm / qty : 0;
    var estRefundOnlyQty = avgPrice > 0 ? refundOnly / avgPrice : 0;
    var estRefundReturnQty = avgPrice > 0 ? refundReturn / avgPrice : 0;
    var netQty = qty - estRefundOnlyQty - estRefundReturnQty;

    var platFee = gsv * feeRate / 100;
    var commFee = s._channel === '达播' ? gsv * commRate / 100 : 0;

    var avgReceive = 0;
    if (s._channel === '买手店') {
      var tagPrice = s['吊牌价'];
      avgReceive = tagPrice > 0 && settleRate > 0 ? tagPrice * settleRate / 100 : 0;
    } else if (netQty > 0) {
      avgReceive = (gsv - platFee - commFee) / netQty;
    }

    var unitGP = avgReceive > 0 && cost > 0 ? avgReceive - cost : 0;
    var marginRate = avgReceive > 0 ? unitGP / avgReceive * 100 : 0;

    s._gmv = gm;
    s._gsv = gsv;
    s._qty = qty;
    s._netQty = netQty;
    s._refundTotal = refundTotal;
    s._refundReturn = refundReturn;
    s._refundOnly = refundOnly;
    s._platFee = platFee;
    s._commFee = commFee;
    s._avgReceive = avgReceive;
    s._unitGP = unitGP;
    s._marginRate = marginRate;
    s._cost = cost;
  });

  return db;
}

function getFilteredSales() {
  if (!DB) return [];
  var range = getCurrentRange();
  return DB.sales.filter(function(s) {
    if (!inDateRange(s['销售日期'], range)) return false;
    if (selectedChannels.size < 3 && !selectedChannels.has(s._channel)) return false;
    if (curPlatform !== 'all' && s._platform !== curPlatform) return false;
    if (curBuyerType !== 'all' && s._channel === '买手店' && s._buyerType !== curBuyerType) return false;
    return true;
  });
}

function getFilteredRefunds() {
  if (!DB) return [];
  var range = getCurrentRange();
  return DB.refunds.filter(function(r) {
    return inDateRange(r['销售日期'], range);
  });
}

function getPrevPeriodSales() {
  if (!DB) return [];
  var range = getPrevRange();
  return DB.sales.filter(function(s) {
    if (!inDateRange(s['销售日期'], range)) return false;
    if (selectedChannels.size < 3 && !selectedChannels.has(s._channel)) return false;
    if (curPlatform !== 'all' && s._platform !== curPlatform) return false;
    if (curBuyerType !== 'all' && s._channel === '买手店' && s._buyerType !== curBuyerType) return false;
    return true;
  });
}

function updateChannelButtonStates() {
  var allBtn = document.querySelector('.fbtn[data-filter="channel"][data-val="all"]');
  if (selectedChannels.size === 3) allBtn.classList.add('active'); else allBtn.classList.remove('active');
  document.querySelectorAll('.fbtn[data-filter="channel"]').forEach(function(btn) {
    if (btn.dataset.val === 'all') return;
    if (selectedChannels.has(btn.dataset.val)) btn.classList.add('active'); else btn.classList.remove('active');
  });
}

function updatePlatformAndBuyerTypeVisibility() {
  var hasSelf = selectedChannels.has('自营');
  var hasAnchor = selectedChannels.has('达播');
  var hasBuyer = selectedChannels.has('买手店');
  document.getElementById('platformFilter').style.display = (hasSelf || hasAnchor) ? 'flex' : 'none';
  document.getElementById('platformSep').style.display = (hasSelf || hasAnchor) ? 'block' : 'none';
  document.getElementById('buyerTypeFilter').style.display = hasBuyer ? 'flex' : 'none';
  document.getElementById('buyerTypeSep').style.display = (hasBuyer && (hasSelf || hasAnchor)) ? 'block' : 'none';
}

function updatePeriodLabel() {
  document.getElementById('periodLabel').textContent = getPeriodText();
}

function updateAllPeriodBadges() {
  var text = getPeriodText();
  ['salesPeriod','modeProfitPeriod','channelProfitPeriod','channelPerfPeriod','returnPeriod','heatmapPeriod','decisionPeriod','anchorPeriod','buyerPeriod'].forEach(function(id) {
    var el = document.getElementById(id);
    if (el) el.textContent = text;
  });
}

function initFilters(json) {
  var years = new Set();
  DB.sales.forEach(function(s) { var y = getYearFromDate(s['销售日期']); if (y) years.add(y); });
  DB.refunds.forEach(function(r) { var y = getYearFromDate(r['销售日期']); if (y) years.add(y); });
  var yearSel = document.getElementById('yearSel');
  yearSel.innerHTML = '';
  var yearArr = Array.from(years).sort();
  if (yearArr.length === 0) yearArr = [new Date().getFullYear()];
  yearArr.forEach(function(y) { var opt = document.createElement('option'); opt.value = y; opt.textContent = y + '年'; yearSel.appendChild(opt); });
  yearSel.value = yearArr[yearArr.length - 1];
  curYear = parseInt(yearSel.value);

  // 默认最近 30 天（日视图）
  var today = new Date();
  var start30 = new Date(today.getTime() - 29 * 86400000);
  document.getElementById('dayStart').value = formatDate(start30);
  document.getElementById('dayEnd').value = formatDate(today);
  curDateStart = document.getElementById('dayStart').value;
  curDateEnd = document.getElementById('dayEnd').value;

  // 初始化季度按钮状态
  document.querySelectorAll('#quarterSel .dim-btn').forEach(function(btn) {
    if (parseInt(btn.dataset.q) === curQuarter) btn.classList.add('active');
    else btn.classList.remove('active');
  });

  // 初始化周下拉选项
  var weekSel = document.getElementById('weekSel');
  weekSel.innerHTML = '';
  for (var w = 1; w <= 52; w++) {
    var opt = document.createElement('option');
    opt.value = w;
    var wr = getWeekDateRange(curYear, w);
    opt.textContent = '第' + w + '周';
    weekSel.appendChild(opt);
  }
  // 默认选中当前周
  var currentWeek = 1;
  var now = new Date();
  var tmpKey = getWeekKey(now);
  if (tmpKey) { var parts = tmpKey.split('-W'); if (parseInt(parts[0]) === curYear) currentWeek = parseInt(parts[1]); }
  curWeek = currentWeek;
  weekSel.value = currentWeek;
  updateWeekRangeHint();

  // 月份默认当前月
  document.getElementById('monthSel').value = today.getMonth() + 1;
  curMonth = today.getMonth() + 1;

  // 事件绑定
  yearSel.addEventListener('change', function() { curYear = parseInt(this.value); rebuildWeekOptions(); renderAll(); });
  document.getElementById('monthSel').addEventListener('change', function() { curMonth = parseInt(this.value); renderAll(); });
  document.querySelectorAll('#quarterSel .dim-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      document.querySelectorAll('#quarterSel .dim-btn').forEach(function(b) { b.classList.remove('active'); });
      btn.classList.add('active');
      curQuarter = parseInt(btn.dataset.q);
      renderAll();
    });
  });
  document.getElementById('weekSel').addEventListener('change', function() { curWeek = parseInt(this.value); updateWeekRangeHint(); renderAll(); });
  document.getElementById('dayStart').addEventListener('change', function() { curDateStart = this.value; renderAll(); });
  document.getElementById('dayEnd').addEventListener('change', function() { curDateEnd = this.value; renderAll(); });

  updateRangeSelectorVisibility();
  updatePlatformAndBuyerTypeVisibility();
  updatePeriodLabel();
  updateAllPeriodBadges();
}

function rebuildWeekOptions() {
  var weekSel = document.getElementById('weekSel');
  var oldVal = parseInt(weekSel.value);
  weekSel.innerHTML = '';
  for (var w = 1; w <= 52; w++) {
    var opt = document.createElement('option');
    opt.value = w;
    opt.textContent = '第' + w + '周';
    weekSel.appendChild(opt);
  }
  weekSel.value = oldVal || 1;
  updateWeekRangeHint();
}

function updateWeekRangeHint() {
  var weekSel = document.getElementById('weekSel');
  var hint = document.getElementById('weekRangeHint');
  var w = parseInt(weekSel.value);
  var year = parseInt(document.getElementById('yearSel').value);
  var r = getWeekDateRange(year, w);
  var fmt = function(d) { return String(d.getMonth() + 1).padStart(2, '0') + '/' + String(d.getDate()).padStart(2, '0'); };
  hint.textContent = fmt(r.start) + ' - ' + fmt(r.end);
  hint.style.display = curPeriod === 'week' ? 'inline' : 'none';
}

function updateRangeSelectorVisibility() {
  var isYear = curPeriod === 'year';
  var isQuarter = curPeriod === 'quarter';
  var isMonth = curPeriod === 'month';
  var isWeek = curPeriod === 'week';
  var isDay = curPeriod === 'day';
  document.getElementById('monthSel').style.display = isMonth ? 'inline-block' : 'none';
  document.getElementById('quarterSel').style.display = isQuarter ? 'flex' : 'none';
  document.getElementById('weekSel').style.display = isWeek ? 'inline-block' : 'none';
  document.getElementById('weekRangeHint').style.display = isWeek ? 'inline' : 'none';
  document.getElementById('dayStart').style.display = isDay ? 'inline-block' : 'none';
  document.getElementById('dayEnd').style.display = isDay ? 'inline-block' : 'none';
}

function calcKPISummary(sales) {
  var totalGMV = 0, totalGSV = 0, totalQty = 0, totalNetQty = 0, totalGP = 0;
  var totalRefundOnly = 0, totalRefundReturn = 0;
  sales.forEach(function(s) {
    totalGMV += s._gmv;
    totalGSV += s._gsv;
    totalQty += s._qty;
    totalNetQty += s._netQty;
    totalGP += s._netQty * s._unitGP;
    totalRefundOnly += s._refundOnly;
    totalRefundReturn += s._refundReturn;
  });

  var avgPrice = totalQty > 0 ? totalGMV / totalQty : 0;
  var estRefundOnlyQty = avgPrice > 0 ? totalRefundOnly / avgPrice : 0;
  var estRefundReturnQty = avgPrice > 0 ? totalRefundReturn / avgPrice : 0;
  var estRefundQty = estRefundOnlyQty + estRefundReturnQty;

  var marginRate = totalGSV > 0 ? (totalGP / totalGSV * 100) : 0;
  var refundRate = totalQty > 0 ? (estRefundQty / totalQty * 100) : 0;

  var range = getCurrentRange();
  var daysInRange = (range.start && range.end) ? Math.max(1, Math.round((range.end.getTime() - range.start.getTime()) / 86400000) + 1) : 30;

  var avgTurnover = 0;
  if (DB.inventory.length > 0 && totalNetQty > 0) {
    var totalStock = 0;
    DB.inventory.forEach(function(item) { totalStock += num(item['当前库存']); });
    var dailyAvg = totalNetQty / daysInRange;
    avgTurnover = dailyAvg > 0 ? Math.round(totalStock / dailyAvg) : 0;
  }

  var totalStockoutLoss = 0;
  DB.inventory.forEach(function(item) {
    var sku = item['SKU编码'];
    var prod = sku ? DB.productMap[sku] : null;
    var styleName = prod ? prod['款式名称'] : (item['🔗 款式名称'] || '未知');
    var stockoutDays = num(item['断货天数']);
    if (stockoutDays > 0) {
      var styleQty = 0, styleGP = 0, gpCount = 0;
      sales.forEach(function(s) {
        if (s['SKU编码'] === sku || s['款式名称'] === styleName) {
          styleQty += s._netQty;
          styleGP += s._unitGP;
          gpCount++;
        }
      });
      var dailyStyleQty = styleQty / daysInRange;
      var avgUnitGP = gpCount > 0 ? styleGP / gpCount : 0;
      totalStockoutLoss += stockoutDays * dailyStyleQty * avgUnitGP;
    }
  });

  return { totalGMV: totalGMV, totalGSV: totalGSV, totalQty: totalQty, totalNetQty: totalNetQty,
    marginRate: marginRate, avgTurnover: avgTurnover, totalStockoutLoss: totalStockoutLoss, refundRate: refundRate };
}

function renderKPI() {
  try {
    var sales = getFilteredSales();
    var cur = calcKPISummary(sales);
    var prevSales = getPrevPeriodSales();
    var prev = prevSales.length > 0 ? calcKPISummary(prevSales) : null;

    var kpis = [
      { label: '总销量', value: cur.totalQty.toLocaleString('zh-CN'), unit: '件', curV: cur.totalQty, prevV: prev ? prev.totalQty : null, pct: true },
      { label: '净销量', value: Math.round(cur.totalNetQty).toLocaleString('zh-CN'), unit: '件', curV: cur.totalNetQty, prevV: prev ? prev.totalNetQty : null, pct: true },
      { label: '销售额', value: (cur.totalGMV / 10000).toFixed(1), unit: '万元', curV: cur.totalGMV, prevV: prev ? prev.totalGMV : null, pct: true },
      { label: '净销售额', value: (cur.totalGSV / 10000).toFixed(1), unit: '万元', curV: cur.totalGSV, prevV: prev ? prev.totalGSV : null, pct: true },
      { label: '毛利率(%)', value: cur.marginRate.toFixed(1), unit: '%', curV: cur.marginRate, prevV: prev ? prev.marginRate : null, pct: false, isRate: true },
      { label: '库存周转天数', value: cur.avgTurnover || '-', unit: '天', curV: cur.avgTurnover, prevV: prev ? prev.avgTurnover : null, pct: false, inverse: true },
      { label: '缺货损失', value: cur.totalStockoutLoss > 0 ? (cur.totalStockoutLoss / 10000).toFixed(1) : '-', unit: '万元', curV: cur.totalStockoutLoss, prevV: prev ? prev.totalStockoutLoss : null, pct: true, inverse: true },
      { label: '退款率', value: cur.refundRate.toFixed(1), unit: '%', curV: cur.refundRate, prevV: prev ? prev.refundRate : null, pct: false, isRate: true, inverse: true }
    ];

    var html = '';
    kpis.forEach(function(k) {
      html += '<div class="kpi-card">';
      html += '<div class="kpi-label">' + k.label + '</div>';
      html += '<div class="kpi-value">' + k.value + '<span class="u">' + k.unit + '</span></div>';
      var momHtml = '';
      if (k.prevV !== null && k.prevV > 0) {
        if (k.isRate) {
          var diff = k.curV - k.prevV;
          var sign = diff > 0 ? '+' : '';
          var cls = diff === 0 ? 'flat' : (k.inverse ? (diff > 0 ? 'down' : 'up') : (diff > 0 ? 'up' : 'down'));
          momHtml = '<div class="kpi-mom ' + cls + '">' + sign + diff.toFixed(1) + 'pp</div>';
        } else {
          var pctChange = (k.curV - k.prevV) / k.prevV * 100;
          var sign2 = pctChange > 0 ? '+' : '';
          var cls2 = pctChange === 0 ? 'flat' : (k.inverse ? (pctChange > 0 ? 'down' : 'up') : (pctChange > 0 ? 'up' : 'down'));
          momHtml = '<div class="kpi-mom ' + cls2 + '">' + sign2 + pctChange.toFixed(1) + '%</div>';
        }
      } else if (k.prevV !== null) {
        momHtml = '<div class="kpi-mom flat">-</div>';
      }
      html += momHtml;
      html += '</div>';
    });
    document.getElementById('kpiRow').innerHTML = html;
  } catch(e) { console.error('renderKPI error:', e); }
}

function getSalesTimeBuckets() {
  var range = getCurrentRange();
  if (!range.start || !range.end) {
    return { labels: MONTH_LABELS, keys: ['01','02','03','04','05','06','07','08','09','10','11','12'], keyFn: function(d) { var dt = parseDate(d); return dt ? String(dt.getMonth() + 1).padStart(2, '0') : null; } };
  }

  if (curPeriod === 'year') {
    var y = range.start.getFullYear();
    return { labels: [y + '年'], keys: [String(y)], keyFn: function(d) { var dt = parseDate(d); return dt ? String(dt.getFullYear()) : null; } };
  }

  if (curPeriod === 'quarter') {
    var labels = [], keys = [];
    for (var y = range.start.getFullYear(); y <= range.end.getFullYear(); y++) {
      var qStart = (y === range.start.getFullYear()) ? Math.floor(range.start.getMonth() / 3) + 1 : 1;
      var qEnd = (y === range.end.getFullYear()) ? Math.floor(range.end.getMonth() / 3) + 1 : 4;
      for (var q = qStart; q <= qEnd; q++) {
        labels.push(y + ' Q' + q);
        keys.push(y + '-Q' + q);
      }
    }
    return { labels: labels, keys: keys, keyFn: function(d) { var dt = parseDate(d); if (!dt) return null; return dt.getFullYear() + '-Q' + (Math.floor(dt.getMonth() / 3) + 1); } };
  }

  if (curPeriod === 'month') {
    var labels = [], keys = [];
    for (var y = range.start.getFullYear(); y <= range.end.getFullYear(); y++) {
      var mStart = (y === range.start.getFullYear()) ? range.start.getMonth() : 0;
      var mEnd = (y === range.end.getFullYear()) ? range.end.getMonth() : 11;
      for (var m = mStart; m <= mEnd; m++) {
        labels.push(MONTH_LABELS[m]);
        keys.push(y + '-' + String(m + 1).padStart(2, '0'));
      }
    }
    return { labels: labels, keys: keys, keyFn: function(d) { var dt = parseDate(d); if (!dt) return null; return dt.getFullYear() + '-' + String(dt.getMonth() + 1).padStart(2, '0'); } };
  }

  if (curPeriod === 'week') {
    var labels = [], keys = [];
    var d = new Date(range.start);
    while (d <= range.end) {
      var key = getWeekKey(d);
      if (key && keys.indexOf(key) === -1) {
        keys.push(key);
        labels.push(key.replace('-W', '周'));
      }
      d.setDate(d.getDate() + 1);
    }
    return { labels: labels, keys: keys, keyFn: function(d) { return getWeekKey(d); } };
  }

  // day
  var labels = [], keys = [];
  var d = new Date(range.start);
  while (d <= range.end) {
    var key = formatDate(d);
    keys.push(key);
    labels.push((d.getMonth() + 1) + '/' + d.getDate());
    d.setDate(d.getDate() + 1);
  }
  return { labels: labels, keys: keys, keyFn: function(d) { return formatDate(parseDate(d)); } };
}

function renderSalesChart() {
  try {
    var sales = getFilteredSales();
    var cfg = getSalesTimeBuckets();
    var labels = cfg.labels;
    var qtyKey = salesQtyType === 'gross' ? '_qty' : '_netQty';

    var styleQty = {};
    sales.forEach(function(s) {
      var styleName = s['款式名称'] || '未知';
      var key = cfg.keyFn(s['销售日期']);
      var qty = s[qtyKey];
      if (!key) return;
      if (!styleQty[styleName]) styleQty[styleName] = {};
      if (!styleQty[styleName][key]) styleQty[styleName][key] = 0;
      styleQty[styleName][key] += qty;
    });

    var styleNames = Object.keys(styleQty);
    if (!salesChartActiveStyles) salesChartActiveStyles = new Set(styleNames);

    var datasets = styleNames.map(function(name, i) {
      var color = getStyleColor(name, i);
      var data = cfg.keys.map(function(k) { return (styleQty[name] ? (styleQty[name][k] || 0) : 0); });
      return { label: name, data: data, borderColor: color, backgroundColor: color + '15', borderWidth: 2, pointRadius: 3, pointHoverRadius: 6, pointBackgroundColor: color, tension: 0.35, fill: false, hidden: !salesChartActiveStyles.has(name) };
    });

    var legendEl = document.getElementById('salesLegend');
    legendEl.innerHTML = '';
    styleNames.forEach(function(name, i) {
      var color = getStyleColor(name, i);
      var chip = document.createElement('button');
      chip.className = 'legend-chip ' + (salesChartActiveStyles.has(name) ? 'active' : 'inactive');
      chip.style.color = color; chip.style.borderColor = color;
      chip.innerHTML = '<span class="legend-dot" style="background:' + color + '"></span>' + name;
      chip.onclick = function() { if (salesChartActiveStyles.has(name)) { if (salesChartActiveStyles.size <= 1) return; salesChartActiveStyles.delete(name); } else { salesChartActiveStyles.add(name); } renderSalesChart(); };
      legendEl.appendChild(chip);
    });

    if (CHARTS.sales) CHARTS.sales.destroy();
    CHARTS.sales = new Chart(document.getElementById('salesChart'), {
      type: 'line',
      data: { labels: labels, datasets: datasets },
      options: { responsive: true, maintainAspectRatio: false, interaction: { mode: 'index', intersect: false }, plugins: { legend: { display: false }, tooltip: { backgroundColor: '#1A1A18', titleFont:{size:11}, bodyFont:{size:11}, padding:10, cornerRadius:8, callbacks: { label: function(ctx) { return ctx.dataset.label + '：' + Math.round(ctx.parsed.y) + ' 件'; } } } }, scales: { x: { grid:{color:'rgba(0,0,0,0.04)'}, ticks:{font:{size:10}} }, y: { beginAtZero:true, grid:{color:'rgba(0,0,0,0.04)'}, ticks:{font:{size:10}, callback:function(v){return v+'件';}} } } }
    });
  } catch(e) { console.error('renderSalesChart error:', e); }
}

function renderProfitCharts() {
  try {
    var sales = getFilteredSales();
    var isChannel = profitDimension === 'channel';
    var dimColors = isChannel ? CHANNEL_COLORS : PLATFORM_COLORS;
    var dimLabel = isChannel ? '渠道' : '平台';
    document.getElementById('modeProfitTitle').textContent = isChannel ? '销售模式利润对比' : '平台利润对比';
    document.getElementById('modeProfitSub').textContent = isChannel ? '同款不同渠道的单件毛利差异(元)' : '同款不同平台的单件毛利差异(元)';
    document.getElementById('channelProfitTitle').textContent = isChannel ? '渠道累计利润贡献' : '平台累计利润贡献';
    document.getElementById('channelProfitSub').textContent = '筛选时间范围内各' + dimLabel + '累计毛利额';
    document.getElementById('channelPerfTitle').textContent = isChannel ? '渠道表现对比' : '平台表现对比';
    document.getElementById('channelPerfSub').textContent = '左轴=净销量(件) 右轴=净销售额(元) · 按' + dimLabel + '维度';

    var styleDimGP = {};
    var styleNames = [];
    sales.forEach(function(s) {
      var name = s['款式名称'] || '未知';
      var dim = isChannel ? s._channel : (s._platform || '未知');
      var unitGP = s._unitGP;
      var qty = s._netQty;
      if (!styleDimGP[name]) { styleDimGP[name] = {}; styleNames.push(name); }
      if (!styleDimGP[name][dim]) styleDimGP[name][dim] = { totalGP: 0, qty: 0 };
      styleDimGP[name][dim].totalGP += qty * unitGP;
      styleDimGP[name][dim].qty += qty;
    });

    var dimKeys = [];
    sales.forEach(function(s) { var dim = isChannel ? s._channel : (s._platform || '未知'); if (dimKeys.indexOf(dim) === -1) dimKeys.push(dim); });

    var modeDatasets = dimKeys.map(function(dim) {
      var data = styleNames.map(function(name) { var d = styleDimGP[name] && styleDimGP[name][dim]; return d && d.qty > 0 ? Math.round(d.totalGP / d.qty) : 0; });
      return { label: dim, data: data, backgroundColor: (dimColors[dim] || '#999') + '88', borderColor: dimColors[dim] || '#999', borderWidth: 1.5, borderRadius: 4 };
    });

    if (CHARTS.modeProfit) CHARTS.modeProfit.destroy();
    CHARTS.modeProfit = new Chart(document.getElementById('modeProfitChart'), {
      type: 'bar', data: { labels: styleNames, datasets: modeDatasets },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position:'bottom', labels:{font:{size:9},padding:8,usePointStyle:true,pointStyle:'circle'} }, tooltip: { backgroundColor:'#1A1A18', cornerRadius:8, padding:10, callbacks: { label: function(ctx) { return ctx.dataset.label + '：¥' + ctx.parsed.y; } } } }, scales: { x: { grid:{display:false}, ticks:{font:{size:9}} }, y: { beginAtZero:true, grid:{color:'rgba(0,0,0,0.04)'}, ticks:{font:{size:9}, callback:function(v){return '¥'+v;}} } } }
    });

    var dimTotalGP = {};
    sales.forEach(function(s) { var dim = isChannel ? s._channel : (s._platform || '未知'); if (!dimTotalGP[dim]) dimTotalGP[dim] = 0; dimTotalGP[dim] += s._netQty * s._unitGP; });
    var profitDims = Object.keys(dimTotalGP);
    var profitValues = profitDims.map(function(dim) { return Math.round(dimTotalGP[dim]); });
    var profitColors = profitDims.map(function(dim) { return dimColors[dim] || '#999'; });

    if (CHARTS.channelProfit) CHARTS.channelProfit.destroy();
    CHARTS.channelProfit = new Chart(document.getElementById('channelProfitChart'), {
      type: 'doughnut',
      data: { labels: profitDims, datasets: [{ data: profitValues, backgroundColor: profitColors.map(function(c) { return c + '88'; }), borderColor: profitColors, borderWidth: 2 }] },
      options: { responsive: true, maintainAspectRatio: false, cutout: '55%', plugins: { legend: { position:'bottom', labels:{font:{size:9},padding:8,usePointStyle:true,pointStyle:'circle'} }, tooltip: { backgroundColor:'#1A1A18', cornerRadius:8, padding:10, callbacks: { label: function(ctx) { return ctx.label + '：¥' + ctx.parsed.toLocaleString('zh-CN'); } } } } }
    });

    var dimPerf = {};
    sales.forEach(function(s) { var dim = isChannel ? s._channel : (s._platform || '未知'); if (!dimPerf[dim]) dimPerf[dim] = { qty: 0, gsv: 0 }; dimPerf[dim].qty += s._netQty; dimPerf[dim].gsv += s._gsv; });
    var perfDims = Object.keys(dimPerf);
    var perfQty = perfDims.map(function(dim) { return Math.round(dimPerf[dim].qty); });
    var perfGSV = perfDims.map(function(dim) { return dimPerf[dim].gsv; });
    var perfColors = perfDims.map(function(dim) { return dimColors[dim] || '#999'; });

    if (CHARTS.channelPerf) CHARTS.channelPerf.destroy();
    CHARTS.channelPerf = new Chart(document.getElementById('channelPerfChart'), {
      type: 'bar',
      data: { labels: perfDims, datasets: [
        { label: '净销量(件)', data: perfQty, backgroundColor: perfColors.map(function(c){return c+'88';}), borderColor: perfColors, borderWidth: 1.5, borderRadius: 4, yAxisID: 'y' },
        { label: '净销售额(元)', data: perfGSV, backgroundColor: 'rgba(24,95,165,0.5)', borderColor: '#185FA5', borderWidth: 1.5, borderRadius: 4, yAxisID: 'y1' }
      ] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position:'bottom', labels:{font:{size:9},padding:8,usePointStyle:true,pointStyle:'circle'} }, tooltip: { backgroundColor:'#1A1A18', cornerRadius:8, padding:10, callbacks: { label: function(ctx) { return ctx.dataset.label + '：' + (ctx.datasetIndex === 1 ? '¥' + ctx.parsed.y.toLocaleString('zh-CN') : ctx.parsed.y + '件'); } } } }, scales: { x: { grid:{display:false}, ticks:{font:{size:10}} }, y: { position:'left', beginAtZero:true, grid:{color:'rgba(0,0,0,0.04)'}, ticks:{font:{size:9}, callback:function(v){return v+'件';}} }, y1: { position:'right', beginAtZero:true, grid:{display:false}, ticks:{font:{size:9}, callback:function(v){return (v/10000).toFixed(0)+'万';}} } } }
    });
  } catch(e) { console.error('renderProfitCharts error:', e); }
}

function renderReturnChart() {
  try {
    var sales = getFilteredSales();
    var refunds = getFilteredRefunds();

    var buckets = {};
    function addToBucket(key, only, ret, total, onlyQty, retQty, totalQty) {
      if (!buckets[key]) buckets[key] = { only:0, ret:0, total:0, onlyQty:0, retQty:0, totalQty:0 };
      buckets[key].only += only; buckets[key].ret += ret; buckets[key].total += total;
      buckets[key].onlyQty += onlyQty; buckets[key].retQty += retQty; buckets[key].totalQty += totalQty;
    }

    var totalGMV = 0, totalQty = 0;
    sales.forEach(function(s) { totalGMV += s._gmv; totalQty += s._qty; });
    var avgPrice = totalQty > 0 ? totalGMV / totalQty : 0;

    sales.forEach(function(s) {
      var key = refundTimeUnit === 'week' ? getWeekKey(s['销售日期']) : ('M' + String(getMonthFromDate(s['销售日期']) + 1).padStart(2, '0'));
      if (!key) return;
      var onlyAmt = s._refundOnly;
      var retAmt = s._refundReturn;
      var totalAmt = onlyAmt + retAmt;
      var onlyQty = avgPrice > 0 ? onlyAmt / avgPrice : 0;
      var retQty = avgPrice > 0 ? retAmt / avgPrice : 0;
      var totalQtyEst = onlyQty + retQty;
      addToBucket(key, onlyAmt, retAmt, totalAmt, onlyQty, retQty, totalQtyEst);
    });

    refunds.forEach(function(r) {
      var key = refundTimeUnit === 'week' ? (r['退款周次'] || getWeekKey(r['销售日期'])) : ('M' + String(getMonthFromDate(r['销售日期']) + 1).padStart(2, '0'));
      if (!key) return;
      var onlyAmt = num(r['仅退款金额（款式级）']);
      var retAmt = num(r['退货退款金额（款式级）']);
      var totalAmt = num(r['退款总金额（款式级）']) || (onlyAmt + retAmt);
      var onlyQty = avgPrice > 0 ? onlyAmt / avgPrice : 0;
      var retQty = avgPrice > 0 ? retAmt / avgPrice : 0;
      var totalQtyEst = onlyQty + retQty;
      addToBucket(key, onlyAmt, retAmt, totalAmt, onlyQty, retQty, totalQtyEst);
    });

    var keys = Object.keys(buckets).sort();
    var labels = keys.map(function(k) { return refundTimeUnit === 'week' ? k.replace('-W', '周') : k.replace('M', '') + '月'; });
    var data = keys.map(function(k) {
      var b = buckets[k];
      if (refundMetric === 'amount') {
        if (refundType === 'only') return b.only;
        if (refundType === 'return') return b.ret;
        return b.total;
      } else {
        if (refundType === 'only') return b.onlyQty;
        if (refundType === 'return') return b.retQty;
        return b.totalQty;
      }
    });

    if (CHARTS.return) CHARTS.return.destroy();
    CHARTS.return = new Chart(document.getElementById('returnChart'), {
      type: 'line',
      data: { labels: labels, datasets: [{ label: refundType === 'only' ? '仅退款' : (refundType === 'return' ? '退货退款' : '总退款'), data: data, borderColor: '#D85A30', backgroundColor: 'rgba(216,90,48,0.1)', borderWidth: 2, pointRadius: 3, tension: 0.3, fill: true }] },
      options: { responsive: true, maintainAspectRatio: false, interaction: { mode: 'index', intersect: false }, plugins: { legend: { display: false }, tooltip: { backgroundColor:'#1A1A18', cornerRadius:8, padding:10, callbacks: { label: function(ctx) { return ctx.dataset.label + '：' + (refundMetric === 'amount' ? '¥' + Math.round(ctx.parsed.y).toLocaleString('zh-CN') : Math.round(ctx.parsed.y) + '件'); } } } }, scales: { x: { grid:{color:'rgba(0,0,0,0.04)'}, ticks:{font:{size:10}} }, y: { beginAtZero:true, grid:{color:'rgba(0,0,0,0.04)'}, ticks:{font:{size:10}, callback:function(v){return refundMetric === 'amount' ? (v/10000).toFixed(0)+'万' : v+'件';}} } } }
    });
  } catch(e) { console.error('renderReturnChart error:', e); }
}

function renderInventory() {
  try {
    if (!DB) return;
    var sales = getFilteredSales();
    var activeMonths = getActiveMonths();

    var range = getCurrentRange();
    var daysInRange = (range.start && range.end) ? Math.max(1, Math.round((range.end.getTime() - range.start.getTime()) / 86400000) + 1) : 30;

    var selfSales = sales.filter(function(s) { return s._channel === '自营'; });
    var styles = [];
    selfSales.forEach(function(s) { var name = s['款式名称']; if (name && styles.indexOf(name) === -1) styles.push(name); });

    var el = document.getElementById('inventoryHeatmap');
    var tableHtml = '<table class="hm-table"><thead><tr><th></th>';
    activeMonths.forEach(function(mi) { tableHtml += '<th>' + MONTH_LABELS[mi] + '</th>'; });
    tableHtml += '</tr></thead><tbody>';

    styles.forEach(function(styleName) {
      tableHtml += '<tr><td>' + styleName + '</td>';
      activeMonths.forEach(function(mi) {
        var monthSales = selfSales.filter(function(s) { return s['款式名称'] === styleName && getMonthFromDate(s['销售日期']) === mi; });
        var totalQty = 0;
        monthSales.forEach(function(s) { totalQty += s._netQty; });
        var dailyAvg = totalQty / daysInRange;
        var color = salesSpeedColor(dailyAvg);
        var fontColor = dailyAvg >= 30 ? '#fff' : '#666';
        tableHtml += '<td><div class="hm-cell" style="background:' + color + ';color:' + fontColor + '">' + dailyAvg.toFixed(1) + '</div></td>';
      });
      tableHtml += '</tr>';
    });
    tableHtml += '</tbody></table>';
    el.innerHTML = tableHtml;

    // 按款式编码聚合库存
    var styleInventory = {};
    DB.inventory.forEach(function(item) {
      var sku = item['SKU编码'];
      var prod = sku ? DB.productMap[sku] : null;
      var styleCode = (prod && prod['款式编码']) ? prod['款式编码'] : (item['🔗 款式编码'] || '');
      var styleName = (prod && prod['款式名称']) ? prod['款式名称'] : (item['🔗 款式名称'] || '未知');
      if (!styleCode) return;
      if (!styleInventory[styleCode]) {
        styleInventory[styleCode] = { styleName: styleName, styleCode: styleCode, stock: 0, stockoutDays: 0 };
      }
      styleInventory[styleCode].stock += num(item['当前库存']);
      styleInventory[styleCode].stockoutDays = Math.max(styleInventory[styleCode].stockoutDays, num(item['断货天数']));
    });

    var tbody = document.querySelector('#inventoryTable tbody');
    var html = '';
    Object.values(styleInventory).forEach(function(item) {
      var styleName = item.styleName;
      var styleCode = item.styleCode;
      var stock = item.stock;
      var stockoutDays = item.stockoutDays;

      var styleQty = 0, styleGP = 0, gpCount = 0;
      sales.forEach(function(s) { if (s['款式编码'] === styleCode || s['款式名称'] === styleName) { styleQty += s._netQty; styleGP += s._unitGP; gpCount++; } });
      var dailyAvg = styleQty / daysInRange;
      var turnover = dailyAvg > 0 ? Math.round(stock / dailyAvg) : 999;
      var avgUnitGP = gpCount > 0 ? styleGP / gpCount : 0;
      var stockoutLoss = stockoutDays * dailyAvg * avgUnitGP;
      var status = getStockStatus(turnover, stockoutDays, stock);

      html += '<tr>';
      html += '<td>' + styleName + '<div class="sub-text">' + styleCode + '</div></td>';
      html += '<td class="' + (turnover <= 14 ? 'good' : (turnover <= 30 ? 'hi' : 'warn')) + '">' + (turnover > 999 ? '∞' : turnover + '天') + '</td>';
      html += '<td>' + stock + '件</td>';
      html += '<td>' + stockoutDays + '天</td>';
      html += '<td class="warn">' + (stockoutLoss > 0 ? '¥' + Math.round(stockoutLoss).toLocaleString('zh-CN') : '-') + '</td>';
      html += '<td><span class="status-badge ' + status.cls + '">' + status.label + '</span></td>';
      html += '</tr>';
    });
    tbody.innerHTML = html;
  } catch(e) { console.error('renderInventory error:', e); }
}

var decisionChart = null;
function renderDecisionChart() {
  try {
    if (!DB) return;
    var sales = getFilteredSales();
    var range = getCurrentRange();
    var daysInRange = (range.start && range.end) ? Math.max(1, Math.round((range.end.getTime() - range.start.getTime()) / 86400000) + 1) : 30;

    var styleDataMap = {};
    sales.forEach(function(s) {
      var name = s['款式名称'] || '未知';
      if (!styleDataMap[name]) styleDataMap[name] = { totalGSV: 0, totalQty: 0, totalGP: 0 };
      styleDataMap[name].totalGSV += s._gsv;
      styleDataMap[name].totalQty += s._netQty;
      styleDataMap[name].totalGP += s._netQty * s._unitGP;
    });

    var styles = Object.keys(styleDataMap);
    var data = styles.map(function(name, idx) {
      var d = styleDataMap[name];
      var marginRate = d.totalGSV > 0 ? (d.totalGP / d.totalGSV * 100) : 0;
      var stock = 0;
      DB.inventory.forEach(function(it) {
        var sku = it['SKU编码'];
        var prod = sku ? DB.productMap[sku] : null;
        var itStyleName = prod ? prod['款式名称'] : (it['🔗 款式名称'] || '');
        if (itStyleName === name) stock += num(it['当前库存']);
      });
      var dailyAvg = d.totalQty / daysInRange;
      var turnover = dailyAvg > 0 ? Math.round(stock / dailyAvg) : 999;
      return { style: name, color: getStyleColor(name, idx), turnover: Math.min(turnover, 120), marginRate: Math.round(marginRate * 10) / 10, salesAmount: d.totalGSV, totalQty: d.totalQty };
    });

    var tSlider = document.getElementById('turnoverSlider');
    var mSlider = document.getElementById('marginSlider');
    var turnoverLine = parseFloat(tSlider.value);
    var marginLine = parseFloat(mSlider.value);
    document.getElementById('turnoverVal').textContent = turnoverLine + '天';
    document.getElementById('marginVal').textContent = marginLine + '%';

    var maxSales = Math.max.apply(null, data.map(function(d) { return d.salesAmount; }).concat([1]));
    var bubbleScale = 40;

    var quadrantPlugin = {
      id: 'quadrantLabels',
      afterDraw: function(chart) {
        var ctx = chart.ctx;
        var xScale = chart.scales['x'];
        var yScale = chart.scales['y'];
        if (!xScale || !yScale) return;
        var xPx = xScale.getPixelForValue(turnoverLine);
        var yPx = yScale.getPixelForValue(marginLine);
        ctx.save();
        ctx.setLineDash([5, 5]);
        ctx.strokeStyle = 'rgba(83,74,183,0.3)';
        ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(xPx, yScale.top); ctx.lineTo(xPx, yScale.bottom); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(xScale.left, yPx); ctx.lineTo(xScale.right, yPx); ctx.stroke();
        ctx.setLineDash([]);
        ctx.font = '600 9px -apple-system, sans-serif';
        ctx.textAlign = 'center';
        var topMid = (yScale.top + yPx) / 2;
        var botMid = (yPx + yScale.bottom) / 2;
        var leftMid = (xScale.left + xPx) / 2;
        var rightMid = (xPx + xScale.right) / 2;
        ctx.fillStyle = '#534AB7';
        ctx.fillText('现金牛', leftMid, topMid + 14);
        ctx.fillText('潜力款', rightMid, topMid + 14);
        ctx.fillStyle = '#6B6A65';
        ctx.fillText('流量款', leftMid, botMid - 6);
        ctx.fillStyle = '#D85A30';
        ctx.fillText('积压款', rightMid, botMid - 6);
        ctx.restore();
      }
    };

    var datasets = data.map(function(d) {
      return { label: d.style, data: [{ x: d.turnover, y: d.marginRate, r: Math.max(6, Math.round(d.salesAmount / maxSales * bubbleScale)), salesAmount: d.salesAmount }], backgroundColor: d.color + '55', borderColor: d.color, borderWidth: 2, hoverBackgroundColor: d.color + '88' };
    });

    if (decisionChart) decisionChart.destroy();
    decisionChart = new Chart(document.getElementById('decisionChart'), {
      type: 'bubble',
      data: { datasets: datasets },
      plugins: [quadrantPlugin],
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { backgroundColor:'#1A1A18', cornerRadius:8, padding:10, callbacks: { label: function(ctx) { var d = ctx.raw; return [ctx.dataset.label, '周转天数: ' + d.x.toFixed(0) + '天', '毛利率(%): ' + d.y.toFixed(1) + '%', '净销售额: ¥' + (d.salesAmount || 0).toLocaleString('zh-CN')]; } } } }, scales: { x: { title:{display:true, text:'库存周转天数（左快右慢）', font:{size:10,weight:'500'}, color:'#6B6A65'}, min:0, max:120, grid:{color:'rgba(0,0,0,0.04)'}, ticks:{font:{size:9}, callback:function(v){return v+'天';}} }, y: { title:{display:true, text:'毛利率(%)', font:{size:10,weight:'500'}, color:'#6B6A65'}, min:0, max:50, grid:{color:'rgba(0,0,0,0.04)'}, ticks:{font:{size:9}, callback:function(v){return v+'%';}} } } }
    });
  } catch(e) { console.error('renderDecisionChart error:', e); }
}

document.getElementById('turnoverSlider').addEventListener('input', function() { renderDecisionChart(); });
document.getElementById('marginSlider').addEventListener('input', function() { renderDecisionChart(); });

function renderRankings() {
  try {
    if (!DB) return;
    var sales = getFilteredSales();

    var anchorStats = {};
    sales.filter(function(s) { return s._channel === '达播'; }).forEach(function(s) {
      var anchorNames = s['主播'];
      if (!Array.isArray(anchorNames)) anchorNames = [anchorNames];
      anchorNames.forEach(function(anchorName) {
        var name = firstText(anchorName);
        if (!name) return;
        if (!anchorStats[name]) anchorStats[name] = { gsv: 0, qty: 0, platform: s._platform || '' };
        anchorStats[name].gsv += s._gsv;
        anchorStats[name].qty += s._netQty;
      });
    });

    var anchorRanking = Object.entries(anchorStats).sort(function(a, b) { return b[1].gsv - a[1].gsv; });
    var anchorTbody = document.querySelector('#anchorRankingTable tbody');
    var anchorHtml = '';
    anchorRanking.slice(0, 10).forEach(function(entry, i) {
      var name = entry[0], st = entry[1];
      var badgeClass = i === 0 ? 'rank-badge top1' : i === 1 ? 'rank-badge top2' : i === 2 ? 'rank-badge top3' : 'rank-badge normal';
      anchorHtml += '<tr><td><span class="' + badgeClass + '">' + (i+1) + '</span></td>';
      anchorHtml += '<td>' + name + '</td><td>' + st.platform + '</td>';
      anchorHtml += '<td>¥' + Math.round(st.gsv).toLocaleString('zh-CN') + '</td>';
      anchorHtml += '<td>' + Math.round(st.qty).toLocaleString('zh-CN') + '件</td></tr>';
    });
    anchorTbody.innerHTML = anchorHtml;

    var buyerStats = {};
    sales.filter(function(s) { return s._channel === '买手店'; }).forEach(function(s) {
      var buyerNames = s['买手店'];
      if (!Array.isArray(buyerNames)) buyerNames = [buyerNames];
      buyerNames.forEach(function(buyerName) {
        var name = firstText(buyerName);
        if (!name) return;
        if (!buyerStats[name]) {
          var buyer = DB.buyerMap[name];
          buyerStats[name] = { gsv: 0, qty: 0, city: buyer ? (buyer['城市'] || '') : '', type: buyer ? (buyer['类型'] || '') : '' };
        }
        buyerStats[name].gsv += s._gsv;
        buyerStats[name].qty += s._netQty;
      });
    });

    var buyerRanking = Object.entries(buyerStats).sort(function(a, b) { return b[1].gsv - a[1].gsv; });
    var buyerTbody = document.querySelector('#buyerRankingTable tbody');
    var buyerHtml = '';
    buyerRanking.slice(0, 10).forEach(function(entry, i) {
      var name = entry[0], st = entry[1];
      var badgeClass = i === 0 ? 'rank-badge top1' : i === 1 ? 'rank-badge top2' : i === 2 ? 'rank-badge top3' : 'rank-badge normal';
      buyerHtml += '<tr><td><span class="' + badgeClass + '">' + (i+1) + '</span></td>';
      buyerHtml += '<td>' + name + '</td><td>' + st.city + '</td><td>' + st.type + '</td>';
      buyerHtml += '<td>¥' + Math.round(st.gsv).toLocaleString('zh-CN') + '</td>';
      buyerHtml += '<td>' + Math.round(st.qty).toLocaleString('zh-CN') + '件</td></tr>';
    });
    buyerTbody.innerHTML = buyerHtml;
  } catch(e) { console.error('renderRankings error:', e); }
}

function renderAll() {
  if (!DB) return;
  updateAllPeriodBadges();
  renderKPI();
  renderSalesChart();
  renderProfitCharts();
  renderReturnChart();
  renderInventory();
  renderDecisionChart();
  renderRankings();
}

// 筛选事件
document.querySelectorAll('.fbtn[data-filter="period"]').forEach(function(btn) {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.fbtn[data-filter="period"]').forEach(function(b) { b.classList.remove('active'); });
    btn.classList.add('active');
    curPeriod = btn.dataset.val;
    updateRangeSelectorVisibility();
    updateWeekRangeHint();
    updatePeriodLabel();
    updateAllPeriodBadges();
    renderAll();
  });
});

document.querySelectorAll('.fbtn[data-filter="channel"]').forEach(function(btn) {
  btn.addEventListener('click', function() {
    var val = btn.dataset.val;
    if (val === 'all') selectedChannels = new Set(['自营', '达播', '买手店']);
    else {
      if (selectedChannels.has(val)) { selectedChannels.delete(val); if (selectedChannels.size === 0) selectedChannels = new Set(['自营', '达播', '买手店']); }
      else selectedChannels.add(val);
    }
    updateChannelButtonStates();
    updatePlatformAndBuyerTypeVisibility();
    renderAll();
  });
});

document.querySelectorAll('.fbtn[data-filter="platform"]').forEach(function(btn) {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.fbtn[data-filter="platform"]').forEach(function(b) { b.classList.remove('active'); });
    btn.classList.add('active');
    curPlatform = btn.dataset.val;
    renderAll();
  });
});

document.querySelectorAll('.fbtn[data-filter="buyerType"]').forEach(function(btn) {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.fbtn[data-filter="buyerType"]').forEach(function(b) { b.classList.remove('active'); });
    btn.classList.add('active');
    curBuyerType = btn.dataset.val;
    renderAll();
  });
});

document.querySelectorAll('#profitDimToggle .dim-btn').forEach(function(btn) {
  btn.addEventListener('click', function() {
    document.querySelectorAll('#profitDimToggle .dim-btn').forEach(function(b) { b.classList.remove('active'); });
    btn.classList.add('active');
    profitDimension = btn.dataset.dim;
    renderProfitCharts();
  });
});

document.querySelectorAll('#salesQtyToggle .dim-btn').forEach(function(btn) {
  btn.addEventListener('click', function() {
    document.querySelectorAll('#salesQtyToggle .dim-btn').forEach(function(b) { b.classList.remove('active'); });
    btn.classList.add('active');
    salesQtyType = btn.dataset.qty;
    renderSalesChart();
  });
});

document.querySelectorAll('#refundMetricToggle .dim-btn').forEach(function(btn) {
  btn.addEventListener('click', function() {
    document.querySelectorAll('#refundMetricToggle .dim-btn').forEach(function(b) { b.classList.remove('active'); });
    btn.classList.add('active');
    refundMetric = btn.dataset.metric;
    renderReturnChart();
  });
});

document.querySelectorAll('#refundTypeToggle .dim-btn').forEach(function(btn) {
  btn.addEventListener('click', function() {
    document.querySelectorAll('#refundTypeToggle .dim-btn').forEach(function(b) { b.classList.remove('active'); });
    btn.classList.add('active');
    refundType = btn.dataset.rtype;
    renderReturnChart();
  });
});

document.querySelectorAll('#refundTimeToggle .dim-btn').forEach(function(btn) {
  btn.addEventListener('click', function() {
    document.querySelectorAll('#refundTimeToggle .dim-btn').forEach(function(b) { b.classList.remove('active'); });
    btn.classList.add('active');
    refundTimeUnit = btn.dataset.tunit;
    renderReturnChart();
  });
});

loadData();
'''

fallback_str = json.dumps(data_json, ensure_ascii=False)
js_code = JS_CODE.replace('__FALLBACK_DATA__', fallback_str)

final_html = head_part + '\n' + body_part + '\n<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>\n<script>\n' + js_code + '\n</script>\n</body>\n</html>'

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(final_html)

print('已生成新仪表盘:', html_path)
print('文件大小:', len(final_html), '字符')
