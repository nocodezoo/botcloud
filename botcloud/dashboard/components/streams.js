/**
 * Streams Panel Component - WebSocket Visualization
 */

class StreamsPanel {
    constructor(container) {
        this.container = container;
        this.streams = [];
        this.activeConnections = [];
        this.render();
        this.startPolling();
    }
    
    async load() {
        try {
            const data = await api.listStreams();
            this.streams = data.streams || [];
            this.render();
        } catch (e) {
            console.error('Failed to load streams:', e);
        }
    }
    
    connectToTask(taskId) {
        if (this.activeConnections.includes(taskId)) {
            showToast('Already connected to ' + taskId);
            return;
        }
        
        try {
            const ws = new WebSocket(`ws://localhost:8000/ws/task/${taskId}`);
            
            ws.onopen = () => {
                showToast('Connected to ' + taskId);
                this.activeConnections.push(taskId);
                this.render();
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.addStreamMessage(taskId, data);
            };
            
            ws.onclose = () => {
                this.activeConnections = this.activeConnections.filter(id => id !== taskId);
                showToast('Disconnected from ' + taskId);
                this.render();
            };
            
            ws.onerror = (e) => {
                showToast('WS Error: ' + e.message, 'error');
            };
            
        } catch (e) {
            showToast('Failed to connect: ' + e.message, 'error');
        }
    }
    
    addStreamMessage(taskId, data) {
        const container = document.getElementById(`stream-messages-${taskId}`);
        if (!container) return;
        
        const msg = document.createElement('div');
        msg.style.cssText = 'padding: 5px 10px; border-bottom: 1px solid var(--border); font-family: var(--font-mono); font-size: 0.85rem;';
        msg.textContent = `[${new Date().toLocaleTimeString()}] ${JSON.stringify(data)}`;
        container.appendChild(msg);
        container.scrollTop = container.scrollHeight;
    }
    
    render() {
        this.container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <span class="card-title">WebSocket Streams</span>
                    <button class="btn btn-secondary btn-small" id="refresh-streams">
                        ⟳ Refresh
                    </button>
                </div>
                
                <div class="input-group">
                    <input type="text" class="input" id="stream-task-id" placeholder="Task ID" style="flex: 1;">
                    <button class="btn btn-primary btn-small" id="connect-stream">Connect</button>
                </div>
                
                <div style="margin-bottom: 15px; color: var(--text-secondary); font-size: 0.9rem;">
                    Active connections: ${this.activeConnections.length}
                </div>
                
                ${this.streams.length === 0 && this.activeConnections.length === 0 ? 
                    '<div class="empty-state">No active streams</div>' : 
                    `
                    <div style="display: grid; gap: 10px;">
                        ${this.streams.map(stream => `
                            <div style="background: var(--bg-tertiary); padding: 10px; border-radius: 6px;">
                                <strong>Task:</strong> ${stream}
                                ${this.activeConnections.includes(stream) ? 
                                    '<span class="badge badge-success">Connected</span>' : 
                                    `<button class="btn btn-secondary btn-small" onclick="streamsPanel.connectToTask('${stream}')">Connect</button>`
                                }
                            </div>
                        `).join('')}
                        
                        ${this.activeConnections.map(taskId => `
                            <div style="background: var(--bg-tertiary); padding: 10px; border-radius: 6px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                                    <strong>Live: ${taskId}</strong>
                                    <span class="badge badge-success">Connected</span>
                                </div>
                                <div id="stream-messages-${taskId}" style="max-height: 200px; overflow-y: auto; background: var(--bg-primary); padding: 10px; border-radius: 4px; font-family: var(--font-mono); font-size: 0.8rem;">
                                    <div style="color: var(--text-muted);">Waiting for messages...</div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    `
                }
            </div>
        `;
        
        document.getElementById('refresh-streams')?.addEventListener('click', () => this.load());
        document.getElementById('connect-stream')?.addEventListener('click', () => {
            const taskId = document.getElementById('stream-task-id').value;
            if (taskId) this.connectToTask(taskId);
        });
    }
    
    startPolling() {
        this.load();
        setInterval(() => this.load(), 3000);
    }
}

if (typeof window !== 'undefined') {
    window.StreamsPanel = StreamsPanel;
}
