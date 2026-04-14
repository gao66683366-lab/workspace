const path = require('path');
const fs = require('fs');
const { MemorySystem, ROOT, DB_PATH, INDEX_PATH } = require('./memory_system');

const DEFAULT_FILES = [
  'IDENTITY.md',
  'USER.md',
  'SOUL.md',
  'AGENTS.md',
  'MEMORY.md',
  'SESSION-STATE.md',
  'improvement_log.md',
  path.join('memory', '2026-03-08.md'),
  path.join('memory', '2026-03-09.md'),
  path.join('memory', 'hot', 'HOT_MEMORY.md'),
  path.join('memory', 'working-buffer.md'),
  path.join('memory', 'checkpoints', '2026-03-09-context-checkpoint.md'),
  path.join('notes', 'open-loops.md'),
  path.join('00-agent', 'MEMORY.md'),
  path.join('00-agent', 'IDENTITY.md'),
  path.join('00-agent', 'USER.md'),
  path.join('00-agent', 'SOUL.md'),
  path.join('00-agent', 'AGENTS.md'),
];

(async () => {
  const memory = new MemorySystem();
  await memory.init();

  const ingested = [];
  for (const relativeFile of DEFAULT_FILES) {
    const fullPath = path.join(ROOT, relativeFile);
    if (!fs.existsSync(fullPath)) continue;
    ingested.push(await memory.ingestMarkdownFile(fullPath));
  }

  const summary = {
    db: DB_PATH,
    vector: INDEX_PATH,
    ingested,
    pinnedFacts: memory.getPinnedFacts(12),
    projectFacts: memory.getProjectFacts(),
  };

  console.log(JSON.stringify(summary, null, 2));
  memory.close();
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
