const { MemorySystem, DB_PATH, INDEX_PATH, MODEL_CACHE_DIR } = require('./memory_system');

(async () => {
  const memory = new MemorySystem();
  await memory.init();
  const status = {
    dbPath: DB_PATH,
    vectorPath: INDEX_PATH,
    modelCachePath: MODEL_CACHE_DIR,
    pinnedFacts: memory.getPinnedFacts(10),
    projectFacts: memory.getProjectFacts(),
  };
  console.log(JSON.stringify(status, null, 2));
  memory.close();
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
