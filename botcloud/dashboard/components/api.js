/**
 * BotCloud Dashboard - Shared API Client
 */

const API_URL = 'http://localhost:8000';

class BotCloudAPI {
    constructor(baseUrl = API_URL) {
        this.baseUrl = baseUrl;
    }
    
    // Health
    async health() {
        return this.get('/health');
    }
    
    // Workers/Agents
    async listAgents() {
        return this.get('/agents');
    }
    
    async createAgent(name, capabilities = []) {
        return this.post('/agents', { name, capabilities });
    }
    
    // Tasks
    async listTasks() {
        return this.get('/tasks');
    }
    
    async createTask(agentId, inputData, callbackUrl = null) {
        const payload = { input_data: inputData };
        if (callbackUrl) payload.callback_url = callbackUrl;
        return this.post(`/agents/${agentId}/tasks`, payload);
    }
    
    async getTask(taskId) {
        return this.get(`/tasks/${taskId}`);
    }
    
    // Shared Memory
    async sharedList() {
        return this.get('/shared');
    }
    
    async sharedGet(key) {
        return this.get(`/shared/${key}`);
    }
    
    async sharedSet(key, value) {
        return this.put(`/shared/${key}`, { value });
    }
    
    async sharedIncr(key, delta = 1) {
        return this.post(`/shared/${key}/incr`, { delta });
    }
    
    async sharedDelete(key) {
        return this.delete(`/shared/${key}`);
    }
    
    // Streams
    async listStreams() {
        return this.get('/ws/streams');
    }
    
    // HTTP helpers
    async get(path) {
        const res = await fetch(this.baseUrl + path);
        return res.json();
    }
    
    async post(path, data) {
        const res = await fetch(this.baseUrl + path, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return res.json();
    }
    
    async put(path, data) {
        const res = await fetch(this.baseUrl + path, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return res.json();
    }
    
    async delete(path) {
        const res = await fetch(this.baseUrl + path, {
            method: 'DELETE'
        });
        return res.json();
    }
}

// Create global instance
const api = new BotCloudAPI();

// Toast notifications
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Format time
function formatTime(isoString) {
    if (!isoString) return '-';
    const date = new Date(isoString);
    return date.toLocaleTimeString();
}

// Format relative time
function formatRelative(isoString) {
    if (!isoString) return '-';
    const date = new Date(isoString);
    const now = new Date();
    const diff = now - date;
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff/60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff/3600000)}h ago`;
    return date.toLocaleDateString();
}

// Export for use in components
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { BotCloudAPI, api, showToast, formatTime, formatRelative };
}
