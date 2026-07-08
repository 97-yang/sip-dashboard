#!/usr/bin/env node
// SIP CLASS 数据获取脚本 v3
// 适配新 5 表结构（产品资料库_新、库存情况_新、销售数据_新、主播资料库、买手店资料库）
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const BASE_TOKEN = 'Wa2lbJtJJaBnU8shuQicW6djnmd';
const LARK_CLI = '/Users/yangyang/.workbuddy/binaries/node/versions/22.12.0/bin/node';
const CLI_PATH = '/Users/yangyang/.workbuddy/binaries/node/cli-connector-packages/bin/lark-cli';
const OUTPUT = path.join(__dirname, 'data.json');

const TABLES = {
  products:  'tbloqO6aUWuYUFXN',  // 产品资料库_新
  sales:     'tblaqV8VUs9J0TPR',   // 销售数据_新
  inventory: 'tblhEywWD302Xmoq',  // 库存情况_新
  anchors:   'tblXN0DBqUGh89BK',   // 主播资料库
  buyers:    'tblxYA07aCARdhuA',   // 买手店资料库
};

// =============================================
//  API 调用
// =============================================
function apiCall(method, urlPath) {
  const cmd = `${LARK_CLI} ${CLI_PATH} api ${method} "${urlPath}" 2>/dev/null`;
  try {
    const result = execSync(cmd, {
      cwd: '/Users/yangyang/.workbuddy/binaries/node/cli-connector-packages',
      encoding: 'utf8',
      timeout: 30000,
      maxBuffer: 10 * 1024 * 1024  // 10MB — sales 表响应可能超过默认 1MB
    });
    return JSON.parse(result);
  } catch (e) {
    console.error(`  API call failed: ${e.message}`);
    return null;
  }
}

// 分页获取所有记录
function fetchAllRecords(tableId) {
  const allRecords = [];
  let pageToken = undefined;
  let page = 0;

  do {
    let url = `/open-apis/bitable/v1/apps/${BASE_TOKEN}/tables/${tableId}/records?page_size=500`;
    if (pageToken) url += `&page_token=${pageToken}`;

    const json = apiCall('GET', url);
    if (!json || !json.ok || !json.data) {
      console.error(`  Failed to fetch records from ${tableId}: ok=${json?.ok}, msg=${json?.msg}`);
      break;
    }

    const items = json.data.items || [];
    allRecords.push(...items);
    pageToken = json.data.has_more ? json.data.page_token : undefined;
    page++;
    console.log(`    page ${page}: ${items.length} records`);
  } while (pageToken);

  return allRecords;
}

// 获取字段元数据
function fetchFields(tableId) {
  const json = apiCall('GET', `/open-apis/bitable/v1/apps/${BASE_TOKEN}/tables/${tableId}/fields`);
  if (!json || !json.ok || !json.data) return [];
  return (json.data.items || []).map(f => ({
    id: f.field_id,
    name: f.field_name,
    type: f.type,
    property: f.property || {}
  }));
}

// =============================================
//  字段值解析（把飞书API原始值转成仪表盘可用的简单类型）
// =============================================
function parseVal(val, ftype, fprop) {
  if (val === undefined || val === null || val === '') return null;

  // 文本 (1)
  if (ftype === 1) {
    if (Array.isArray(val)) return val.map(v => v.text || v).join('');
    return String(val);
  }

  // 数字 (2)
  if (ftype === 2) {
    if (typeof val === 'number') return val;
    const n = parseFloat(val);
    return isNaN(n) ? null : n;
  }

  // 单选 (3)
  if (ftype === 3) {
    if (typeof val === 'object' && val !== null) return val.text || val.name || null;
    return String(val);
  }

  // 多选 (4)
  if (ftype === 4) {
    if (Array.isArray(val)) return val.map(v => v.text || v.name || v);
    return null;
  }

  // 日期 (5)
  if (ftype === 5) {
    if (typeof val === 'number') {
      // 飞书日期字段返回 Unix 毫秒时间戳
      return new Date(val).toISOString().split('T')[0]; // YYYY-MM-DD
    }
    if (typeof val === 'string') return val;
    return null;
  }

  // 复选框 (7)
  if (ftype === 7) return !!val;

  // 附件 (17)
  if (ftype === 17) {
    if (!Array.isArray(val) || val.length === 0) return null;
    const file = val[0];
    return file.attachmentToken || file.file_token || file.id || file.url || null;
  }

  // 双向关联 (21) / 单向关联 (18)
  if (ftype === 21 || ftype === 18) {
    if (!Array.isArray(val) || val.length === 0) return null;
    // 返回关联记录的文本数组
    const texts = [];
    for (const v of val) {
      if (typeof v === 'string') { texts.push(v); continue; }
      // 优先 text_arr（多行文本数组），其次 text
      if (Array.isArray(v.text_arr) && v.text_arr.length > 0) {
        texts.push(v.text_arr.join(''));
      } else if (v.text) {
        texts.push(v.text);
      } else if (v.record_ids && Array.isArray(v.record_ids) && v.record_ids.length > 0) {
        texts.push(v.record_ids[0]); // 回退到 record_id
      }
    }
    return texts.length > 0 ? texts : null;
  }

  // 公式 (20)
  if (ftype === 20) {
    return parseFormulaVal(val);
  }

  // 查找引用 lookup (19)
  if (ftype === 19) {
    if (Array.isArray(val)) {
      if (val.length === 0) return null;
      if (val.length === 1) return parseFormulaVal(val[0]);
      return val.map(v => parseFormulaVal(v));
    }
    return parseFormulaVal(val);
  }

  // 创建时间 (1001) / 修改时间 (1002)
  if (ftype === 1001 || ftype === 1002) {
    if (typeof val === 'number') return new Date(val).toISOString();
    return val;
  }

  // 其他类型原样返回
  return val;
}

// 解析公式字段的值
function parseFormulaVal(val) {
  if (val === undefined || val === null || val === '') return null;
  if (typeof val === 'number') return val;
  if (typeof val === 'boolean') return val;
  if (typeof val === 'string') {
    const n = parseFloat(val);
    return isNaN(n) ? val : n;
  }
  if (Array.isArray(val)) {
    if (val.length === 0) return null;
    // 公式返回数组时（如多选），取文本
    if (val.length === 1) {
      const item = val[0];
      if (typeof item === 'object' && item !== null) {
        if (item.text !== undefined) return item.text;
        if (item.value !== undefined) return parseFloat(item.value) || 0;
      }
      return typeof item === 'number' ? item : String(item);
    }
    return val.map(v => (typeof v === 'object' && v !== null) ? (v.text || v.value || String(v)) : v);
  }
  if (typeof val === 'object' && val !== null) {
    if (val.value !== undefined) return parseFloat(val.value) || 0;
    if (val.text !== undefined) return val.text;
    if (val.cent !== undefined) return val.cent / 100;
  }
  return val;
}

// 字段名标准化：去掉 lookup(🔗) / formula(⚙️) 等 emoji 前缀，方便前端统一使用
function normalizeFieldName(name) {
  return name
    .replace(/^\u{1F517}\s*/u, '')   // 🔗
    .replace(/^\u{2699}\u{FE0F}\s*/u, '') // ⚙️
    .trim();
}

// =============================================
//  解析整表数据
// =============================================
function parseTable(tableId) {
  console.log(`  Fetching fields...`);
  const rawFieldsMeta = fetchFields(tableId);
  const fieldsMeta = rawFieldsMeta
    .filter(fm => !fm.name.includes('_旧'))  // 过滤废弃的link字段
    .map(fm => ({
      ...fm,
      originalName: fm.name,
      name: normalizeFieldName(fm.name)
    }));
  console.log(`  ${fieldsMeta.length} fields: ${fieldsMeta.map(f => f.name).join(', ')}`);

  console.log(`  Fetching records...`);
  const rawRecords = fetchAllRecords(tableId);

  const records = rawRecords.map(rec => {
    const row = { _id: rec.record_id };
    const fields = rec.fields || {};

    fieldsMeta.forEach(fm => {
      const rawVal = fields[fm.originalName];
      row[fm.name] = parseVal(rawVal, fm.type, fm.property);
    });

    return row;
  });

  console.log(`  → ${records.length} records parsed`);
  return { fields: fieldsMeta, records };
}

// =============================================
//  主流程
// =============================================
console.log('SIP CLASS 数据获取 v2');
console.log('=====================\n');

const data = { fetchedAt: new Date().toISOString(), tables: {} };

for (const [key, tableId] of Object.entries(TABLES)) {
  console.log(`\n[${key}] (${tableId})`);
  data.tables[key] = parseTable(tableId);
}

fs.writeFileSync(OUTPUT, JSON.stringify(data), 'utf8');

const totalRecords = Object.values(data.tables).reduce((sum, t) => sum + t.records.length, 0);
console.log(`\n=====================`);
console.log(`数据已保存到 ${OUTPUT}`);
console.log(`总记录数: ${totalRecords}`);
