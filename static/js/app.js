// AI Career Copilot - Frontend Application Logic

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initFileUpload();
    initFormSubmission();
    initSingleOptimizer();
    loadScanHistory();
});

// TAB NAVIGATION
function initNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');

            navButtons.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));

            btn.classList.add('active');
            const activePane = document.getElementById(targetTab);
            if (activePane) activePane.classList.add('active');

            if (targetTab === 'tab-history') {
                loadScanHistory();
            }
        });
    });
}

// FILE DRAG & DROP UPLOAD
function initFileUpload() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('resumePdf');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const btnRemove = document.getElementById('btnRemoveFile');

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('dragover');
        });
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            const ext = files[0].name.toLowerCase();
            if (ext.endsWith('.pdf') || ext.endsWith('.docx') || ext.endsWith('.doc')) {
                fileInput.files = files;
                updateFileDisplay(files[0].name);
            } else {
                alert('Please drop a valid PDF or DOCX file.');
            }
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            updateFileDisplay(fileInput.files[0].name);
        }
    });

    btnRemove.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        fileInput.value = '';
        fileInfo.classList.add('hidden');
        dropZone.querySelector('.drop-title').classList.remove('hidden');
        dropZone.querySelector('.drop-subtitle').classList.remove('hidden');
    });

    function updateFileDisplay(name) {
        fileName.textContent = name;
        fileInfo.classList.remove('hidden');
        dropZone.querySelector('.drop-title').classList.add('hidden');
        dropZone.querySelector('.drop-subtitle').classList.add('hidden');
    }
}

// FORM SUBMISSION & ANALYSIS
function initFormSubmission() {
    const form = document.getElementById('analyzeForm');
    const btnSubmit = document.getElementById('btnSubmit');
    const spinner = document.getElementById('spinner');
    const btnText = btnSubmit.querySelector('.btn-text');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const jobDesc = formData.get('job_description').trim();
        const resumeText = formData.get('resume_text').trim();
        const pdfInput = document.getElementById('resumePdf');

        if (!jobDesc) {
            alert('Please enter a target job description.');
            return;
        }

        if (pdfInput.files.length === 0 && !resumeText) {
            alert('Please upload a PDF resume or paste resume text.');
            return;
        }

        // Show loading spinner
        spinner.classList.remove('hidden');
        btnText.textContent = 'Parsing & Analyzing...';
        btnSubmit.disabled = True = true;

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                renderDashboard(data);
            } else {
                alert('Analysis Error: ' + (data.error || 'Failed to analyze resume.'));
            }
        } catch (err) {
            alert('Network Error: ' + err.message);
        } finally {
            spinner.classList.add('hidden');
            btnText.textContent = 'Run ATS Match Analysis';
            btnSubmit.disabled = false;
        }
    });

    document.getElementById('btnReanalyze')?.addEventListener('click', () => {
        document.getElementById('emptyState').classList.remove('hidden');
        document.getElementById('dashboardContent').classList.add('hidden');
    });
}

// RENDER DASHBOARD RESULTS
function renderDashboard(data) {
    document.getElementById('emptyState').classList.add('hidden');
    document.getElementById('dashboardContent').classList.remove('hidden');

    document.getElementById('resultJobTitle').textContent = `${data.target_job_title || 'Software Engineer'} Report`;
    document.getElementById('resultFilename').textContent = `${data.filename || 'Resume.pdf'} • ${data.word_count || 0} words`;

    // Overall score gauge & dynamic rating hint
    const scoreOverall = data.overall_match_score || 0;
    document.getElementById('scoreOverall').textContent = `${scoreOverall}%`;
    const gauge = document.getElementById('overallGauge');
    gauge.style.setProperty('--score', scoreOverall);

    const hintOverall = document.getElementById('hintOverall');
    if (hintOverall) {
        if (scoreOverall >= 80) {
            hintOverall.textContent = "High Candidate Fit (Ready to Apply)";
            hintOverall.style.color = "var(--accent-green-bright)";
        } else if (scoreOverall >= 65) {
            hintOverall.textContent = "Good Match (Add missing skills)";
            hintOverall.style.color = "var(--accent-amber)";
        } else {
            hintOverall.textContent = "Low Match (Needs Revision)";
            hintOverall.style.color = "var(--accent-red)";
        }
    }

    // ATS score
    const scoreAts = data.ats_formatting_score || 0;
    document.getElementById('scoreAts').textContent = `${scoreAts}%`;
    document.getElementById('barAts').style.width = `${scoreAts}%`;

    // Quantified impact score
    const scoreQuant = data.quantified_impact_score || 0;
    document.getElementById('scoreQuant').textContent = `${scoreQuant}%`;
    document.getElementById('barQuant').style.width = `${scoreQuant}%`;

    // Summary Text
    document.getElementById('summaryText').textContent = data.summary_feedback || 'Analysis complete.';

    // Skill Badges
    const missingContainer = document.getElementById('missingSkillsPills');
    missingContainer.innerHTML = '';
    if (data.missing_critical_skills && data.missing_critical_skills.length > 0) {
        data.missing_critical_skills.forEach(skill => {
            const pill = document.createElement('span');
            pill.className = 'pill pill-amber';
            pill.textContent = skill;
            missingContainer.appendChild(pill);
        });
    } else {
        missingContainer.innerHTML = '<span class="text-muted" style="font-size: 0.8rem;">No critical missing skills detected! Great match.</span>';
    }

    const matchingContainer = document.getElementById('matchingSkillsPills');
    matchingContainer.innerHTML = '';
    if (data.present_matching_skills && data.present_matching_skills.length > 0) {
        data.present_matching_skills.forEach(skill => {
            const pill = document.createElement('span');
            pill.className = 'pill pill-green';
            pill.textContent = skill;
            matchingContainer.appendChild(pill);
        });
    } else {
        matchingContainer.innerHTML = '<span class="text-muted" style="font-size: 0.8rem;">No exact keyword matches found.</span>';
    }

    // Bullet Recommendations Cards
    const bulletCards = document.getElementById('bulletCards');
    bulletCards.innerHTML = '';

    if (data.bullet_improvements && data.bullet_improvements.length > 0) {
        data.bullet_improvements.forEach(b => {
            const card = document.createElement('div');
            card.className = 'diff-card';
            card.innerHTML = `
                <div class="diff-block diff-before">
                    <span class="diff-label">ORIGINAL BULLET</span>
                    <p>${escapeHtml(b.original)}</p>
                </div>
                <div class="diff-block diff-after">
                    <span class="diff-label">RECOMMENDED ATS REVISION</span>
                    <p>${escapeHtml(b.revised)}</p>
                </div>
                <div style="padding: 8px 12px; background: var(--bg-surface);">
                    <p class="reason-note">💡 ${escapeHtml(b.reason || 'Improved impact and action verbs.')}</p>
                </div>
            `;
            bulletCards.appendChild(card);
        });
    } else {
        bulletCards.innerHTML = '<p class="text-muted" style="font-size: 0.85rem;">Bullet points are already well quantified.</p>';
    }
}

// SINGLE BULLET OPTIMIZER TAB
function initSingleOptimizer() {
    const btn = document.getElementById('btnOptimizeSingle');
    const input = document.getElementById('singleBulletInput');
    const resultBox = document.getElementById('optimizerResult');
    const copyBtn = document.getElementById('btnCopyOpt');

    btn.addEventListener('click', async () => {
        const text = input.value.trim();
        if (!text) return;

        btn.disabled = true;
        btn.textContent = 'Optimizing...';

        try {
            const res = await fetch('/api/optimize-bullet', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ bullet: text })
            });
            const data = await res.json();

            if (data.success && data.result) {
                resultBox.classList.remove('hidden');
                document.getElementById('optOriginalText').textContent = data.result.original;
                document.getElementById('optRevisedText').textContent = data.result.revised;
                document.getElementById('optReasonText').textContent = '💡 ' + (data.result.reason || '');
            }
        } catch (e) {
            alert('Failed to optimize bullet.');
        } finally {
            btn.disabled = false;
            btn.textContent = 'Rewrite & Optimize';
        }
    });

    copyBtn.addEventListener('click', () => {
        const revised = document.getElementById('optRevisedText').textContent;
        navigator.clipboard.writeText(revised);
        copyBtn.textContent = 'Copied!';
        setTimeout(() => copyBtn.textContent = 'Copy Bullet', 2000);
    });
}

// SCAN HISTORY TABLE
async function loadScanHistory() {
    const tbody = document.getElementById('historyTableBody');
    try {
        const res = await fetch('/api/history');
        const data = await res.json();

        if (data.success && data.scans.length > 0) {
            tbody.innerHTML = '';
            data.scans.forEach(scan => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>#${scan.id}</td>
                    <td><strong>${escapeHtml(scan.target_job_title)}</strong></td>
                    <td>${escapeHtml(scan.filename || 'Upload')}</td>
                    <td><span class="pill pill-green">${scan.overall_match_score}%</span></td>
                    <td><span class="pill pill-amber">${scan.ats_formatting_score}%</span></td>
                    <td>${scan.analyzed_at ? scan.analyzed_at.substring(0, 16) : ''}</td>
                    <td><button class="btn btn-secondary btn-sm" onclick="viewHistoryItem(${scan.id})">View Report</button></td>
                `;
                tbody.appendChild(tr);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted">No scan history records found in database yet.</td></tr>';
        }
    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted">Could not load scan history.</td></tr>';
    }
}

async function viewHistoryItem(id) {
    try {
        const res = await fetch(`/api/analysis/${id}`);
        const data = await res.json();
        if (data.success) {
            // Switch tab to matcher & render
            document.querySelector('[data-tab="tab-analyze"]').click();
            renderDashboard(data);
        }
    } catch (e) {
        alert('Failed to load analysis record.');
    }
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}
