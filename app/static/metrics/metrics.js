async function fetchMetrics() {
    const response = await fetch("/metrics-json");
    const data = await response.json();

    // Update bars
    document.getElementById("cpu-bar").style.width = data.cpu_percent + "%";
    document.getElementById("cpu-text").innerText = data.cpu_percent + "%";

    document.getElementById("mem-bar").style.width = data.memory_percent + "%";
    document.getElementById("mem-text").innerText = `${data.memory_used.toFixed(1)} / ${data.memory_total.toFixed(1)} GB (${data.memory_percent}%)`;

    document.getElementById("disk-bar").style.width = data.disk_percent + "%";
    document.getElementById("disk-text").innerText = `${data.disk_used.toFixed(1)} / ${data.disk_total.toFixed(1)} GB (${data.disk_percent}%)`;
}

// Poll every 2 seconds
setInterval(fetchMetrics, 2000);
