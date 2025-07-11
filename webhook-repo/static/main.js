function formatEvent(event) {
    const date = new Date(event.timestamp).toUTCString();
    switch (event.action_type) {
        case "PUSH":
            return `${event.author} pushed to ${event.to_branch} on ${date}`;
        case "PULL_REQUEST":
            return `${event.author} submitted a pull request from ${event.from_branch} to ${event.to_branch} on ${date}`;
        case "MERGE":
            return `${event.author} merged branch ${event.from_branch} to ${event.to_branch} on ${date}`;
        default:
            return "Unknown event";
    }
}

async function fetchEvents() {
    const res = await fetch('/events');
    const data = await res.json();
    const list = document.getElementById('activity-list');
    list.innerHTML = '';
    data.forEach(event => {
        const li = document.createElement('li');
        li.textContent = formatEvent(event);
        list.appendChild(li);
    });
}

setInterval(fetchEvents, 15000); // Poll every 15 sec
window.onload = fetchEvents;
