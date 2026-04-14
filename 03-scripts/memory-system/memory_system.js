const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const Database = require('better-sqlite3');
const { LocalIndex } = require('vectra');

const ROOT = path.resolve(__dirname, '..', '..');
const BASE_DIR = path.join(ROOT, '.openclaw', 'memory-system');
const DB_DIR = path.join(BASE_DIR, 'sqlite');
const VECTOR_DIR = path.join(BASE_DIR, 'vector');
const MODEL_CACHE_DIR = path.join(BASE_DIR, 'models');
const DB_PATH = path.join(DB_DIR, 'long_term_memory.sqlite');
const INDEX_PATH = path.join(VECTOR_DIR, 'semantic-memory');
const EMBEDDING_DIM = 256;

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function sha256(text) {
  return crypto.createHash('sha256').update(text).digest('hex');
}

function splitIntoChunks(text, maxChars = 1200) {
  const normalized = text.replace(/\r\n/g, '\n').trim();
  if (!normalized) return [];
  const parts = normalized.split(/\n\s*\n/g);
  const chunks = [];
  let current = '';

  for (const part of parts) {
    const piece = part.trim();
    if (!piece) continue;
    if ((current + '\n\n' + piece).trim().length <= maxChars) {
      current = current ? `${current}\n\n${piece}` : piece;
      continue;
    }
    if (current) chunks.push(current);
    if (piece.length <= maxChars) {
      current = piece;
      continue;
    }
    let start = 0;
    while (start < piece.length) {
      chunks.push(piece.slice(start, start + maxChars));
      start += maxChars;
    }
    current = '';
  }

  if (current) chunks.push(current);
  return chunks;
}

function inferCategory(sourcePath, text) {
  const p = sourcePath.toLowerCase();
  if (p.includes('identity')) return 'identity';
  if (p.includes('user')) return 'user';
  if (p.includes('memory')) return 'memory';
  if (p.includes('soul')) return 'persona';
  if (p.includes('agent')) return 'agent';
  if (/待办|todo|下一步/.test(text)) return 'task';
  if (/已确认|约束|必须|不能/.test(text)) return 'fact';
  return 'note';
}

class MemorySystem {
  constructor() {
    ensureDir(DB_DIR);
    ensureDir(VECTOR_DIR);
    ensureDir(MODEL_CACHE_DIR);
    this.db = new Database(DB_PATH);
    this.index = new LocalIndex(INDEX_PATH);
  }

  async init() {
    this.db.pragma('journal_mode = WAL');
    this.db.pragma('foreign_keys = ON');
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS memory_items (
        id TEXT PRIMARY KEY,
        scope TEXT NOT NULL,
        category TEXT NOT NULL,
        title TEXT,
        content TEXT NOT NULL,
        source_path TEXT,
        source_ref TEXT,
        tags_json TEXT DEFAULT '[]',
        confidence REAL DEFAULT 1.0,
        is_pinned INTEGER DEFAULT 0,
        valid_from TEXT DEFAULT (datetime('now')),
        valid_to TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now')),
        content_hash TEXT NOT NULL UNIQUE
      );

      CREATE TABLE IF NOT EXISTS decisions (
        id TEXT PRIMARY KEY,
        topic TEXT NOT NULL,
        decision TEXT NOT NULL,
        rationale TEXT,
        status TEXT DEFAULT 'active',
        source_path TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
      );

      CREATE TABLE IF NOT EXISTS project_facts (
        id TEXT PRIMARY KEY,
        project TEXT NOT NULL,
        fact_key TEXT NOT NULL,
        fact_value TEXT NOT NULL,
        unit TEXT,
        source_path TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now')),
        UNIQUE(project, fact_key)
      );

      CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        status TEXT DEFAULT 'open',
        priority TEXT DEFAULT 'normal',
        details TEXT,
        source_path TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
      );

      CREATE TABLE IF NOT EXISTS ingestion_runs (
        id TEXT PRIMARY KEY,
        started_at TEXT DEFAULT (datetime('now')),
        finished_at TEXT,
        status TEXT DEFAULT 'running',
        notes TEXT
      );

      CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
        id UNINDEXED,
        title,
        content,
        source_path,
        category,
        tags
      );

      CREATE INDEX IF NOT EXISTS idx_memory_scope_category ON memory_items(scope, category);
      CREATE INDEX IF NOT EXISTS idx_memory_pinned ON memory_items(is_pinned, updated_at);
      CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status, priority);
    `);

    if (!(await this.index.isIndexCreated())) {
      await this.index.createIndex();
    }
  }

  tokenize(text) {
    return (text || '')
      .toLowerCase()
      .replace(/[^\p{L}\p{N}\s]+/gu, ' ')
      .split(/\s+/)
      .filter(Boolean);
  }

  async embed(text) {
    const vector = new Array(EMBEDDING_DIM).fill(0);
    const tokens = this.tokenize(text);
    if (tokens.length === 0) return vector;

    for (const token of tokens) {
      const hash = sha256(token);
      for (let i = 0; i < 8; i += 1) {
        const slice = hash.slice(i * 8, (i + 1) * 8);
        const bucket = parseInt(slice, 16) % EMBEDDING_DIM;
        vector[bucket] += 1;
      }
    }

    const norm = Math.sqrt(vector.reduce((sum, value) => sum + value * value, 0)) || 1;
    return vector.map((value) => value / norm);
  }

  upsertMemoryItem(item) {
    const stmt = this.db.prepare(`
      INSERT INTO memory_items (
        id, scope, category, title, content, source_path, source_ref, tags_json,
        confidence, is_pinned, valid_from, valid_to, content_hash, updated_at
      ) VALUES (
        @id, @scope, @category, @title, @content, @source_path, @source_ref, @tags_json,
        @confidence, @is_pinned, COALESCE(@valid_from, datetime('now')), @valid_to, @content_hash, datetime('now')
      )
      ON CONFLICT(content_hash) DO UPDATE SET
        scope = excluded.scope,
        category = excluded.category,
        title = excluded.title,
        content = excluded.content,
        source_path = excluded.source_path,
        source_ref = excluded.source_ref,
        tags_json = excluded.tags_json,
        confidence = excluded.confidence,
        is_pinned = excluded.is_pinned,
        valid_to = excluded.valid_to,
        updated_at = datetime('now')
    `);
    stmt.run(item);

    this.db.prepare('DELETE FROM memory_fts WHERE id = ?').run(item.id);
    this.db.prepare(`
      INSERT INTO memory_fts (id, title, content, source_path, category, tags)
      VALUES (?, ?, ?, ?, ?, ?)
    `).run(
      item.id,
      item.title || '',
      item.content,
      item.source_path || '',
      item.category,
      item.tags_json || '[]'
    );
  }

  upsertDecision({ topic, decision, rationale = null, source_path = null }) {
    const id = sha256(`decision:${topic}:${decision}`).slice(0, 32);
    const stmt = this.db.prepare(`
      INSERT INTO decisions (id, topic, decision, rationale, source_path, updated_at)
      VALUES (?, ?, ?, ?, ?, datetime('now'))
      ON CONFLICT(id) DO UPDATE SET
        rationale = excluded.rationale,
        source_path = excluded.source_path,
        updated_at = datetime('now')
    `);
    stmt.run(id, topic, decision, rationale, source_path);
  }

  upsertProjectFact({ project, fact_key, fact_value, unit = null, source_path = null }) {
    const id = sha256(`fact:${project}:${fact_key}`).slice(0, 32);
    const stmt = this.db.prepare(`
      INSERT INTO project_facts (id, project, fact_key, fact_value, unit, source_path, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
      ON CONFLICT(project, fact_key) DO UPDATE SET
        fact_value = excluded.fact_value,
        unit = excluded.unit,
        source_path = excluded.source_path,
        updated_at = datetime('now')
    `);
    stmt.run(id, project, fact_key, fact_value, unit, source_path);
  }

  upsertTask({ title, details = null, priority = 'normal', status = 'open', source_path = null }) {
    const id = sha256(`task:${title}`).slice(0, 32);
    const stmt = this.db.prepare(`
      INSERT INTO tasks (id, title, status, priority, details, source_path, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
      ON CONFLICT(id) DO UPDATE SET
        status = excluded.status,
        priority = excluded.priority,
        details = excluded.details,
        source_path = excluded.source_path,
        updated_at = datetime('now')
    `);
    stmt.run(id, title, status, priority, details, source_path);
  }

  async addSemanticChunk({ sourcePath, title, content, scope = 'workspace', category = 'note', tags = [], pinned = false, sourceRef = null, confidence = 1.0 }) {
    const text = content.trim();
    if (!text) return null;
    const contentHash = sha256(text);
    const id = contentHash.slice(0, 32);

    this.upsertMemoryItem({
      id,
      scope,
      category,
      title,
      content: text,
      source_path: sourcePath,
      source_ref: sourceRef,
      tags_json: JSON.stringify(tags),
      confidence,
      is_pinned: pinned ? 1 : 0,
      valid_from: null,
      valid_to: null,
      content_hash: contentHash,
    });

    const existing = await this.index.listItemsByMetadata({ memoryId: id });
    for (const item of existing) {
      await this.index.deleteItem(item.id);
    }

    const vector = await this.embed(text);
    await this.index.insertItem({
      vector,
      metadata: {
        memoryId: id,
        title,
        sourcePath,
        category,
        scope,
        tags,
        preview: text.slice(0, 280),
      },
    });

    return id;
  }

  async ingestMarkdownFile(sourcePath, options = {}) {
    const absPath = path.resolve(sourcePath);
    const raw = fs.readFileSync(absPath, 'utf8');
    const relativePath = path.relative(ROOT, absPath) || absPath;
    const chunks = splitIntoChunks(raw, options.maxChars || 1200);
    const category = options.category || inferCategory(relativePath, raw);
    const scope = options.scope || 'workspace';
    const tags = options.tags || [];
    const title = path.basename(absPath);

    for (let i = 0; i < chunks.length; i += 1) {
      const chunk = chunks[i];
      await this.addSemanticChunk({
        sourcePath: relativePath,
        title: `${title}#${i + 1}`,
        content: chunk,
        scope,
        category,
        tags,
        pinned: /hot_memory|memory\.md|identity|user|soul/i.test(relativePath),
        sourceRef: `chunk:${i + 1}`,
      });
    }

    this.extractStructuredFacts(relativePath, raw);
    return { sourcePath: relativePath, chunks: chunks.length, category };
  }

  extractStructuredFacts(sourcePath, raw) {
    const lines = raw.split(/\r?\n/).map(x => x.trim()).filter(Boolean);
    const project = '铁路线路智能检测机器人';

    for (const line of lines) {
      if (line.includes('速度') && /3\s*km\/h/.test(line)) {
        this.upsertProjectFact({ project, fact_key: '运行速度', fact_value: '3', unit: 'km/h', source_path: sourcePath });
      }
      if (line.includes('每天运行') && /2\s*小时/.test(line)) {
        this.upsertProjectFact({ project, fact_key: '每日运行时长', fact_value: '2', unit: 'h', source_path: sourcePath });
      }
      if ((line.includes('轨面') || line.includes('轨头')) && /72\s*mm/.test(line)) {
        this.upsertProjectFact({ project, fact_key: '轨面工程宽度', fact_value: '72', unit: 'mm', source_path: sourcePath });
      }
      if (line.includes('垂直朝下')) {
        this.upsertDecision({ topic: '相机与线激光安装视角', decision: '统一按垂直朝下处理', rationale: line, source_path: sourcePath });
      }
      if (line.includes('边处理边展示过程') || line.includes('边处理边汇报')) {
        this.upsertDecision({ topic: '协作方式', decision: '边处理边展示过程', rationale: line, source_path: sourcePath });
      }
      if (/\[ \]/.test(line) || /^- \[ \]/.test(line) || /^- \[x\]/i.test(line)) {
        this.upsertTask({ title: line.replace(/^-\s*/, ''), details: line, source_path: sourcePath, status: /\[x\]/i.test(line) ? 'done' : 'open' });
      }
    }
  }

  async search(query, limit = 8) {
    const vector = await this.embed(query);
    const semanticResults = await this.index.queryItems(vector, limit * 2);
    const memoryLookup = this.db.prepare(`SELECT * FROM memory_items WHERE id = ?`);
    const lexicalRows = this.db.prepare(`
      SELECT mi.*, bm25(memory_fts) AS rank
      FROM memory_fts
      JOIN memory_items mi ON mi.id = memory_fts.id
      WHERE memory_fts MATCH ?
      ORDER BY rank
      LIMIT ?
    `).all(query.replace(/"/g, ' '), limit * 2);

    const merged = new Map();

    for (const row of lexicalRows) {
      merged.set(row.id, {
        score: 1 / (1 + Math.max(0, row.rank || 0)),
        title: row.title,
        category: row.category,
        source_path: row.source_path,
        content: row.content,
      });
    }

    for (const result of semanticResults) {
      const row = memoryLookup.get(result.item.metadata.memoryId);
      const id = row?.id || result.item.metadata.memoryId;
      const existing = merged.get(id);
      const candidate = {
        score: result.score,
        title: row?.title || result.item.metadata.title,
        category: row?.category || result.item.metadata.category,
        source_path: row?.source_path || result.item.metadata.sourcePath,
        content: row?.content || result.item.metadata.preview,
      };
      if (!existing || candidate.score > existing.score) {
        merged.set(id, candidate);
      }
    }

    return Array.from(merged.values())
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);
  }

  getPinnedFacts(limit = 20) {
    return this.db.prepare(`
      SELECT category, title, source_path, substr(content, 1, 240) AS preview, updated_at
      FROM memory_items
      WHERE is_pinned = 1
      ORDER BY updated_at DESC
      LIMIT ?
    `).all(limit);
  }

  getProjectFacts(project = '铁路线路智能检测机器人') {
    return this.db.prepare(`
      SELECT fact_key, fact_value, unit, source_path, updated_at
      FROM project_facts
      WHERE project = ?
      ORDER BY fact_key
    `).all(project);
  }

  close() {
    this.db.close();
  }
}

module.exports = {
  MemorySystem,
  ROOT,
  BASE_DIR,
  DB_PATH,
  INDEX_PATH,
  MODEL_CACHE_DIR,
  sha256,
};
