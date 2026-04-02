/* ============================================
   FB Automotion Dashboard - Frontend Logic
   ============================================ */

// Socket.IO connection
const socket = io();

// ============ Status Updates ============
socket.on('status_update', function(state) {
    updateDashboard(state);
});

socket.on('connect', function() {
    console.log('Connected to dashboard server');
    addLog('Dashboard connected');
});

socket.on('disconnect', function() {
    console.log('Disconnected from server');
});

// ============ Update Dashboard ============
function updateDashboard(state) {
    // Gaming status
    const gamingBadge = document.getElementById('gaming-badge');
    if (gamingBadge) {
        if (state.gaming.running) {
            gamingBadge.textContent = 'Running';
            gamingBadge.className = 'badge badge-running';
        } else {
            gamingBadge.textContent = 'Stopped';
            gamingBadge.className = 'badge';
        }
    }

    // Personal status
    const personalBadge = document.getElementById('personal-badge');
    if (personalBadge) {
        if (state.personal.running) {
            personalBadge.textContent = 'Running';
            personalBadge.className = 'badge badge-running';
        } else {
            personalBadge.textContent = 'Stopped';
            personalBadge.className = 'badge';
        }
    }

    // FTP status
    const ftpDot = document.getElementById('ftp-dot');
    if (ftpDot) {
        ftpDot.className = state.ftp.running ? 'dot active' : 'dot';
    }

    const ftpStatus = document.getElementById('ftp-status');
    if (ftpStatus) {
        ftpStatus.textContent = state.ftp.running ? 'Online' : 'Offline';
    }

    // Gaming stats
    updateElement('gaming-processed', state.gaming.videos_processed);
    updateElement('gaming-uploaded', state.gaming.videos_uploaded);
    updateElement('gaming-queued', state.gaming.videos_queued);

    // Personal stats
    updateElement('personal-created', state.personal.posts_created);
    updateElement('personal-uploaded', state.personal.posts_uploaded);
    updateElement('personal-queued', state.personal.posts_queued);
}

function updateElement(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

// ============ Automation Controls ============
function startAutomation(type) {
    fetch(`/api/${type}/start`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            addLog(`${type.charAt(0).toUpperCase() + type.slice(1)} automation started`);
        })
        .catch(err => {
            addLog(`Error starting ${type}: ${err.message}`);
        });
}

function stopAutomation(type) {
    fetch(`/api/${type}/stop`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            addLog(`${type.charAt(0).toUpperCase() + type.slice(1)} automation stopped`);
        })
        .catch(err => {
            addLog(`Error stopping ${type}: ${err.message}`);
        });
}

// ============ Activity Log ============
function addLog(message) {
    const log = document.getElementById('activity-log');
    if (!log) return;

    const now = new Date();
    const time = now.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit' });

    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.innerHTML = `
        <span class="log-time">${time}</span>
        <span class="log-msg">${message}</span>
    `;

    log.insertBefore(entry, log.firstChild);

    // Keep only last 50 entries
    while (log.children.length > 50) {
        log.removeChild(log.lastChild);
    }
}

// ============ Clock ============
function updateClock() {
    const el = document.getElementById('current-time');
    if (el) {
        const now = new Date();
        el.textContent = now.toLocaleString('en-US', {
            weekday: 'short',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true
        });
    }
}

setInterval(updateClock, 1000);
updateClock();

// ============ Auto Refresh Stats ============
function refreshStats() {
    fetch('/api/status')
        .then(r => r.json())
        .then(data => {
            updateElement('raw-count', data.raw_videos);
            updateElement('gaming-ready', data.gaming_ready);
            updateElement('personal-ready', data.personal_ready);
            updateDashboard(data.state);
        })
        .catch(() => {});
}

// Refresh every 10 seconds
setInterval(refreshStats, 10000);
