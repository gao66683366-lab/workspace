const { MemorySystem } = require('./memory_system');

const query = process.argv.slice(2).join(' ').trim();
if (!query) {
  console.error('Usage: node 03-scripts/memory-system/search.js <query>');
  process.exit(1);
}

(async () => {
  const memory = new MemorySystem();
  await memory.init();
  const results = await memory.search(query, 8);
  console.log(JSON.stringify({ query, results }, null, 2));
  memory.close();
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
