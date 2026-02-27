#!/usr/bin/env python3
"""
BotCloud Database Layer
Supports SQLite (local) and PostgreSQL (production)
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod


class Database(ABC):
    """Abstract database interface"""
    
    @abstractmethod
    def init_schema(self):
        pass
    
    @abstractmethod
    def create_agent(self, name: str, capabilities: List[str], api_key: str) -> Dict:
        pass
    
    @abstractmethod
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        pass
    
    @abstractmethod
    def list_agents(self) -> List[Dict]:
        pass
    
    @abstractmethod
    def create_task(self, agent_id: str, input_data: str) -> Dict:
        pass
    
    @abstractmethod
    def get_task(self, task_id: str) -> Optional[Dict]:
        pass
    
    @abstractmethod
    def list_tasks(self, agent_id: str = None) -> List[Dict]:
        pass
    
    @abstractmethod
    def complete_task(self, task_id: str, output: str, status: str = "completed"):
        pass
    
    @abstractmethod
    def store_memory(self, agent_id: str, key: str, value: str) -> Dict:
        pass
    
    @abstractmethod
    def get_memories(self, agent_id: str) -> List[Dict]:
        pass
    
    @abstractmethod
    def search_memories(self, agent_id: str, query: str) -> List[Dict]:
        """Hybrid search - keyword + semantic"""
        pass


class SQLiteDB(Database):
    """SQLite implementation for local storage"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.expanduser("~/botcloud/data/botcloud.db")
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_schema()
    
    def init_schema(self):
        """Initialize database schema"""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                capabilities TEXT,
                status TEXT DEFAULT 'stopped',
                config TEXT,
                api_key TEXT,
                created_at TEXT,
                last_active TEXT
            );
            
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                input TEXT,
                output TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                completed_at TEXT,
                FOREIGN KEY (agent_id) REFERENCES agents(id)
            );
            
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                created_at TEXT,
                FOREIGN KEY (agent_id) REFERENCES agents(id)
            );
            
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                from_agent_id TEXT,
                to_agent_id TEXT,
                content TEXT,
                created_at TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_tasks_agent ON tasks(agent_id);
            CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
            CREATE INDEX IF NOT EXISTS idx_memories_agent ON memories(agent_id);
            CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key);
            CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
                agent_id, key, value, content='memories', content_rowid='id'
            );
        """)
        self.conn.commit()
    
    def create_agent(self, name: str, capabilities: List[str], api_key: str) -> Dict:
        import uuid
        agent_id = f"agent_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()
        
        self.conn.execute("""
            INSERT INTO agents (id, name, capabilities, status, api_key, created_at, last_active)
            VALUES (?, ?, ?, 'stopped', ?, ?, ?)
        """, (agent_id, name, json.dumps(capabilities), api_key, now, now))
        self.conn.commit()
        
        return {
            "id": agent_id,
            "name": name,
            "capabilities": capabilities,
            "api_key": api_key,
            "created_at": now
        }
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        row = self.conn.execute(
            "SELECT * FROM agents WHERE id = ?", (agent_id,)
        ).fetchone()
        
        if row:
            return dict(row)
        return None
    
    def list_agents(self) -> List[Dict]:
        rows = self.conn.execute("SELECT * FROM agents").fetchall()
        return [dict(r) for r in rows]
    
    def create_task(self, agent_id: str, input_data: str) -> Dict:
        import uuid
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()
        
        self.conn.execute("""
            INSERT INTO tasks (id, agent_id, input, status, created_at)
            VALUES (?, ?, ?, 'pending', ?)
        """, (task_id, agent_id, input_data, now))
        self.conn.commit()
        
        return {
            "id": task_id,
            "agent_id": agent_id,
            "input": input_data,
            "status": "pending",
            "created_at": now
        }
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        row = self.conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        
        if row:
            return dict(row)
        return None
    
    def list_tasks(self, agent_id: str = None) -> List[Dict]:
        if agent_id:
            rows = self.conn.execute(
                "SELECT * FROM tasks WHERE agent_id = ? ORDER BY created_at DESC", 
                (agent_id,)
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM tasks ORDER BY created_at DESC"
            ).fetchall()
        
        return [dict(r) for r in rows]
    
    def complete_task(self, task_id: str, output: str, status: str = "completed"):
        now = datetime.utcnow().isoformat()
        self.conn.execute("""
            UPDATE tasks SET output = ?, status = ?, completed_at = ?
            WHERE id = ?
        """, (output, status, now, task_id))
        self.conn.commit()
    
    def store_memory(self, agent_id: str, key: str, value: str) -> Dict:
        now = datetime.utcnow().isoformat()
        
        # Delete existing key
        self.conn.execute(
            "DELETE FROM memories WHERE agent_id = ? AND key = ?",
            (agent_id, key)
        )
        
        self.conn.execute("""
            INSERT INTO memories (agent_id, key, value, created_at)
            VALUES (?, ?, ?, ?)
        """, (agent_id, key, value, now))
        self.conn.commit()
        
        return {"key": key, "value": value, "created_at": now}
    
    def get_memories(self, agent_id: str) -> List[Dict]:
        rows = self.conn.execute(
            "SELECT * FROM memories WHERE agent_id = ? ORDER BY created_at DESC",
            (agent_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    
    def search_memories(self, agent_id: str, query: str) -> List[Dict]:
        """Hybrid search: keyword match + FTS"""
        if not query:
            return self.get_memories(agent_id)
        
        # Try FTS first
        try:
            rows = self.conn.execute("""
                SELECT m.* FROM memories m
                JOIN memories_fts fts ON m.id = fts.rowid
                WHERE memories_fts MATCH ? AND m.agent_id = ?
                ORDER BY rank
            """, (query, agent_id)).fetchall()
            
            if rows:
                return [dict(r) for r in rows]
        except:
            pass
        
        # Fallback: LIKE search
        rows = self.conn.execute("""
            SELECT * FROM memories 
            WHERE agent_id = ? AND (key LIKE ? OR value LIKE ?)
            ORDER BY created_at DESC
        """, (agent_id, f"%{query}%", f"%{query}%")).fetchall()
        
        return [dict(r) for r in rows]
    
    def close(self):
        self.conn.close()


class PostgresDB(Database):
    """PostgreSQL implementation for production"""
    
    def __init__(self, connection_string: str = None):
        if connection_string is None:
            connection_string = os.environ.get(
                "DATABASE_URL", 
                "postgresql://localhost/botcloud"
            )
        
        import psycopg2
        self.conn = psycopg2.connect(connection_string)
        self.conn.autocommit = True
        self.init_schema()
    
    def init_schema(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    capabilities JSONB,
                    status TEXT DEFAULT 'stopped',
                    config JSONB,
                    api_key TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    last_active TIMESTAMP
                )
            """)
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT REFERENCES agents(id),
                    input TEXT,
                    output TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT NOW(),
                    completed_at TIMESTAMP
                )
            """)
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id SERIAL PRIMARY KEY,
                    agent_id TEXT REFERENCES agents(id),
                    key TEXT NOT NULL,
                    value TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create GIN index for full-text search
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_memories_fts 
                ON memories USING GIN(to_tsvector('english', key || ' ' || value))
            """)
    
    def create_agent(self, name: str, capabilities: List[str], api_key: str) -> Dict:
        import uuid
        import json
        agent_id = f"agent_{uuid.uuid4().hex[:8]}"
        
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO agents (id, name, capabilities, api_key)
                VALUES (%s, %s, %s, %s)
                RETURNING *
            """, (agent_id, name, json.dumps(capabilities), api_key))
            
            row = cur.fetchone()
            return {
                "id": row[0],
                "name": row[1],
                "capabilities": json.loads(row[2]) if row[2] else [],
                "api_key": row[5]
            }
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM agents WHERE id = %s", (agent_id,))
            row = cur.fetchone()
            if row:
                return {"id": row[0], "name": row[1], "capabilities": row[2], "status": row[3]}
            return None
    
    def list_agents(self) -> List[Dict]:
        with self.conn.cursor() as cur:
            cur.execute("SELECT id, name, capabilities, status FROM agents")
            return [{"id": r[0], "name": r[1], "capabilities": r[2], "status": r[3]} for r in cur.fetchall()]
    
    def create_task(self, agent_id: str, input_data: str) -> Dict:
        import uuid
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tasks (id, agent_id, input)
                VALUES (%s, %s, %s)
                RETURNING *
            """, (task_id, agent_id, input_data))
            
            return {"id": task_id, "agent_id": agent_id, "input": input_data, "status": "pending"}
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            row = cur.fetchone()
            if row:
                return {"id": row[0], "agent_id": row[1], "input": row[2], "output": row[3], "status": row[4]}
            return None
    
    def list_tasks(self, agent_id: str = None) -> List[Dict]:
        with self.conn.cursor() as cur:
            if agent_id:
                cur.execute("SELECT * FROM tasks WHERE agent_id = %s ORDER BY created_at DESC", (agent_id,))
            else:
                cur.execute("SELECT * FROM tasks ORDER BY created_at DESC")
            
            return [{"id": r[0], "agent_id": r[1], "input": r[2], "output": r[3], "status": r[4]} for r in cur.fetchall()]
    
    def complete_task(self, task_id: str, output: str, status: str = "completed"):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE tasks SET output = %s, status = %s, completed_at = NOW()
                WHERE id = %s
            """, (output, status, task_id))
    
    def store_memory(self, agent_id: str, key: str, value: str) -> Dict:
        with self.conn.cursor() as cur:
            # Delete existing
            cur.execute("DELETE FROM memories WHERE agent_id = %s AND key = %s", (agent_id, key))
            
            cur.execute("""
                INSERT INTO memories (agent_id, key, value)
                VALUES (%s, %s, %s)
                RETURNING *
            """, (agent_id, key, value))
            
            return {"key": key, "value": value}
    
    def get_memories(self, agent_id: str) -> List[Dict]:
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM memories WHERE agent_id = %s ORDER BY created_at DESC", (agent_id,))
            return [{"id": r[0], "key": r[2], "value": r[3]} for r in cur.fetchall()]
    
    def search_memories(self, agent_id: str, query: str) -> List[Dict]:
        """Full-text search using PostgreSQL"""
        if not query:
            return self.get_memories(agent_id)
        
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM memories
                WHERE agent_id = %s AND to_tsvector('english', key || ' ' || value) @@ plainto_tsquery('english', %s)
                ORDER BY created_at DESC
            """, (agent_id, query))
            
            return [{"id": r[0], "key": r[2], "value": r[3]} for r in cur.fetchall()]
    
    def close(self):
        self.conn.close()


def get_database(db_type: str = None) -> Database:
    """Factory function to get database instance"""
    if db_type is None:
        db_type = os.environ.get("BOTCLOUD_DB", "sqlite")
    
    if db_type == "postgres" or db_type == "postgresql":
        return PostgresDB()
    else:
        return SQLiteDB()


if __name__ == "__main__":
    # Test
    db = get_database("sqlite")
    
    # Create agent
    agent = db.create_agent("test-bot", ["chat", "search"], "key123")
    print(f"Created: {agent}")
    
    # Create task
    task = db.create_task(agent["id"], "Hello world")
    print(f"Task: {task}")
    
    # Complete task
    db.complete_task(task["id"], "Processed!")
    print(f"Completed: {db.get_task(task['id'])}")
    
    # Store memory
    db.store_memory(agent["id"], "context", "User likes AI")
    print(f"Memories: {db.get_memories(agent['id'])}")
    
    # Search memories
    print(f"Search 'AI': {db.search_memories(agent['id'], 'AI')}")
    
    db.close()
