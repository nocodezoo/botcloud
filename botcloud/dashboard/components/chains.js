/**
 * Chains Panel Component - Task Chaining UI
 */

class ChainsPanel {
    constructor(container) {
        this.container = container;
        this.steps = [];
        this.render();
    }
    
    addStep() {
        this.steps.push({ worker: '', task: '' });
        this.render();
    }
    
    removeStep(index) {
        this.steps.splice(index, 1);
        this.render();
    }
    
    updateStep(index, field, value) {
        if (this.steps[index]) {
            this.steps[index][field] = value;
        }
    }
    
    async runChain() {
        if (this.steps.length === 0) {
            showToast('Add at least one step', 'error');
            return;
        }
        
        // Validate
        for (let i = 0; i < this.steps.length; i++) {
            if (!this.steps[i].worker || !this.steps[i].task) {
                showToast('Fill in all worker and task fields', 'error');
                return;
            }
        }
        
        showToast('Running chain...');
        
        const results = [];
        let previousOutput = null;
        
        for (let i = 0; i < this.steps.length; i++) {
            const step = this.steps[i];
            let task = step.task;
            
            // Replace {{result}} placeholder
            if (previousOutput && task.includes('{{result}}')) {
                task = task.replace('{{result}}', previousOutput);
            }
            
            try {
                // Get worker ID from name
                const agents = await api.listAgents();
                const worker = agents.agents.find(a => a.name === step.worker);
                
                if (!worker) {
                    throw new Error('Worker not found: ' + step.worker);
                }
                
                const result = await api.createTask(worker.id, task);
                results.push({ step: i, status: 'submitted', task: result });
                
                // Wait for completion (simple polling)
                for (let j = 0; j < 30; j++) {
                    await new Promise(r => setTimeout(r, 500));
                    const taskResult = await api.getTask(result.id);
                    if (taskResult.status === 'completed') {
                        previousOutput = taskResult.output;
                        results[i].status = 'completed';
                        results[i].output = taskResult.output;
                        break;
                    }
                    if (taskResult.status === 'failed') {
                        results[i].status = 'failed';
                        results[i].error = 'Task failed';
                        break;
                    }
                }
                
            } catch (e) {
                results.push({ step: i, status: 'error', error: e.message });
                showToast('Chain error: ' + e.message, 'error');
                break;
            }
        }
        
        this.results = results;
        this.render();
        showToast('Chain completed!');
    }
    
    render() {
        this.container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Task Chain Builder</span>
                    <div style="display: flex; gap: 10px;">
                        <button class="btn btn-secondary btn-small" id="add-step">
                            + Add Step
                        </button>
                        <button class="btn btn-primary btn-small" id="run-chain">
                            ▶ Run Chain
                        </button>
                    </div>
                </div>
                
                <div style="margin-bottom: 20px; color: var(--text-secondary); font-size: 0.9rem;">
                    <strong>Format:</strong> Use {{result}} to pass previous step's output to next step
                </div>
                
                <div id="chain-steps">
                    ${this.steps.length === 0 ? 
                        '<div class="empty-state">Click "+ Add Step" to build a chain</div>' :
                        this.steps.map((step, i) => `
                            <div class="input-group" style="margin-bottom: 10px;">
                                <span style="padding: 8px; background: var(--bg-tertiary); border-radius: 6px; min-width: 30px; text-align: center;">
                                    ${i + 1}
                                </span>
                                <input type="text" class="input" placeholder="Worker name (e.g., worker-0)" 
                                    value="${step.worker}" 
                                    onchange="chainsPanel.updateStep(${i}, 'worker', this.value)"
                                    style="width: 200px;">
                                <input type="text" class="input" placeholder="Task (use {{result}} for output)"
                                    value="${step.task}"
                                    onchange="chainsPanel.updateStep(${i}, 'task', this.value)"
                                    style="flex: 1;">
                                <button class="btn btn-danger btn-small" onclick="chainsPanel.removeStep(${i})">
                                    ✕
                                </button>
                            </div>
                        `).join('')
                    }
                </div>
                
                ${this.results ? `
                    <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid var(--border);">
                        <strong>Results:</strong>
                        ${this.results.map((r, i) => `
                            <div style="padding: 10px; background: var(--bg-tertiary); border-radius: 6px; margin-top: 10px;">
                                <div style="display: flex; justify-content: space-between;">
                                    <strong>Step ${i + 1}</strong>
                                    <span class="badge ${r.status === 'completed' ? 'badge-success' : r.status === 'failed' ? 'badge-error' : 'badge-warning'}">
                                        ${r.status}
                                    </span>
                                </div>
                                ${r.output ? `<div style="margin-top: 5px; font-family: var(--font-mono); font-size: 0.85rem;">${r.output}</div>` : ''}
                                ${r.error ? `<div style="margin-top: 5px; color: var(--accent-red); font-size: 0.85rem;">${r.error}</div>` : ''}
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
        
        document.getElementById('add-step')?.addEventListener('click', () => this.addStep());
        document.getElementById('run-chain')?.addEventListener('click', () => this.runChain());
    }
}

if (typeof window !== 'undefined') {
    window.ChainsPanel = ChainsPanel;
}
