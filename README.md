# SIP CLASS 销售仪表盘

SIP CLASS 内部销售数据可视化仪表盘，数据源自飞书多维表格，定期自动同步。

## 在线访问

- GitHub Pages 地址：`https://97-yang.github.io/sip-dashboard/`
- 访问密码：`sipclass888`（前端简单密码保护，同一浏览器登录一次后自动记住）

## 项目结构

- `index.html`：仪表盘页面（含前端密码保护）
- `data.json`：从飞书拉取并结构化后的数据
- `fetch-data.js`：飞书数据同步脚本（本地/自动化执行）
- `data_quality_check.py`：数据质量检查脚本
- `add_password.py`：生成带密码保护的 index.html

## 数据更新流程

1. 小伙伴在飞书多维表格录入/更新数据
2. 自动化或手动运行 `fetch-data.js` 拉取最新数据并更新 `data.json`
3. `git push` 到 GitHub
4. GitHub Pages 自动部署，团队成员刷新页面即可看到最新数据

## 数据源

飞书多维表格：SIP CLASS 销售数据
