const fs = require('fs');
const path = require('path');
const { ROOT } = require('./memory_system');

const logPath = path.join(ROOT, 'improvement_log.md');
const now = new Date();
const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

function parseEntries(content) {
  const blocks = content.split(/\n## \[/).slice(1);
  return blocks.map(block => {
    const full = '## [' + block;
    const match = full.match(/^## \[([^\]]+)\]\s+(.+)\n-\s+([\s\S]*?)$/m);
    if (!match) return null;
    const [, stamp, category, insight] = match;
    const date = new Date(stamp.replace(/\//g, '-'));
    return { stamp, date, category: category.trim(), insight: insight.trim() };
  }).filter(Boolean);
}

const content = fs.existsSync(logPath) ? fs.readFileSync(logPath, 'utf8') : '# Self-Improvement Log\n';
const entries = parseEntries(content).filter(x => !Number.isNaN(x.date.getTime()) && x.date >= weekAgo);
const byCategory = {};
for (const entry of entries) byCategory[entry.category] = (byCategory[entry.category] || 0) + 1;

const lines = [
  '# 🔄 Self-Improvement Weekly Report',
  `Generated: ${now.toLocaleString('zh-CN', { hour12: false })}`,
  '',
  '## 概览',
  `- 最近 7 天记录数：${entries.length}`,
  ...Object.entries(byCategory).map(([k, v]) => `- ${k}: ${v}`),
  '',
  '## 最近改进',
  ...(entries.slice(-10).map(x => `- [${x.stamp}] (${x.category}) ${x.insight}`)),
];

console.log(lines.join('\n'));
