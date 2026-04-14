const fs = require('fs');
const path = require('path');
const { ROOT, MemorySystem } = require('./memory_system');

(async () => {
  const memory = new MemorySystem();
  await memory.init();

  const workingBufferPath = path.join(ROOT, 'memory', 'working-buffer.md');
  const sessionStatePath = path.join(ROOT, 'SESSION-STATE.md');
  const memoryPath = path.join(ROOT, 'MEMORY.md');

  const workingBuffer = fs.existsSync(workingBufferPath) ? fs.readFileSync(workingBufferPath, 'utf8') : '';
  const sessionState = fs.existsSync(sessionStatePath) ? fs.readFileSync(sessionStatePath, 'utf8') : '';
  const longMemory = fs.existsSync(memoryPath) ? fs.readFileSync(memoryPath, 'utf8') : '';
  const search = await memory.search('当前主线 关键约束 最近决策 下一步', 6);

  console.log(JSON.stringify({
    workingBufferTail: workingBuffer.slice(-2000),
    sessionStateTail: sessionState.slice(-2000),
    memoryTail: longMemory.slice(-2000),
    search,
  }, null, 2));

  memory.close();
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
