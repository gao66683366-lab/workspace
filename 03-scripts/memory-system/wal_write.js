const fs = require('fs');
const path = require('path');
const { ROOT, MemorySystem } = require('./memory_system');

const args = process.argv.slice(2);
const category = args[0] || 'general';
const detail = args.slice(1).join(' ').trim();

if (!detail) {
  console.error('Usage: node 03-scripts/memory-system/wal_write.js <category> <detail>');
  process.exit(1);
}

(async () => {
  const filePath = path.join(ROOT, 'SESSION-STATE.md');
  const now = new Date().toLocaleString('zh-CN', { hour12: false });
  const block = `\n### [${now}] ${category}\n- ${detail}\n`;
  fs.appendFileSync(filePath, block, 'utf8');

  const memory = new MemorySystem();
  await memory.init();
  await memory.ingestMarkdownFile(filePath, {
    category: 'session-state',
    scope: 'workspace',
    tags: ['proactive-agent', 'wal', category],
    maxChars: 900,
  });

  console.log(JSON.stringify({ ok: true, filePath, category, detail }, null, 2));
  memory.close();
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
