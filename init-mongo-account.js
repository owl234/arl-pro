// 切换到 arl 数据库
db = db.getSiblingDB('arl');
// 注入默认账号
db.user.insert({ username: 'admin', password: hex_md5('arlsalt!@#'+'arlpass') });
print("✅ ARL Pro: 默认账号 admin / arlpass 注入成功！");