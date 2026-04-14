const fs = require('fs');
const path = require('path');
const { MemorySystem, ROOT } = require('./memory_system');

const args = process.argv.slice(2);
const category = args[0] || 'general';
const insight = args.slice(1).join(' ').trim();

if (!insight) {
  console.error('Usage: node 03-scripts/memory-system/improve.js <category> <insight>');
  process.exit(1);
}

(async () => {
  const memory = new MemorySystem();
  await memory.init();

  const timestamp = new Date();
  const stamp = timestamp.toLocaleString('zh-CN', { hour12: false });
  const logPath = path.join(ROOT, 'improvement_log.md');
  const block = `\n## [${stamp}] ${category}\n- ${insight}\n`;
  fs.appendFileSync(logPath, block, 'utf8');

  await memory.ingestMarkdownFile(logPath, {
    category: 'improvement',
    scope: 'workspace',
    tags: ['self-improving-agent', category],
    maxChars: 900,
  });

  memory.upsertDecision({
    topic: `self-improvement:${category}`,
    decision: insight,
    rationale: 'Logged via self-improving-agent bridge',
    source_path: 'improvement_log.md',
  });

  console.log(JSON.stringify({ ok: true, category, insight, logPath }, null, 2));
  memory.close();
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
