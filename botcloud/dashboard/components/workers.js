/**
 * Workers Panel Component
 */

class WorkersPanel {
    constructor(container) {
        this.container = container;
        this.workers = [];
        this.render();
        this.startPolling();
    }
    
    async load() {
        try {
            const data = await api.listAgents();
            this.workers = data.agents || [];
            this.render();
        } catch (e) {
            console.error('Failed to load workers:', e);
        }
    }
    
    async spawnWorker() {
        const name = 'worker-' + Date.now().toString(36);
        try {
            await api.createAgent(name, ['general']);
            showToast('Worker spawned');
            this.load();
        } catch (e) {
            showToast('Failed to spawn worker: ' + e.message, 'error');
        }
    }
    
    render() {
        const running = this.workers.filter(w => w.status === 'running').length;
        
        this.container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Workers (${this.workers.length})</span>
                    <button class="btn btn-primary btn-small" id="spawn-worker">
                        + Spawn Worker
                    </button>
                </div>
                
                ${this.workers.length === 0 ? 
                    '<div class="empty-state">No workers</div>' : 
                    `<table class="table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>ID</th>
                                <th>Status</th>
                                <th>Capabilities</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${this.workers.map(w => `
                                <tr>
                                    <td><strong>${w.name}</strong></td>
                                    <td style="color: var(--text-muted); font-size: 0.8rem;">${w.id}</td>
                                    <td>
                                        <span class="badge ${w.status === 'running' ? 'badge-success' : 'badge-warning'}">
                                            ${w.status}
                                        </span>
                                    </td>
                                    <td>${(w.capabilities || []).join(', ') || '-'}</td>
                                    <td>
                                        <button class="btn btn-secondary btn-small" onclick="workersPanel.testWorker('${w.id}')">
                                            Test
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>`
                }
            </div>
        `;
        
        document.getElementById('spawn-worker')?.addEventListener('click', () => this.spawnWorker());
    }
    
    async testWorker(workerId) {
        try {
            const result = await api.createTask(workerId, 'exec echo test-' + Date.now());
            showToast('Task sent to worker');
        } catch (e) {
            showToast('Failed: ' + e.message, 'error');
        }
    }
    
    startPolling() {
        this.load();
        setInterval(() => this.load(), 3000);
    }
}

// Make globally available
if (typeof window !== 'undefined') {
    window.WorkersPanel = WorkersPanel;
}
