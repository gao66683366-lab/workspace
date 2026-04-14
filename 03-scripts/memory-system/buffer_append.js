const fs = require('fs');
const path = require('path');
const { ROOT, MemorySystem } = require('./memory_system');

const role = process.argv[2] || 'Human';
const text = process.argv.slice(3).join(' ').trim();

if (!text) {
  console.error('Usage: node 03-scripts/memory-system/buffer_append.js <Human|Agent> <text>');
  process.exit(1);
}

(async () => {
  const filePath = path.join(ROOT, 'memory', 'working-buffer.md');
  const now = new Date().toLocaleString('zh-CN', { hour12: false });
  const block = `\n## [${now}] ${role}\n${text}\n`;
  fs.appendFileSync(filePath, block, 'utf8');

  const memory = new MemorySystem();
  await memory.init();
  await memory.ingestMarkdownFile(filePath, {
    category: 'working-buffer',
    scope: 'workspace',
    tags: ['proactive-agent', 'buffer', role.toLowerCase()],
    maxChars: 900,
  });

  console.log(JSON.stringify({ ok: true, filePath, role, text }, null, 2));
  memory.close();
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
