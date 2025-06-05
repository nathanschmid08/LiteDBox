const totalDuration = 5000;
const updateInterval = 200;

const statusMessages = [
    "Checking system requirements...",
    "Loading core libraries...",
    "Initializing connection manager...",
    "Loading database drivers...",
    "Preparing user interface components...",
    "Loading saved connections...",
    "Initializing query builder...",
    "Checking for updates...",
    "Loading extensions...",
    "Setting up workspace...",
    "Loading SQL autocomplete dictionary...",
    "Initializing script engine...",
    "Setting up session parameters...",
    "Loading user preferences...",
    "Starting background services...",
    "Application ready.",
];

const taskMessages = [
    "Initializing...",
    "Loading core components...",
    "Preparing environment...",
    "Loading resources...",
    "Finalizing...",
];

const progressBar = document.getElementById("progress-bar");
const percentText = document.getElementById("percent");
const taskText = document.getElementById("task");
const loadingDetails = document.getElementById("loading-details");
const statusArea = document.getElementById("status-area");

let startTime = Date.now();
let currentTaskIndex = 0;
let statusIndex = 0;

function addStatusMessage(message) {
    const line = document.createElement("div");
    line.className = "status-line";
    line.textContent = message;
    statusArea.appendChild(line);
    statusArea.scrollTop = statusArea.scrollHeight;
}

function updateProgress() {
    const elapsedTime = Date.now() - startTime;
    const progress = Math.min(elapsedTime / totalDuration, 1);
    const progressPercent = Math.floor(progress * 100);

    progressBar.style.width = `${progressPercent}%`;
    percentText.textContent = `${progressPercent}%`;

    // Update task message at certain progress points
    const taskIndex = Math.floor(progress * taskMessages.length);
    if (taskIndex !== currentTaskIndex && taskIndex < taskMessages.length) {
        currentTaskIndex = taskIndex;
        taskText.textContent = taskMessages[taskIndex];
    }

    // Add status messages periodically
    if (statusIndex < statusMessages.length && Math.random() < 0.3) {
        addStatusMessage(statusMessages[statusIndex]);
        loadingDetails.textContent = statusMessages[statusIndex];
        statusIndex++;
    }

    // Continue updating if not done
    if (progress < 1) {
        setTimeout(updateProgress, updateInterval);
    } else {
        // Final status when loading is complete
        addStatusMessage("Application ready.");
        loadingDetails.textContent = "Ready to use.";
        taskText.textContent = "Complete";
    }
}

// Start the progress updates
updateProgress();