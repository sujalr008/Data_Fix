from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

HTML_PAGE = '''<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>DataFix – Autonomous Data Quality & Repair Engine</title>
    <script src=\"https://cdn.tailwindcss.com\"></script>
    <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap\" rel=\"stylesheet\">
    <style>
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class=\"bg-slate-900 text-slate-100 min-h-screen py-8 px-4\">
    <div class=\"max-w-5xl mx-auto space-y-8\">
        <!-- Header -->
        <header class=\"flex items-center justify-between border-b border-slate-800 pb-6\">
            <div>
                <h1 class=\"text-3xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent\">
                    DataFix Engine
                </h1>
                <p class=\"text-sm text-slate-400 mt-1\">Autonomous Data Quality Inspection, AI Root Cause Analysis & Repair</p>
            </div>
            <a href=\"/docs\" target=\"_blank\" class=\"text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-2 rounded-lg border border-slate-700 transition\">
                Swagger API Docs ↗
            </a>
        </header>

        <!-- Step 1: Upload Section -->
        <div class=\"bg-slate-800/80 border border-slate-700 rounded-xl p-6 shadow-xl\">
            <h2 class=\"text-lg font-semibold text-white mb-3 flex items-center gap-2\">
                <span class=\"bg-blue-600 text-white rounded-full w-6 h-6 inline-flex items-center justify-center text-xs\">1</span>
                Upload Dataset (CSV or Excel)
            </h2>
            <div class=\"border-2 border-dashed border-slate-600 hover:border-blue-500 rounded-lg p-8 text-center cursor-pointer transition bg-slate-900/40\" id=\"dropzone\">
                <input type=\"file\" id=\"fileInput\" accept=\".csv,.xlsx,.xls\" class=\"hidden\">
                <div class=\"space-y-2\">
                    <svg class=\"mx-auto h-12 w-12 text-slate-400\" fill=\"none\" stroke=\"currentColor\" viewBox=\"0 0 24 24\">
                        <path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"1.5\" d=\"M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12\" />
                    </svg>
                    <p class=\"text-slate-300 font-medium\" id=\"fileLabel\">Click to choose file or drag and drop</p>
                    <p class=\"text-xs text-slate-500\">Supports CSV, XLSX up to 10 MB</p>
                </div>
            </div>
            <div class=\"mt-4 flex justify-end\">
                <button id=\"uploadBtn\" class=\"bg-blue-600 hover:bg-blue-500 text-white font-medium px-5 py-2.5 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed\" disabled>
                    Upload & Inspect
                </button>
            </div>
        </div>

        <!-- Step 2: Quality Inspection Results -->
        <div id=\"analysisCard\" class=\"hidden bg-slate-800/80 border border-slate-700 rounded-xl p-6 shadow-xl space-y-6\">
            <div class=\"flex items-center justify-between border-b border-slate-700/60 pb-4\">
                <div>
                    <h2 class=\"text-lg font-semibold text-white flex items-center gap-2\">
                        <span class=\"bg-blue-600 text-white rounded-full w-6 h-6 inline-flex items-center justify-center text-xs\">2</span>
                        Quality Health Score
                    </h2>
                    <p class=\"text-xs text-slate-400\">Session ID: <span id=\"sessionIdText\" class=\"font-mono text-blue-400\"></span></p>
                </div>
                <div class=\"text-right\">
                    <span id=\"qualityScoreBadge\" class=\"text-3xl font-bold px-4 py-1.5 rounded-xl border bg-slate-900\">--/100</span>
                </div>
            </div>

            <!-- Issues Table -->
            <div>
                <h3 class=\"text-sm font-semibold text-slate-300 mb-2\">Detected Quality Anomalies</h3>
                <div class=\"overflow-x-auto rounded-lg border border-slate-700\">
                    <table class=\"min-w-full divide-y divide-slate-700 text-sm\">
                        <thead class=\"bg-slate-900/60 text-slate-400 text-left\">
                            <tr>
                                <th class=\"py-2 px-4\">Issue Type</th>
                                <th class=\"py-2 px-4\">Field</th>
                                <th class=\"py-2 px-4\">Severity</th>
                                <th class=\"py-2 px-4\">Affected Count</th>
                                <th class=\"py-2 px-4\">Suggested Fix</th>
                            </tr>
                        </thead>
                        <tbody id=\"issuesTableBody\" class=\"divide-y divide-slate-800\"></tbody>
                    </table>
                </div>
            </div>

            <!-- Step 3: AI Insights -->
            <div class=\"bg-slate-900/70 border border-indigo-900/50 rounded-xl p-5 space-y-4\">
                <div class=\"flex items-center justify-between\">
                    <h3 class=\"text-md font-semibold text-indigo-300 flex items-center gap-2\">
                        ✨ AI Root Cause & Risk Analysis
                    </h3>
                    <button id=\"aiBtn\" class=\"text-xs bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-3 py-1.5 rounded-lg transition\">
                        Generate AI Insights
                    </button>
                </div>
                <div id=\"aiOutput\" class=\"hidden space-y-3 text-sm text-slate-300 border-t border-slate-800 pt-3\">
                    <p id=\"aiOverview\" class=\"text-slate-200 italic\"></p>
                    <div class=\"grid md:grid-cols-2 gap-4 mt-2\">
                        <div class=\"bg-slate-800/60 p-3 rounded-lg border border-slate-700/50\">
                            <h4 class=\"text-xs font-bold text-slate-400 uppercase tracking-wider mb-1\">Risk Assessment</h4>
                            <p id=\"aiRisk\" class=\"text-xs text-rose-300\"></p>
                        </div>
                        <div class=\"bg-slate-800/60 p-3 rounded-lg border border-slate-700/50\">
                            <h4 class=\"text-xs font-bold text-slate-400 uppercase tracking-wider mb-1\">Priority Remediations</h4>
                            <ul id=\"aiPriority\" class=\"text-xs text-slate-300 list-disc list-inside space-y-1\"></ul>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Step 4: Repair Options -->
            <div class=\"border-t border-slate-700/60 pt-5 space-y-4\">
                <h3 class=\"text-md font-semibold text-white flex items-center gap-2\">
                    <span class=\"bg-blue-600 text-white rounded-full w-6 h-6 inline-flex items-center justify-center text-xs\">3</span>
                    Autonomous Repair Configuration
                </h3>
                <div class=\"grid sm:grid-cols-2 md:grid-cols-4 gap-3 text-sm\">
                    <label class=\"flex items-center gap-2 p-3 bg-slate-900/50 rounded-lg border border-slate-700 cursor-pointer\">
                        <input type=\"checkbox\" id=\"optMissing\" checked class=\"accent-blue-500\">
                        <span>Fix Missing Values</span>
                    </label>
                    <label class=\"flex items-center gap-2 p-3 bg-slate-900/50 rounded-lg border border-slate-700 cursor-pointer\">
                        <input type=\"checkbox\" id=\"optDuplicates\" checked class=\"accent-blue-500\">
                        <span>Remove Duplicates</span>
                    </label>
                    <label class=\"flex items-center gap-2 p-3 bg-slate-900/50 rounded-lg border border-slate-700 cursor-pointer\">
                        <input type=\"checkbox\" id=\"optFormats\" checked class=\"accent-blue-500\">
                        <span>Standardise Formats</span>
                    </label>
                    <label class=\"flex items-center gap-2 p-3 bg-slate-900/50 rounded-lg border border-slate-700 cursor-pointer\">
                        <input type=\"checkbox\" id=\"optOutliers\" class=\"accent-blue-500\">
                        <span>Clip Outliers</span>
                    </label>
                </div>
                <div class=\"flex justify-end\">
                    <button id=\"repairBtn\" class=\"bg-emerald-600 hover:bg-emerald-500 text-white font-medium px-6 py-2.5 rounded-lg transition\">
                        Apply Autonomous Repair
                    </button>
                </div>
            </div>
        </div>

        <!-- Step 5: Diff & Download Results -->
        <div id=\"repairCard\" class=\"hidden bg-slate-800/80 border border-slate-700 rounded-xl p-6 shadow-xl space-y-6\">
            <div class=\"flex items-center justify-between border-b border-slate-700 pb-4\">
                <div>
                    <h2 class=\"text-lg font-semibold text-white flex items-center gap-2\">
                        <span class=\"bg-emerald-600 text-white rounded-full w-6 h-6 inline-flex items-center justify-center text-xs\">✓</span>
                        Repair Summary & Clean Dataset
                    </h2>
                    <p id=\"repairExplanation\" class=\"text-sm text-emerald-400 mt-1\"></p>
                </div>
                <div class=\"flex items-center gap-3\">
                    <button id=\"downloadCsvBtn\" class=\"bg-slate-700 hover:bg-slate-600 text-white text-xs px-3 py-2 rounded-lg transition border border-slate-600\">
                        Download CSV
                    </button>
                    <button id=\"downloadXlsxBtn\" class=\"bg-slate-700 hover:bg-slate-600 text-white text-xs px-3 py-2 rounded-lg transition border border-slate-600\">
                        Download Excel (.xlsx)
                    </button>
                </div>
            </div>

            <!-- Diff Table -->
            <div>
                <h3 class=\"text-sm font-semibold text-slate-300 mb-2\">Audit Trail (Original vs Repaired Changes)</h3>
                <div class=\"overflow-x-auto rounded-lg border border-slate-700 max-h-64 overflow-y-auto\">
                    <table class=\"min-w-full divide-y divide-slate-700 text-xs\">
                        <thead class=\"bg-slate-900/70 text-slate-400 sticky top-0\">
                            <tr>
                                <th class=\"py-2 px-3 text-left\">Row</th>
                                <th class=\"py-2 px-3 text-left\">Field</th>
                                <th class=\"py-2 px-3 text-left text-rose-400\">Original Value</th>
                                <th class=\"py-2 px-3 text-left text-emerald-400\">Repaired Value</th>
                            </tr>
                        </thead>
                        <tbody id=\"diffTableBody\" class=\"divide-y divide-slate-800\"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentSessionId = null;
        let selectedFile = null;

        const dropzone = document.getElementById('dropzone');
        const fileInput = document.getElementById('fileInput');
        const fileLabel = document.getElementById('fileLabel');
        const uploadBtn = document.getElementById('uploadBtn');

        dropzone.onclick = () => fileInput.click();
        fileInput.onchange = (e) => {
            if (e.target.files.length > 0) {
                selectedFile = e.target.files[0];
                fileLabel.innerText = selectedFile.name + ' (' + (selectedFile.size / 1024).toFixed(1) + ' KB)';
                uploadBtn.disabled = false;
            }
        };

        // Upload
        uploadBtn.onclick = async () => {
            if (!selectedFile) return;
            uploadBtn.innerText = 'Uploading & Inspecting...';
            uploadBtn.disabled = true;

            const formData = new FormData();
            formData.append('file', selectedFile);

            try {
                const res = await fetch('/api/upload', { method: 'POST', body: formData });
                const json = await res.json();
                if (json.success) {
                    currentSessionId = json.data.sessionId;
                    renderAnalysis(json.data);
                } else {
                    alert('Upload failed: ' + json.message);
                }
            } catch (err) {
                alert('Error: ' + err.message);
            } finally {
                uploadBtn.innerText = 'Upload & Inspect';
                uploadBtn.disabled = false;
            }
        };

        function renderAnalysis(data) {
            document.getElementById('analysisCard').classList.remove('hidden');
            document.getElementById('sessionIdText').innerText = data.sessionId;
            const scoreBadge = document.getElementById('qualityScoreBadge');
            scoreBadge.innerText = data.qualityScore + '/100';
            scoreBadge.className = data.qualityScore > 75 
                ? 'text-3xl font-bold px-4 py-1.5 rounded-xl border border-emerald-700 text-emerald-400 bg-slate-900'
                : 'text-3xl font-bold px-4 py-1.5 rounded-xl border border-amber-700 text-amber-400 bg-slate-900';

            const tbody = document.getElementById('issuesTableBody');
            tbody.innerHTML = '';
            data.issues.forEach(issue => {
                const tr = document.createElement('tr');
                const sevColor = issue.severity === 'critical' ? 'text-rose-400 bg-rose-950/50 border border-rose-800' : (issue.severity === 'high' ? 'text-amber-400 bg-amber-950/50 border border-amber-800' : 'text-slate-300 bg-slate-800 border border-slate-700');
                tr.innerHTML = 
                    <td class=\"py-2.5 px-4 font-mono text-xs\"></td>
                    <td class=\"py-2.5 px-4 font-semibold text-slate-200\"></td>
                    <td class=\"py-2.5 px-4\"><span class=\"text-xs px-2 py-0.5 rounded-full \"></span></td>
                    <td class=\"py-2.5 px-4\"></td>
                    <td class=\"py-2.5 px-4 text-xs text-slate-400\"></td>
                ;
                tbody.appendChild(tr);
            });
            window.scrollTo({ top: document.getElementById('analysisCard').offsetTop - 20, behavior: 'smooth' });
        }

        // AI Insights
        document.getElementById('aiBtn').onclick = async () => {
            if (!currentSessionId) return;
            const btn = document.getElementById('aiBtn');
            btn.innerText = 'Analyzing...';
            btn.disabled = true;

            try {
                const res = await fetch(/api/analysis//ai-insights, { method: 'POST' });
                const json = await res.json();
                if (json.success) {
                    document.getElementById('aiOutput').classList.remove('hidden');
                    document.getElementById('aiOverview').innerText = json.data.aiInsights;
                    document.getElementById('aiRisk').innerText = json.data.riskAssessment;
                    const ul = document.getElementById('aiPriority');
                    ul.innerHTML = '';
                    json.data.priorityOrder.forEach(item => {
                        const li = document.createElement('li');
                        li.innerText = item;
                        ul.appendChild(li);
                    });
                }
            } catch (err) {
                alert('AI generation failed: ' + err.message);
            } finally {
                btn.innerText = 'Regenerate AI Insights';
                btn.disabled = false;
            }
        };

        // Repair
        document.getElementById('repairBtn').onclick = async () => {
            if (!currentSessionId) return;
            const btn = document.getElementById('repairBtn');
            btn.innerText = 'Applying Repairs...';
            btn.disabled = true;

            const payload = {
                repairOptions: {
                    fixMissing: document.getElementById('optMissing').checked,
                    removeDuplicates: document.getElementById('optDuplicates').checked,
                    fixFormats: document.getElementById('optFormats').checked,
                    fixOutliers: document.getElementById('optOutliers').checked
                }
            };

            try {
                const res = await fetch(/api/repair/, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const json = await res.json();
                if (json.success) {
                    document.getElementById('repairCard').classList.remove('hidden');
                    document.getElementById('repairExplanation').innerText = json.data.aiExplanation;
                    loadDiff();
                }
            } catch (err) {
                alert('Repair failed: ' + err.message);
            } finally {
                btn.innerText = 'Apply Autonomous Repair';
                btn.disabled = false;
            }
        };

        // Load Diff
        async function loadDiff() {
            try {
                const res = await fetch(/api/repair//diff);
                const json = await res.json();
                if (json.success) {
                    const tbody = document.getElementById('diffTableBody');
                    tbody.innerHTML = '';
                    json.data.changes.forEach(c => {
                        const tr = document.createElement('tr');
                        tr.innerHTML = 
                            <td class=\"py-2 px-3 text-slate-400 font-mono\">#</td>
                            <td class=\"py-2 px-3 font-semibold text-slate-200\"></td>
                            <td class=\"py-2 px-3 text-rose-400 line-through\"></td>
                            <td class=\"py-2 px-3 text-emerald-400 font-semibold\"></td>
                        ;
                        tbody.appendChild(tr);
                    });
                    window.scrollTo({ top: document.getElementById('repairCard').offsetTop - 20, behavior: 'smooth' });
                }
            } catch (err) {
                console.error('Diff error:', err);
            }
        }

        // Downloads
        document.getElementById('downloadCsvBtn').onclick = () => {
            if (currentSessionId) window.location.href = /api/download/?format=csv;
        };
        document.getElementById('downloadXlsxBtn').onclick = () => {
            if (currentSessionId) window.location.href = /api/download/?format=xlsx;
        };
    </script>
</body>
</html>'''

@router.get('/', response_class=HTMLResponse)
def index_page():
    return HTML_PAGE
