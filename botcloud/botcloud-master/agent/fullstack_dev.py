#!/usr/bin/env python3
"""
Full Stack Developer Worker
Can create websites, APIs, databases, files, and more
"""

import sys
import os
import subprocess
import shutil
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent import BotCloudAgent

WORKSPACE = "/home/openryanclaw/botcloud/workspace"

def ensure_workspace():
    """Ensure workspace exists"""
    os.makedirs(WORKSPACE, exist_ok=True)

def create_html_page(title, content):
    """Create a simple HTML page"""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>""" + title + """</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>""" + title + """</h1>
    <div>""" + content + """</div>
</body>
</html>"""
    return html

def create_react_component(name):
    """Create a React component"""
    return """import React from 'react';

export function """ + name + """() {
    return (
        <div className='""" + name.lower() + """'>
            <h2>""" + name + """</h2>
        </div>
    );
}

export default """ + name + """;"""

def create_python_api():
    """Create a Python Flask API"""
    return """from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/data', methods=['GET', 'POST'])
def data():
    if request.method == 'POST':
        return jsonify({"received": request.json})
    return jsonify({"data": []})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
"""

def create_nodejs_server():
    """Create a Node.js Express server"""
    return """const express = require('express');
const app = express();
const PORT = 3000;

app.use(express.json());

app.get('/api/health', (req, res) => {
    res.json({ status: 'ok' });
});

app.post('/api/data', (req, res) => {
    res.json({ received: req.body });
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
"""

def create_database_schema():
    """Create a SQL database schema"""
    return """-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Posts table
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Comments table
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id),
    user_id INTEGER REFERENCES users(id),
    body TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);"""

def write_file(filename, content):
    """Write content to a file"""
    ensure_workspace()
    filepath = os.path.join(WORKSPACE, filename)
    
    # Create directories if needed
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    return filepath

def read_file(filename):
    """Read content from a file"""
    filepath = os.path.join(WORKSPACE, filename)
    
    if not os.path.exists(filepath):
        return f"File not found: {filename}"
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    return content

def create_directory(dirname):
    """Create a directory"""
    ensure_workspace()
    dirpath = os.path.join(WORKSPACE, dirname)
    os.makedirs(dirpath, exist_ok=True)
    return f"Created directory: {dirname}/"

def list_files(dirname=""):
    """List files in directory"""
    dirpath = os.path.join(WORKSPACE, dirname) if dirname else WORKSPACE
    
    if not os.path.exists(dirpath):
        return f"Directory not found: {dirname}"
    
    files = []
    for item in os.listdir(dirpath):
        full_path = os.path.join(dirpath, item)
        if os.path.isdir(full_path):
            files.append(item + "/")
        else:
            files.append(item)
    
    return "\n".join(files) if files else "Empty directory"

def copy_file(source, dest):
    """Copy a file"""
    src = os.path.join(WORKSPACE, source)
    dst = os.path.join(WORKSPACE, dest)
    
    if not os.path.exists(src):
        return f"Source not found: {source}"
    
    shutil.copy2(src, dst)
    return f"Copied {source} to {dest}"

def delete_file(filename):
    """Delete a file or directory"""
    filepath = os.path.join(WORKSPACE, filename)
    
    if not os.path.exists(filepath):
        return f"File not found: {filename}"
    
    if os.path.isdir(filepath):
        shutil.rmtree(filepath)
        return f"Deleted directory: {filename}"
    else:
        os.remove(filepath)
        return f"Deleted file: {filename}"

def process_task(task_input):
    """Process developer tasks"""
    task = task_input.lower()
    
    # Write file
    if task.startswith("write ") or task.startswith("save "):
        # Format: "write filename content" or "save file.py code"
        parts = task_input.split(None, 2)
        if len(parts) >= 3:
            filename = parts[1]
            content = parts[2]
            filepath = write_file(filename, content)
            return f"Wrote to {filepath}\n\nContent:\n{content}"
        return "Format: write <filename> <content>"
    
    # Read file
    if task.startswith("read ") or task.startswith("show "):
        parts = task_input.split(None, 1)
        if len(parts) >= 2:
            filename = parts[1]
            return read_file(filename)
        return "Format: read <filename>"
    
    # Create directory
    if task.startswith("mkdir ") or "create directory" in task:
        parts = task_input.split()
        for i, p in enumerate(parts):
            if p == "mkdir" or p == "directory":
                if i+1 < len(parts):
                    return create_directory(parts[i+1])
        return "Format: mkdir <directoryname>"
    
    # List files
    if "list files" in task or "ls " in task or "show files" in task:
        parts = task_input.split()
        dirname = ""
        for i, p in enumerate(parts):
            if p in ["ls", "list", "show"] and i+1 < len(parts):
                dirname = parts[i+1]
                break
        return list_files(dirname)
    
    # Copy file
    if task.startswith("copy ") or task.startswith("cp "):
        parts = task.split()
        if len(parts) >= 3:
            return copy_file(parts[1], parts[2])
        return "Format: copy <source> <dest>"
    
    # Delete file
    if task.startswith("delete ") or task.startswith("rm "):
        parts = task.split()
        if len(parts) >= 2:
            return delete_file(parts[1])
        return "Format: delete <filename>"
    
    # Create HTML page
    if "html" in task or "website" in task or "web page" in task:
        title = "My Website"
        content = "Welcome to my new website!"
        return "Here's an HTML page:\n\n" + create_html_page(title, content)
    
    # Create React component
    if "react" in task or "component" in task:
        name = "MyComponent"
        return "Here's a React component:\n\n" + create_react_component(name)
    
    # Create Python API
    if "python api" in task or "flask" in task or "backend python" in task:
        return "Here's a Flask API:\n\n" + create_python_api()
    
    # Create Node.js server
    if "node" in task or "express" in task or "javascript api" in task or "backend" in task:
        return "Here's an Express.js server:\n\n" + create_nodejs_server()
    
    # Create database schema
    if "database" in task or "schema" in task or "sql" in task:
        return "Here's a SQL schema:\n\n" + create_database_schema()
    
    # Help
    return """FullStack Developer - Commands:

FILE OPERATIONS:
- write <filename> <content> - Write file
- read <filename> - Read file
- mkdir <dirname> - Create directory
- ls or list files - List all files
- copy <source> <dest> - Copy file
- delete <filename> - Delete file/directory

CREATE PROJECTS:
- create html website
- create react component
- create python flask api
- create express api
- create database schema

What would you like me to do?"""

# Create the agent
agent = BotCloudAgent(
    name="FullStackDev",
    api_url="http://localhost:8001",
    capabilities=["code", "develop", "web", "api", "fullstack", "create", "write", "read", "file"]
)

@agent.task("write")
@agent.task("save")
def write_handler(task_input):
    return process_task(task_input)

@agent.task("read")
def read_handler(task_input):
    return process_task(task_input)

@agent.task("mkdir")
@agent.task("directory")
def dir_handler(task_input):
    return process_task(task_input)

@agent.task("ls")
@agent.task("list")
def list_handler(task_input):
    return process_task(task_input)

@agent.task("copy")
@agent.task("cp")
def copy_handler(task_input):
    return process_task(task_input)

@agent.task("delete")
@agent.task("rm")
def delete_handler(task_input):
    return process_task(task_input)

@agent.task("create")
@agent.task("build")
def create_handler(task_input):
    return process_task(task_input)

@agent.task("default")
def default_handler(task_input):
    return process_task(task_input)

print("FullStack Developer starting...")
print("File operations + project creation!")
agent.start()
print(f"Registered as: {agent.agent_id}")
print(f"Workspace: {WORKSPACE}")
print("\nWaiting for tasks...")

try:
    import time
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    agent.stop()
