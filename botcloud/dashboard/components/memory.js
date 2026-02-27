/**
 * Shared Memory Panel Component
 */

class MemoryPanel {
    constructor(container) {
        this.container = container;
        this.memory = [];
        this.render();
        this.startPolling();
    }
    
    async load() {
        try {
            const data = await api.sharedList();
            this.memory = data.shared || [];
            this.render();
        } catch (e) {
            console.error('Failed to load memory:', e);
        }
    }
    
    async setValue(key, value) {
        try {
            await api.sharedSet(key, value);
            showToast('Value set');
            this.load();
        } catch (e) {
            showToast('Failed: ' + e.message, 'error');
        }
    }
    
    async increment(key, delta = 1) {
        try {
            const result = await api.sharedIncr(key, delta);
            showToast(`Counter: ${result.counter}`);
            this.load();
        } catch (e) {
            showToast('Failed: ' + e.message, 'error');
        }
    }
    
    async deleteKey(key) {
        try {
            await api.sharedDelete(key);
            showToast('Deleted');
            this.load();
        } catch (e) {
            showToast('Failed: ' + e.message, 'error');
        }
    }
    
    render() {
        this.container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Shared Memory (${this.memory.length})</span>
                    <button class="btn btn-secondary btn-small" id="refresh-memory">
                        ⟳ Refresh
                    </button>
                </div>
                
                <div class="input-group">
                    <input type="text" class="input" id="mem-key" placeholder="Key" style="width: 150px;">
                    <input type="text" class="input" id="mem-value" placeholder="Value" style="flex: 1;">
                    <button class="btn btn-primary btn-small" id="mem-set">Set</button>
                </div>
                
                <div class="input-group">
                    <input type="text" class="input" id="mem-key-incr" placeholder="Counter key" style="width: 150px;">
                    <input type="number" class="input" id="mem-delta" placeholder="Delta" value="1" style="width: 80px;">
                    <button class="btn btn-secondary btn-small" id="mem-incr">Increment</button>
                </div>
                
                ${this.memory.length === 0 ? 
                    '<div class="empty-state">No shared memory</div>' : 
                    `<table class="table">
                        <thead>
                            <tr>
                                <th>Key</th>
                                <th>Value</th>
                                <th>Counter</th>
                                <th>Updated</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${this.memory.map(m => `
                                <tr>
                                    <td><strong>${m.key}</strong></td>
                                    <td>${m.value || '-'}</td>
                                    <td style="color: var(--accent-orange);">${m.counter || 0}</td>
                                    <td style="color: var(--text-muted); font-size: 0.8rem;">${formatRelative(m.updated_at)}</td>
                                    <td>
                                        <button class="btn btn-danger btn-small" onclick="memoryPanel.deleteKey('${m.key}')">
                                            Delete
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>`
                }
            </div>
        `;
        
        // Event listeners
        document.getElementById('refresh-memory')?.addEventListener('click', () => this.load());
        document.getElementById('mem-set')?.addEventListener('click', () => {
            const key = document.getElementById('mem-key').value;
            const value = document.getElementById('mem-value').value;
            if (key) this.setValue(key, value);
        });
        document.getElementById('mem-incr')?.addEventListener('click', () => {
            const key = document.getElementById('mem-key-incr').value;
            const delta = parseInt(document.getElementById('mem-delta').value) || 1;
            if (key) this.increment(key, delta);
        });
    }
    
    startPolling() {
        this.load();
        setInterval(() => this.load(), 5000);
    }
}

if (typeof window !== 'undefined') {
    window.MemoryPanel = MemoryPanel;
}
