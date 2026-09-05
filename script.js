const API_BASE_URL = "http://127.0.0.1:8000";

// ========================================
// STATE & CONFIG
// ========================================
let allTransactions = [];
let currentPage = 1;
const PAGE_SIZE = 50;

let allAuditLogs = [];
let currentAuditPage = 1;
const AUDIT_PAGE_SIZE = 50;

let recoveryLineChart = null;

// ========================================
// FORMATTING HELPERS
// ========================================
const formatCurrency = (amount) => `₹${Number(amount || 0).toLocaleString("en-IN")}`;
const formatPercent = (rate) => `${rate ?? 0}%`;


// ========================================
// REVENUE RECOVERY LINE GRAPH
// ========================================
function updateLineChart(logsData) {
    const canvas = document.getElementById("recoveryLineChart");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    const logs = Array.isArray(logsData) ? [...logsData] : [];
    logs.reverse(); // Chronological order (oldest to newest)

    const labels = ["0"];
    const cumulativeData = [0];
    let runningTotal = 0;

    logs.forEach((log, index) => {
        if (log.recovery_success) {
            runningTotal += Number(log.recovered_amount || log.amount || 0);
        }
        labels.push(`${index + 1}`);
        cumulativeData.push(runningTotal);
    });

    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, "rgba(16, 185, 129, 0.25)");
    gradient.addColorStop(1, "rgba(16, 185, 129, 0.0)");

    const pointSize = cumulativeData.length > 30 ? 2 : 4;

    if (!recoveryLineChart) {
        recoveryLineChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: "Recovery Progress (₹)",
                    data: cumulativeData,
                    borderColor: "#10b981",
                    backgroundColor: gradient,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.35,
                    pointBackgroundColor: "#10b981",
                    pointBorderColor: "#ffffff",
                    pointBorderWidth: 1.5,
                    pointRadius: pointSize,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: { duration: 750 },
                plugins: {
                    legend: {
                        position: "top",
                        labels: { font: { weight: "700", size: 13 } }
                    },
                    tooltip: {
                        callbacks: {
                            title: (items) => {
                                const idx = items[0].dataIndex;
                                if (idx === 0) return "Baseline (Start)";
                                const log = logs[idx - 1];
                                return `Transaction #${idx} (${log?.transaction_id || ""})`;
                            },
                            label: (ctx) => ` Total Recovered: ₹${Number(ctx.raw).toLocaleString("en-IN")}`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: "#f1f5f9" },
                        title: {
                            display: true,
                            text: "Revenue Recovered (₹)",
                            color: "#64748b",
                            font: { weight: "600", size: 12 },
                            padding: { bottom: 10 }
                        },
                        ticks: {
                            callback: (val) => `₹${Number(val).toLocaleString("en-IN")}`,
                            color: "#64748b",
                            font: { weight: "500" }
                        }
                    },
                    x: {
                        grid: { display: false },
                        title: {
                            display: true,
                            text: "Transactions Processed",
                            color: "#64748b",
                            font: { weight: "600", size: 12 },
                            padding: { top: 10 }
                        },
                        ticks: {
                            maxTicksLimit: 7,
                            autoSkip: true,
                            maxRotation: 0,
                            color: "#64748b",
                            font: { weight: "500", size: 12 }
                        }
                    }
                }
            }
        });
    } else {
        recoveryLineChart.data.labels = labels;
        recoveryLineChart.data.datasets[0].data = cumulativeData;
        recoveryLineChart.data.datasets[0].pointRadius = pointSize;
        recoveryLineChart.update();
    }
}


// ========================================
// METRICS (5 CARDS)
// ========================================
async function loadMetrics() {
    try {
        const res = await fetch(`${API_BASE_URL}/metrics`);
        if (!res.ok) throw new Error(`Metrics API error: ${res.status}`);
        const data = await res.json();

        document.getElementById("failedTransactions").textContent = data.total_failed_transactions ?? "-";
        document.getElementById("failedRevenue").textContent = formatCurrency(data.total_failed_revenue);
        document.getElementById("revenueRecovered").textContent = formatCurrency(data.revenue_recovered);
        document.getElementById("recoveryRate").textContent = formatPercent(data.recovery_rate);

        const successRateEl = document.getElementById("attemptedSuccessRate");
        if (successRateEl) {
            successRateEl.textContent = formatPercent(data.attempted_success_rate);
        }
    } catch (err) {
        console.error("Failed to load metrics:", err);
    }
}


// ========================================
// LOAD TRANSACTIONS
// ========================================
async function loadTransactions() {
    try {
        const res = await fetch(`${API_BASE_URL}/transactions?limit=500`);
        if (!res.ok) throw new Error(`Transactions API error: ${res.status}`);
        const data = await res.json();

        allTransactions = data.transactions || [];
        const totalPages = Math.ceil(allTransactions.length / PAGE_SIZE) || 1;
        if (currentPage > totalPages) currentPage = totalPages;

        renderCurrentPage();
    } catch (err) {
        console.error("Failed to load transactions:", err);
    }
}


// ========================================
// RENDER TRANSACTIONS (50 PER PAGE)
// ========================================
function renderCurrentPage() {
    const table = document.getElementById("transactionTable");
    table.innerHTML = "";

    const total = allTransactions.length;
    const totalPages = Math.ceil(total / PAGE_SIZE) || 1;
    const start = (currentPage - 1) * PAGE_SIZE;
    const end = Math.min(start + PAGE_SIZE, total);
    const pageItems = allTransactions.slice(start, end);

    if (pageItems.length === 0) {
        table.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:24px; color:#64748b;">No transactions found.</td></tr>`;
    } else {
        pageItems.forEach((tx) => {
            const score = (tx.recovery_score !== null && tx.recovery_score !== undefined) ? tx.recovery_score : "-";
            const category = tx.recovery_category || "Not processed";
            const action = tx.ai_action || tx.ai_decision || "Not processed";

            const row = document.createElement("tr");
            row.innerHTML = `
                <td>
                    <button type="button" class="transaction-button" data-id="${tx.transaction_id}">
                        ${tx.transaction_id}
                    </button>
                </td>
                <td>${formatCurrency(tx.amount)}</td>
                <td>${tx.failure_reason}</td>
                <td class="score">${score}</td>
                <td>${category}</td>
                <td>${action}</td>
            `;

            row.querySelector(".transaction-button").addEventListener("click", (e) => {
                e.preventDefault();
                showTransaction(tx.transaction_id);
            });

            table.appendChild(row);
        });
    }

    const info = document.getElementById("paginationInfo");
    if (info) info.textContent = total > 0 ? `Showing ${start + 1}–${end} of ${total} transactions` : "No transactions";

    const indicator = document.getElementById("currentPageIndicator");
    if (indicator) indicator.textContent = `Page ${currentPage} of ${totalPages}`;

    const prevBtn = document.getElementById("prevPageBtn");
    const nextBtn = document.getElementById("nextPageBtn");
    if (prevBtn) prevBtn.disabled = (currentPage <= 1);
    if (nextBtn) nextBtn.disabled = (currentPage >= totalPages);
}


// ========================================
// TRANSACTION INFORMATION SECTION
// ========================================
function renderInfoSection(tx, analysis) {
    return `
        <div class="analysis-section">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <h3 style="margin:0;">Transaction Information</h3>
                <button type="button" id="clearBtn" class="clear-button">Clear</button>
            </div>
            <div class="detail-grid">
                <div class="detail-item"><h4>Transaction ID</h4><p>${tx.transaction_id}</p></div>
                <div class="detail-item"><h4>Amount</h4><p>${formatCurrency(tx.amount)}</p></div>
                <div class="detail-item"><h4>Failure Reason</h4><p>${tx.failure_reason}</p></div>
                <div class="detail-item"><h4>Recovery Score</h4><p>${analysis.score ?? "-"}</p></div>
                <div class="detail-item"><h4>Category</h4><p>${analysis.category ?? "-"}</p></div>
                <div class="detail-item"><h4>Previous Successes</h4><p>${tx.previous_successes ?? 0}</p></div>
                <div class="detail-item"><h4>Previous Failures</h4><p>${tx.previous_failures ?? 0}</p></div>
                <div class="detail-item"><h4>Recovery Attempts</h4><p>${tx.attempt_count ?? 0}</p></div>
            </div>
        </div>
    `;
}


// ========================================
// AI DECISION SECTION
// ========================================
function renderAIDecisionSection(ai, policy) {
    const isAllowed = policy?.allowed ?? false;

    return `
        <div class="analysis-section">
            <h3>AI Recovery Decision</h3>
            <div class="detail-grid">
                <div class="detail-item"><h4>Decision</h4><p>${ai.decision || "-"}</p></div>
                <div class="detail-item"><h4>Recommended Action</h4><p>${ai.action || "-"}</p></div>
                <div class="detail-item"><h4>Confidence</h4><p>${Math.round(Number(ai.confidence || 0) * 100)}%</p></div>
                <div class="detail-item">
                    <h4>Policy</h4>
                    <p style="color:${isAllowed ? "#16a34a" : "#dc2626"}; font-weight:700;">
                        ${isAllowed ? "ALLOWED" : "BLOCKED"}
                    </p>
                </div>
            </div>
            <div class="detail-item" style="margin-top:14px; border-left:4px solid #3b82f6;">
                <h4>AI Reason</h4>
                <p style="font-weight:500; font-size:14px;">${ai.reason || "No reason provided."}</p>
            </div>
        </div>
    `;
}


// ========================================
// RECOVERY RESULT SECTION (WITH CONDITIONAL RE-RUN)
// ========================================
function renderResultSection(rec, attempts = 0) {
    const isSuccess = rec?.success ?? false;
    const message = String(rec?.message || "").toLowerCase();
    const isStopped = message.includes("stopped");
    const isBlocked = message.includes("blocked");

    // Only allow Re-run if Attempt 1 failed and it wasn't blocked/stopped
    const canRerun = !isSuccess && attempts === 1 && !isStopped && !isBlocked;

    return `
        <div class="analysis-section">
            <h3>Recovery Result</h3>
            <div class="detail-grid">
                <div class="detail-item">
                    <h4>Status</h4>
                    <p style="color:${isSuccess ? "#16a34a" : "#dc2626"}; font-weight:700;">
                        ${isSuccess ? "RECOVERED" : "NOT RECOVERED"}
                    </p>
                </div>
                <div class="detail-item">
                    <h4>Recovered Amount</h4>
                    <p>${formatCurrency(rec?.recovered_amount)}</p>
                </div>
                <div class="detail-item">
                    <h4>Recovery Attempts</h4>
                    <p>${attempts}</p>
                </div>
            </div>
            <div class="detail-item" style="margin-top:14px; border-left:4px solid ${isSuccess ? "#10b981" : "#ef4444"};">
                <h4>Recovery Message</h4>
                <p style="font-weight:500; font-size:14px;">${rec?.message || "No recovery message."}</p>
            </div>
            ${
                canRerun
                    ? `<button type="button" class="recover-button" id="rerunRecoverBtn" style="margin-top:16px;">
                           Re-run AI Recovery
                       </button>`
                    : ""
            }
        </div>
    `;
}


function attachRerunRecoveryButton(transactionId) {
    const rerunBtn = document.getElementById("rerunRecoverBtn");
    if (!rerunBtn) return;
    rerunBtn.addEventListener("click", () => recoverTransaction(transactionId));
}


// ========================================
// CLEAR ANALYSIS
// ========================================
function clearAnalysis() {
    sessionStorage.removeItem("activeAnalysis");
    document.getElementById("transactionDetails").innerHTML = `
        <p>Select a transaction to view its recovery analysis.</p>
    `;
}


// ========================================
// SHOW TRANSACTION ANALYSIS
// ========================================
async function showTransaction(transactionId) {
    const details = document.getElementById("transactionDetails");
    details.innerHTML = `
        <div class="analysis-section">
            <h3>Loading Transaction</h3>
            <p>Loading transaction analysis...</p>
        </div>
    `;

    try {
        const res = await fetch(`${API_BASE_URL}/transactions/${transactionId}/analysis`);
        if (!res.ok) throw new Error(`Analysis API error: ${res.status}`);
        const data = await res.json();

        details.innerHTML = `
            ${renderInfoSection(data.transaction, data.recovery_analysis)}
            <div class="analysis-section" id="aiRecoverySection">
                <h3>AI Recovery</h3>
                <p>Click the button below to let RevenueAI analyze and recover this payment.</p>
                <button type="button" class="recover-button" id="recoverBtn">
                    Run AI Recovery
                </button>
            </div>
        `;

        document.getElementById("clearBtn").addEventListener("click", clearAnalysis);
        document.getElementById("recoverBtn").addEventListener("click", () => recoverTransaction(transactionId));

        sessionStorage.setItem("activeAnalysis", JSON.stringify({ type: "details", transactionId, data }));

    } catch (err) {
        console.error("Failed to load transaction:", err);
        details.innerHTML = `
            <div class="analysis-section">
                <h3 style="color:#dc2626;">Error</h3>
                <p>${err.message}</p>
                <button type="button" class="clear-button" id="clearBtn" style="margin-top:10px;">Clear</button>
            </div>
        `;
        document.getElementById("clearBtn").addEventListener("click", clearAnalysis);
    }
}


// ========================================
// RUN / RE-RUN AI RECOVERY
// ========================================
async function recoverTransaction(transactionId) {
    const btn = document.getElementById("recoverBtn");
    const rerunBtn = document.getElementById("rerunRecoverBtn");

    if (btn) {
        btn.disabled = true;
        btn.textContent = "Analyzing with AI...";
    }
    if (rerunBtn) {
        rerunBtn.disabled = true;
        rerunBtn.textContent = "Re-running AI Recovery...";
    }

    try {
        const res = await fetch(`${API_BASE_URL}/transactions/${transactionId}/recover`, { method: "POST" });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || `Recovery error: ${res.status}`);

        const attempts = data.recovery_attempts ?? data.transaction?.attempt_count ?? 0;
        const details = document.getElementById("transactionDetails");

        details.innerHTML = `
            ${renderInfoSection(data.transaction, data.recovery_analysis)}
            ${renderAIDecisionSection(data.ai_decision, data.policy_check)}
            ${renderResultSection(data.recovery_result, attempts)}
        `;

        document.getElementById("clearBtn").addEventListener("click", clearAnalysis);
        attachRerunRecoveryButton(transactionId);

        sessionStorage.setItem("activeAnalysis", JSON.stringify({ type: "recovered", transactionId, data }));

        // Refresh all tables, metrics, and line graph
        await Promise.all([
            loadMetrics(),
            loadTransactions(),
            loadAuditTrail()
        ]);

    } catch (err) {
        console.error("AI recovery failed:", err);
        alert(`Recovery failed: ${err.message}`);
        if (btn) {
            btn.disabled = false;
            btn.textContent = "Run AI Recovery";
        }
        if (rerunBtn) {
            rerunBtn.disabled = false;
            rerunBtn.textContent = "Re-run AI Recovery";
        }
    }
}


// ========================================
// RESTORE ANALYSIS AFTER RELOAD
// ========================================
function restoreAnalysis() {
    const saved = sessionStorage.getItem("activeAnalysis");
    if (!saved) return;

    try {
        const { type, transactionId, data } = JSON.parse(saved);
        const details = document.getElementById("transactionDetails");

        if (type === "recovered") {
            const attempts = data.recovery_attempts ?? data.transaction?.attempt_count ?? 0;
            details.innerHTML = `
                ${renderInfoSection(data.transaction, data.recovery_analysis)}
                ${renderAIDecisionSection(data.ai_decision, data.policy_check)}
                ${renderResultSection(data.recovery_result, attempts)}
            `;
            document.getElementById("clearBtn").addEventListener("click", clearAnalysis);
            attachRerunRecoveryButton(transactionId);
        } else if (type === "details") {
            showTransaction(transactionId);
        }
    } catch (e) {
        console.error("Failed to restore analysis:", e);
        sessionStorage.removeItem("activeAnalysis");
    }
}


// ========================================
// AUDIT LOG DETAILS (ROW 3 - RIGHT PANEL)
// ========================================
function clearAuditDetails() {
    const details = document.getElementById("auditDetails");
    if (details) {
        details.innerHTML = `<p>Select an audit record from the table to view its full details.</p>`;
    }
}

function showAuditDetails(log) {
    const details = document.getElementById("auditDetails");
    if (!details) return;

    const policyAllowed = Boolean(log.policy_allowed);
    const recoverySuccess = Boolean(log.recovery_success);

    details.innerHTML = `
        <div class="analysis-section">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <h3 style="margin:0;">Recovery Audit Details</h3>
                <button type="button" id="clearAuditBtn" class="clear-button">Clear</button>
            </div>
            <div class="detail-grid">
                <div class="detail-item"><h4>Transaction ID</h4><p>${log.transaction_id || "-"}</p></div>
                <div class="detail-item"><h4>Amount</h4><p>${formatCurrency(log.amount)}</p></div>
                <div class="detail-item"><h4>Recovery Score</h4><p>${log.recovery_score ?? "-"}</p></div>
                <div class="detail-item"><h4>Recovery Category</h4><p>${log.recovery_category || "-"}</p></div>
                <div class="detail-item"><h4>AI Decision</h4><p>${log.ai_decision || "-"}</p></div>
                <div class="detail-item"><h4>AI Action</h4><p>${log.ai_action || "-"}</p></div>
                <div class="detail-item"><h4>AI Confidence</h4><p>${Math.round(Number(log.ai_confidence || 0) * 100)}%</p></div>
                <div class="detail-item">
                    <h4>Policy</h4>
                    <p style="color:${policyAllowed ? "#16a34a" : "#dc2626"}; font-weight:700;">
                        ${policyAllowed ? "ALLOWED" : "BLOCKED"}
                    </p>
                </div>
                <div class="detail-item">
                    <h4>Recovery Result</h4>
                    <p style="color:${recoverySuccess ? "#16a34a" : "#dc2626"}; font-weight:700;">
                        ${recoverySuccess ? "RECOVERED" : "NOT RECOVERED"}
                    </p>
                </div>
                <div class="detail-item"><h4>Recovered Amount</h4><p>${formatCurrency(log.recovered_amount)}</p></div>
                <div class="detail-item"><h4>Recovery Attempts</h4><p>${log.attempt_count ?? 0}</p></div>
            </div>

            <div class="detail-item" style="margin-top:14px; border-left:4px solid #3b82f6;">
                <h4>AI Reason</h4>
                <p style="font-weight:500; font-size:14px; color:#334155;">${log.ai_reason || "No reason provided."}</p>
            </div>
            <div class="detail-item" style="margin-top:14px; border-left:4px solid #f59e0b;">
                <h4>Policy Reason</h4>
                <p style="font-weight:500; font-size:14px; color:#334155;">${log.policy_reason || "No policy reason provided."}</p>
            </div>
            <div class="detail-item" style="margin-top:14px; border-left:4px solid #10b981;">
                <h4>Recovery Message</h4>
                <p style="font-weight:500; font-size:14px; color:#334155;">${log.recovery_message || "No recovery message."}</p>
            </div>
            <div class="detail-item" style="margin-top:14px;">
                <h4>Logged At</h4>
                <p style="font-weight:500; font-size:13px; color:#64748b;">${log.created_at || "-"}</p>
            </div>
        </div>
    `;

    document.getElementById("clearAuditBtn").addEventListener("click", clearAuditDetails);
    details.scrollIntoView({ behavior: "smooth", block: "nearest" });
}


// ========================================
// LOAD RECOVERY AUDIT TRAIL
// ========================================
async function loadAuditTrail() {
    try {
        const res = await fetch(`${API_BASE_URL}/recovery-logs`);
        if (!res.ok) throw new Error(`Audit API error: ${res.status}`);
        const data = await res.json();

        allAuditLogs = data.logs || [];
        const totalPages = Math.ceil(allAuditLogs.length / AUDIT_PAGE_SIZE) || 1;
        if (currentAuditPage > totalPages) currentAuditPage = totalPages;

        renderCurrentAuditPage();
        updateLineChart(allAuditLogs);

    } catch (err) {
        console.error("Failed to load audit trail:", err);
        const tableBody = document.getElementById("auditTableBody");
        if (tableBody) {
            tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:#dc2626; padding:24px;">Failed to load audit trail.</td></tr>`;
        }
    }
}


// ========================================
// RENDER AUDIT PAGE (50 PER PAGE)
// ========================================
function renderCurrentAuditPage() {
    const tableBody = document.getElementById("auditTableBody");
    if (!tableBody) return;

    const total = allAuditLogs.length;
    const totalPages = Math.ceil(total / AUDIT_PAGE_SIZE) || 1;
    const start = (currentAuditPage - 1) * AUDIT_PAGE_SIZE;
    const end = Math.min(start + AUDIT_PAGE_SIZE, total);
    const pageItems = allAuditLogs.slice(start, end);

    if (pageItems.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:#64748b; padding:24px;">No recovery decisions recorded yet.</td></tr>`;
    } else {
        tableBody.innerHTML = pageItems.map((log, index) => {
            let resultText = "FAILED";
            if (log.recovery_success) {
                resultText = "RECOVERED";
            } else if (!log.policy_allowed) {
                resultText = "BLOCKED";
            } else if (log.ai_decision === "STOP_RECOVERY" || log.ai_action === "STOP_RECOVERY") {
                resultText = "STOPPED";
            }

            return `
                <tr>
                    <td>
                        <button type="button" class="audit-transaction-button" data-index="${start + index}">
                            ${log.transaction_id}
                        </button>
                    </td>
                    <td>${formatCurrency(log.amount)}</td>
                    <td>${log.ai_decision || "-"}</td>
                    <td>${log.ai_action || "-"}</td>
                    <td style="font-weight:700; color:${log.policy_allowed ? "#16a34a" : "#dc2626"};">
                        ${log.policy_allowed ? "ALLOWED" : "BLOCKED"}
                    </td>
                    <td style="font-weight:700; color:${log.recovery_success ? "#16a34a" : "#dc2626"};">
                        ${resultText}
                    </td>
                    <td>${formatCurrency(log.recovered_amount)}</td>
                </tr>
            `;
        }).join("");

        tableBody.querySelectorAll(".audit-transaction-button").forEach(button => {
            button.addEventListener("click", () => {
                const index = Number(button.dataset.index);
                showAuditDetails(allAuditLogs[index]);
            });
        });
    }

    const info = document.getElementById("auditPaginationInfo");
    if (info) info.textContent = total > 0 ? `Showing ${start + 1}–${end} of ${total} records` : "No records";

    const indicator = document.getElementById("currentAuditPageIndicator");
    if (indicator) indicator.textContent = `Page ${currentAuditPage} of ${totalPages}`;

    const prevBtn = document.getElementById("prevAuditPageBtn");
    const nextBtn = document.getElementById("nextAuditPageBtn");
    if (prevBtn) prevBtn.disabled = (currentAuditPage <= 1);
    if (nextBtn) nextBtn.disabled = (currentAuditPage >= totalPages);
}


// ========================================
// RESET ENTIRE SYSTEM
// ========================================
async function resetSystem() {
    const confirmReset = confirm("Are you sure you want to reset all recovery decisions and metrics? This will start from the beginning.");
    if (!confirmReset) return;

    try {
        const res = await fetch(`${API_BASE_URL}/reset`, { method: "POST" });
        if (!res.ok) throw new Error(`Reset error: ${res.status}`);

        sessionStorage.clear();
        currentPage = 1;
        currentAuditPage = 1;

        clearAnalysis();
        clearAuditDetails();
        updateLineChart([]);

        await Promise.all([
            loadMetrics(),
            loadTransactions(),
            loadAuditTrail()
        ]);

        alert("All recovery decisions have been cleared! Fresh start ready.");
    } catch (err) {
        console.error("Failed to reset system:", err);
        alert(`Reset failed: ${err.message}`);
    }
}


// ========================================
// INITIALIZE DASHBOARD
// ========================================
async function initializeDashboard() {
    // Header Reset Button
    const resetBtn = document.getElementById("resetSystemBtn");
    if (resetBtn) resetBtn.addEventListener("click", resetSystem);

    // Failed Transactions Pagination Buttons
    const prevBtn = document.getElementById("prevPageBtn");
    if (prevBtn) {
        prevBtn.addEventListener("click", () => {
            if (currentPage > 1) {
                currentPage--;
                renderCurrentPage();
            }
        });
    }

    const nextBtn = document.getElementById("nextPageBtn");
    if (nextBtn) {
        nextBtn.addEventListener("click", () => {
            const totalPages = Math.ceil(allTransactions.length / PAGE_SIZE);
            if (currentPage < totalPages) {
                currentPage++;
                renderCurrentPage();
            }
        });
    }

    // Audit Trail Pagination Buttons (WIRED UP!)
    const prevAuditBtn = document.getElementById("prevAuditPageBtn");
    if (prevAuditBtn) {
        prevAuditBtn.addEventListener("click", () => {
            if (currentAuditPage > 1) {
                currentAuditPage--;
                renderCurrentAuditPage();
            }
        });
    }

    const nextAuditBtn = document.getElementById("nextAuditPageBtn");
    if (nextAuditBtn) {
        nextAuditBtn.addEventListener("click", () => {
            const totalPages = Math.ceil(allAuditLogs.length / AUDIT_PAGE_SIZE);
            if (currentAuditPage < totalPages) {
                currentAuditPage++;
                renderCurrentAuditPage();
            }
        });
    }

    // Initial load
    await Promise.all([
        loadMetrics(),
        loadTransactions(),
        loadAuditTrail()
    ]);

    restoreAnalysis();
}

initializeDashboard();