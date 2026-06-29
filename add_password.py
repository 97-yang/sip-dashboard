#!/usr/bin/env python3
# 为 SIP CLASS 仪表盘添加前端密码保护，生成 GitHub Pages 可用的 index.html

import re

SRC = "/Users/yangyang/Desktop/SIP_CLASS_销售仪表盘_2026.html"
DEST = "/Users/yangyang/Desktop/sip-dashboard/index.html"
PASSWORD = "sipclass888"

LOGIN_CSS = """
/* 密码保护登录层 */
.login-overlay{position:fixed;inset:0;background:var(--bg);display:flex;align-items:center;justify-content:center;z-index:9999;font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","PingFang SC","Hiragino Sans GB",sans-serif}
.login-overlay.hidden{display:none}
.login-box{background:var(--surface);border-radius:var(--radius);padding:36px 32px;box-shadow:var(--shadow);border:.5px solid var(--border);width:100%;max-width:340px;text-align:center}
.login-box h1{font-size:18px;font-weight:600;margin-bottom:6px;color:var(--text1);letter-spacing:-.3px}
.login-box p{font-size:11px;color:var(--text3);margin-bottom:22px;line-height:1.6}
.login-box input{width:100%;padding:10px 12px;border-radius:10px;border:1px solid var(--border);background:var(--surface);color:var(--text1);font-size:13px;font-family:inherit;margin-bottom:12px;outline:none;transition:border-color .15s}
.login-box input:focus{border-color:var(--accent)}
.login-box button{width:100%;padding:10px 12px;border-radius:10px;border:none;background:var(--accent);color:#fff;font-size:13px;font-weight:600;cursor:pointer;font-family:inherit;transition:opacity .15s}
.login-box button:hover{opacity:.9}
.login-error{color:var(--red);font-size:11px;margin-top:10px;display:none}
.page-content{display:none}
.page-content.authenticated{display:block}
"""

LOGIN_HTML = f"""
<!-- 密码保护登录层 -->
<div class="login-overlay" id="loginOverlay">
  <div class="login-box">
    <h1>SIP CLASS 销售仪表盘</h1>
    <p>核心团队内部使用，请输入访问密码</p>
    <input type="password" id="passwordInput" placeholder="访问密码" onkeydown="if(event.key==='Enter')checkPassword()" autocomplete="off">
    <button onclick="checkPassword()">进入仪表盘</button>
    <div class="login-error" id="loginError">密码错误，请重试</div>
  </div>
</div>

<div class="page-content" id="pageContent">
"""

LOGIN_JS = f"""
// 密码保护
function checkPassword(){{
  var input = document.getElementById('passwordInput').value;
  if(input === '{PASSWORD}'){{
    localStorage.setItem('sip_dashboard_auth','1');
    document.getElementById('loginOverlay').classList.add('hidden');
    document.getElementById('pageContent').classList.add('authenticated');
  }} else {{
    document.getElementById('loginError').style.display = 'block';
  }}
}}
(function(){{
  if(localStorage.getItem('sip_dashboard_auth') === '1'){{
    var overlay = document.getElementById('loginOverlay');
    var content = document.getElementById('pageContent');
    if(overlay) overlay.classList.add('hidden');
    if(content) content.classList.add('authenticated');
  }}
}})();
"""

with open(SRC, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. 在 </style> 前插入登录 CSS
html = html.replace('</style>', LOGIN_CSS.rstrip() + '\n</style>', 1)

# 2. 在 <body> 后插入登录层和 page-content 包裹开头
html = html.replace('<body>\n<div class="page">', '<body>\n' + LOGIN_HTML.rstrip() + '\n<div class="page">', 1)

# 3. 在最后的 </script> 前插入密码 JS，并补上 </body></html>
html = html.replace('</script>\n</body>\n</html>', '</script>\n</body>\n</html>', 1)  # 先移除如果存在
html = re.sub(r'^(.*)</script>\s*$', r'\1\n' + LOGIN_JS.rstrip() + '\n</script>\n</body>\n</html>', html, flags=re.DOTALL)

with open(DEST, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"已生成密码保护版本：{DEST}")
print(f"访问密码：{PASSWORD}")
