const fs = require('fs');
const path = require('path');
const { ROOT } = require('./memory_system');

const logPath = path.join(ROOT, 'improvement_log.md');
const content = fs.existsSync(logPath) ? fs.readFileSync(logPath, 'utf8') : '';
const totalEntries = (content.match(/\n## \[/g) || []).length;

console.log(JSON.stringify({
  log_exists: fs.existsSync(logPath),
  soul_exists: fs.existsSync(path.join(ROOT, 'SOUL.md')),
  total_entries: totalEntries,
  log_size_kb: Number((Buffer.byteLength(content, 'utf8') / 1024).toFixed(2)),
  log_path: logPath,
}, null, 2));
