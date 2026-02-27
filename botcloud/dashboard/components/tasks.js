/**
 * Tasks Panel Component
 */

class TasksPanel {
    constructor(container) {
        this.container = container;
        this.tasks = [];
        this.render();
        this.startPolling();
    }
    
    async load() {
        try {
            const data = await api.listTasks();
            this.tasks = data.tasks || [];
            this.render();
        } catch (e) {
            console.error('Failed to load tasks:', e);
        }
    }
    
    render() {
        const pending = this.tasks.filter(t => t.status === 'pending').length;
        const completed = this.tasks.filter(t => t.status === 'completed').length;
        
        this.container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Task Queue (${this.tasks.length})</span>
                    <button class="btn btn-secondary btn-small" id="refresh-tasks">
                        ⟳ Refresh
                    </button>
                </div>
                
                <div class="stats-grid" style="margin-bottom: 15px;">
                    <div class="stat-card">
                        <div class="stat-value" style="color: var(--accent-orange);">${pending}</div>
                        <div class="stat-label">Pending</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" style="color: var(--accent-green);">${completed}</div>
                        <div class="stat-label">Completed</div>
                    </div>
                </div>
                
                ${this.tasks.length === 0 ? 
                    '<div class="empty-state">No tasks</div>' : 
                    `<table class="table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Worker</th>
                                <th>Input</th>
                                <th>Output</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${this.tasks.slice(0, 20).map(t => `
                                <tr>
                                    <td style="font-family: var(--font-mono); font-size: 0.8rem;">${t.id}</td>
                                    <td>${t.agent_id}</td>
                                    <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis;">${t.input || '-'}</td>
                                    <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; color: var(--text-muted);">
                                        ${t.output ? t.output.substring(0, 50) + '...' : '-'}
                                    </td>
                                    <td>
                                        <span class="badge ${t.status === 'completed' ? 'badge-success' : t.status === 'pending' ? 'badge-warning' : 'badge-error'}">
                                            ${t.status}
                                        </span>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                    ${this.tasks.length > 20 ? `<div style="text-align: center; padding: 10px; color: var(--text-muted);">Showing 20 of ${this.tasks.length} tasks</div>` : ''}
                `}
            </div>
        `;
        
        document.getElementById('refresh-tasks')?.addEventListener('click', () => this.load());
    }
    
    startPolling() {
        this.load();
        setInterval(() => this.load(), 3000);
    }
}

if (typeof window !== 'undefined') {
    window.TasksPanel = TasksPanel;
}
