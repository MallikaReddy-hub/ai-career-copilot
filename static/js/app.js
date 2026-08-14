// AI Career Copilot - Frontend Application Logic

let lastAnalysisResult = null;
let currentUser = null;

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initAuth();
    initNavigation();
    initFileUpload();
    initFormSubmission();
    initSingleOptimizer();
    initCoverLetterGenerator();
    initExportAndCopyActions();
    checkAuthState();
});

// THEME TOGGLE (Dark / Light Mode)
function initTheme() {
    const toggleBtn = document.getElementById('themeToggleBtn');
    const sunIcon = toggleBtn.querySelector('.sun-icon');
    const moonIcon = toggleBtn.querySelector('.moon-icon');

    const savedTheme = localStorage.getItem('career_copilot_theme') || 'dark';
    applyTheme(savedTheme);

    toggleBtn.addEventListener('click', () => {
        const currentTheme = document.body.getAttribute('data-theme') || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        applyTheme(newTheme);
        localStorage.setItem('career_copilot_theme', newTheme);
        showToast(`Switched to ${newTheme === 'dark' ? 'Dark' : 'Light'} Mode`);
    });

    function applyTheme(theme) {
        document.body.setAttribute('data-theme', theme);
        if (theme === 'light') {
            sunIcon.classList.remove('hidden');
            moonIcon.classList.add('hidden');
        } else {
            sunIcon.classList.add('hidden');
            moonIcon.classList.remove('hidden');
        }
    }
}

// TOAST NOTIFICATIONS
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
        <span>${escapeHtml(message)}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// AUTHENTICATION MANAGEMENT
function initAuth() {
    const modal = document.getElementById('authModal');
    const btnOpen = document.getElementById('btnOpenAuthModal');
    const btnPromptOpen = document.getElementById('btnPromptSignIn');
    const btnClose = document.getElementById('btnCloseAuthModal');

    const tabSignIn = document.getElementById('tabBtnSignIn');
    const tabSignUp = document.getElementById('tabBtnSignUp');
    const formSignIn = document.getElementById('formSignIn');
    const formSignUp = document.getElementById('formSignUp');
    const authAlert = document.getElementById('authAlert');

    const btnLogout = document.getElementById('btnLogout');
    const btnGoogle = document.getElementById('btnGoogleAuth');

    // Open Modal
    function openModal(defaultTab = 'signin') {
        modal.classList.remove('hidden');
        authAlert.classList.add('hidden');
        if (defaultTab === 'signup') {
            switchToSignUp();
        } else {
            switchToSignIn();
        }
    }

    // Close Modal
    function closeModal() {
        modal.classList.add('hidden');
        authAlert.classList.add('hidden');
    }

    btnOpen?.addEventListener('click', () => openModal('signin'));
    btnPromptOpen?.addEventListener('click', () => openModal('signin'));
    btnClose?.addEventListener('click', closeModal);

    modal?.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    // Tab Switching
    function switchToSignIn() {
        tabSignIn.classList.add('active');
        tabSignUp.classList.remove('active');
        formSignIn.classList.remove('hidden');
        formSignUp.classList.add('hidden');
        document.getElementById('modalAuthTitle').textContent = 'Welcome to AI Career Copilot';
        document.getElementById('modalAuthSubtitle').textContent = 'Sign in to access your private resume evaluation history.';
        authAlert.classList.add('hidden');
    }

    function switchToSignUp() {
        tabSignUp.classList.add('active');
        tabSignIn.classList.remove('active');
        formSignUp.classList.remove('hidden');
        formSignIn.classList.add('hidden');
        document.getElementById('modalAuthTitle').textContent = 'Create Your Free Account';
        document.getElementById('modalAuthSubtitle').textContent = 'Save your tailored resumes, cover letters, and private scan reports.';
        authAlert.classList.add('hidden');
    }

    tabSignIn?.addEventListener('click', switchToSignIn);
    tabSignUp?.addEventListener('click', switchToSignUp);

    // Sign In Form Submission
    formSignIn?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value.trim();
        const password = document.getElementById('loginPassword').value.trim();
        const btn = document.getElementById('btnSubmitLogin');
        const spinner = document.getElementById('spinnerLogin');
        const btnText = btn.querySelector('.btn-text');

        btn.disabled = true;
        spinner.classList.remove('hidden');
        btnText.textContent = 'Signing in...';
        authAlert.classList.add('hidden');

        try {
            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            const data = await res.json();

            if (data.success && data.user) {
                currentUser = data.user;
                updateAuthUI();
                closeModal();
                showToast(`Welcome back, ${data.user.name || 'Candidate'}!`);
                loadScanHistory();
            } else {
                authAlert.textContent = data.error || 'Failed to sign in. Please check your credentials.';
                authAlert.classList.remove('hidden');
            }
        } catch (err) {
            authAlert.textContent = 'Network connection error: ' + err.message;
            authAlert.classList.remove('hidden');
        } finally {
            btn.disabled = false;
            spinner.classList.add('hidden');
            btnText.textContent = 'Sign In';
        }
    });

    // Sign Up Form Submission
    formSignUp?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('registerName').value.trim();
        const email = document.getElementById('registerEmail').value.trim();
        const password = document.getElementById('registerPassword').value.trim();
        const btn = document.getElementById('btnSubmitRegister');
        const spinner = document.getElementById('spinnerRegister');
        const btnText = btn.querySelector('.btn-text');

        btn.disabled = true;
        spinner.classList.remove('hidden');
        btnText.textContent = 'Creating account...';
        authAlert.classList.add('hidden');

        try {
            const res = await fetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password })
            });
            const data = await res.json();

            if (data.success && data.user) {
                currentUser = data.user;
                updateAuthUI();
                closeModal();
                showToast(`Account created! Welcome, ${data.user.name || 'Candidate'}!`);
                loadScanHistory();
            } else {
                authAlert.textContent = data.error || 'Failed to create account.';
                authAlert.classList.remove('hidden');
            }
        } catch (err) {
            authAlert.textContent = 'Network connection error: ' + err.message;
            authAlert.classList.remove('hidden');
        } finally {
            btn.disabled = false;
            spinner.classList.add('hidden');
            btnText.textContent = 'Create Account';
        }
    });

    // Google Sign In Button
    btnGoogle?.addEventListener('click', async () => {
        // Prompt for Google account email or use Google Identity Services
        const userEmail = prompt('Enter your Google email to sign in:');
        if (!userEmail || !userEmail.includes('@')) return;

        const userName = userEmail.split('@')[0];

        try {
            const res = await fetch('/api/auth/google', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: userEmail,
                    name: userName,
                    google_id: 'g_' + btoa(userEmail)
                })
            });
            const data = await res.json();

            if (data.success && data.user) {
                currentUser = data.user;
                updateAuthUI();
                closeModal();
                showToast(`Signed in with Google as ${data.user.name}!`);
                loadScanHistory();
            } else {
                alert(data.error || 'Google Sign-In failed.');
            }
        } catch (err) {
            alert('Google authentication error: ' + err.message);
        }
    });

    // Logout
    btnLogout?.addEventListener('click', async () => {
        try {
            await fetch('/api/auth/logout', { method: 'POST' });
            currentUser = null;
            updateAuthUI();
            showToast('Logged out successfully');
            loadScanHistory();
        } catch (e) {
            alert('Logout error.');
        }
    });
}

// Check if user is logged in
async function checkAuthState() {
    try {
        const res = await fetch('/api/auth/me');
        const data = await res.json();
        if (data.logged_in && data.user) {
            currentUser = data.user;
        } else {
            currentUser = null;
        }
    } catch (e) {
        currentUser = null;
    } finally {
        updateAuthUI();
        loadScanHistory();
    }
}

function updateAuthUI() {
    const loggedOutDiv = document.getElementById('authLoggedOut');
    const loggedInDiv = document.getElementById('authLoggedIn');
    const userNameSpan = document.getElementById('headerUserName');
    const userAvatar = document.getElementById('headerUserAvatar');

    if (currentUser) {
        loggedOutDiv?.classList.add('hidden');
        loggedInDiv?.classList.remove('hidden');
        if (userNameSpan) userNameSpan.textContent = currentUser.name || currentUser.email;
        if (userAvatar) userAvatar.textContent = (currentUser.name || currentUser.email).charAt(0).toUpperCase();
    } else {
        loggedOutDiv?.classList.remove('hidden');
        loggedInDiv?.classList.add('hidden');
    }
}

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
        btnSubmit.disabled = true;

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                lastAnalysisResult = data;
                renderDashboard(data);
                showToast('ATS Match Analysis Complete!');
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
        } else if (scoreOverall >= 60) {
            hintOverall.textContent = "Good Match (Add missing skills)";
            hintOverall.style.color = "var(--accent-amber)";
        } else {
            hintOverall.textContent = "Needs Revision (Add keywords)";
            hintOverall.style.color = "var(--accent-red)";
        }
    }

    // ATS Readability score
    const scoreAts = data.ats_formatting_score || 0;
    document.getElementById('scoreAts').textContent = `${scoreAts}%`;
    document.getElementById('barAts').style.width = `${scoreAts}%`;

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

    // Bullet Recommendations Cards with individual Copy buttons
    const bulletCards = document.getElementById('bulletCards');
    bulletCards.innerHTML = '';

    if (data.bullet_improvements && data.bullet_improvements.length > 0) {
        data.bullet_improvements.forEach((b, index) => {
            const card = document.createElement('div');
            card.className = 'diff-card';
            card.innerHTML = `
                <div class="diff-block diff-before">
                    <span class="diff-label">ORIGINAL BULLET</span>
                    <p>${escapeHtml(b.original)}</p>
                </div>
                <div class="diff-block diff-after">
                    <div class="diff-header-row">
                        <span class="diff-label">RECOMMENDED ATS REVISION</span>
                        <button class="btn btn-secondary btn-xs" data-copy-bullet="${index}">Copy</button>
                    </div>
                    <p id="bulletRev_${index}">${escapeHtml(b.revised)}</p>
                </div>
                <div class="reason-container">
                    <p class="reason-note">💡 ${escapeHtml(b.reason || 'Improved impact and action verbs.')}</p>
                </div>
            `;
            bulletCards.appendChild(card);
        });

        bulletCards.querySelectorAll('[data-copy-bullet]').forEach(btn => {
            btn.addEventListener('click', () => {
                const idx = btn.getAttribute('data-copy-bullet');
                const textElem = document.getElementById(`bulletRev_${idx}`);
                if (textElem) {
                    navigator.clipboard.writeText(textElem.textContent.trim());
                    showToast('Optimized bullet copied to clipboard!');
                    btn.textContent = 'Copied!';
                    setTimeout(() => btn.textContent = 'Copy', 2000);
                }
            });
        });
    } else {
        bulletCards.innerHTML = '<p class="text-muted" style="font-size: 0.85rem;">Bullet points are already well formatted.</p>';
    }
}

// EXPORT & COPY ACTION HANDLERS
function initExportAndCopyActions() {
    // Export PDF Report
    document.getElementById('btnExportPdf')?.addEventListener('click', () => {
        window.print();
    });

    // Copy Full Report Summary
    document.getElementById('btnCopyReport')?.addEventListener('click', () => {
        if (!lastAnalysisResult) {
            showToast('No active report to copy.');
            return;
        }

        const missing = (lastAnalysisResult.missing_critical_skills || []).join(', ') || 'None';
        const matching = (lastAnalysisResult.present_matching_skills || []).join(', ') || 'None';
        const report = `AI Career Copilot - ATS Match Report
Job Role: ${lastAnalysisResult.target_job_title || 'Software Engineer'}
Match Score: ${lastAnalysisResult.overall_match_score || 0}%
ATS Readability: ${lastAnalysisResult.ats_formatting_score || 0}%

Summary Verdict:
${lastAnalysisResult.summary_feedback || ''}

Matching Skills: ${matching}
Missing Critical Skills: ${missing}
`;
        navigator.clipboard.writeText(report);
        showToast('Analysis report copied to clipboard!');
    });

    // Copy Missing Skills List
    document.getElementById('btnCopyMissing')?.addEventListener('click', () => {
        if (!lastAnalysisResult || !lastAnalysisResult.missing_critical_skills || lastAnalysisResult.missing_critical_skills.length === 0) {
            showToast('No missing skills to copy.');
            return;
        }
        const skillsList = lastAnalysisResult.missing_critical_skills.join(', ');
        navigator.clipboard.writeText(skillsList);
        showToast('Missing skills copied to clipboard!');
    });

    // Transfer from Dashboard to Cover Letter Generator
    document.getElementById('btnTransferToCoverLetter')?.addEventListener('click', () => {
        if (!lastAnalysisResult) return;

        document.getElementById('navCoverLetter').click();

        const targetRoleInput = document.getElementById('clTargetRole');
        const resumeInput = document.getElementById('clResumeText');
        const jdInput = document.getElementById('clJobDesc');

        if (targetRoleInput) targetRoleInput.value = lastAnalysisResult.target_job_title || 'Software Engineer';
        if (resumeInput) {
            const skills = (lastAnalysisResult.present_matching_skills || []).join(', ');
            resumeInput.value = `Target Role: ${lastAnalysisResult.target_job_title || 'Software Engineer'}\nKey Skills: ${skills}\nMatch Score: ${lastAnalysisResult.overall_match_score || 0}%`;
        }
        if (jdInput) {
            const formJd = document.getElementById('jobDescription');
            if (formJd && formJd.value) jdInput.value = formJd.value;
        }
    });
}

// SINGLE BULLET OPTIMIZER TAB
function initSingleOptimizer() {
    const btn = document.getElementById('btnOptimizeSingle');
    const input = document.getElementById('singleBulletInput');
    const resultBox = document.getElementById('optimizerResult');
    const copyBtn = document.getElementById('btnCopyOpt');
    const spinner = document.getElementById('spinnerBullet');
    const btnText = btn.querySelector('.btn-text');

    btn.addEventListener('click', async () => {
        const text = input.value.trim();
        if (!text) {
            alert('Please paste a bullet point from your resume to optimize.');
            return;
        }

        btn.disabled = true;
        if (spinner) spinner.classList.remove('hidden');
        if (btnText) btnText.textContent = 'Optimizing...';

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
                showToast('Bullet successfully optimized!');
            } else {
                alert(data.error || 'Failed to optimize bullet point.');
            }
        } catch (e) {
            alert('Failed to optimize bullet.');
        } finally {
            btn.disabled = false;
            if (spinner) spinner.classList.add('hidden');
            if (btnText) btnText.textContent = 'Rewrite & Optimize Bullet';
        }
    });

    copyBtn.addEventListener('click', () => {
        const revised = document.getElementById('optRevisedText').textContent;
        navigator.clipboard.writeText(revised);
        showToast('Optimized bullet copied to clipboard!');
        copyBtn.textContent = 'Copied!';
        setTimeout(() => copyBtn.textContent = 'Copy', 2000);
    });
}

// COVER LETTER GENERATOR TAB
function initCoverLetterGenerator() {
    const btnGenerate = document.getElementById('btnGenerateCoverLetter');
    const resultArea = document.getElementById('coverLetterResult');
    const btnCopy = document.getElementById('btnCopyCoverLetter');
    const btnDownload = document.getElementById('btnDownloadCoverLetter');
    const spinner = document.getElementById('spinnerCl');
    const btnText = btnGenerate.querySelector('.btn-text');

    btnGenerate.addEventListener('click', async () => {
        const role = document.getElementById('clTargetRole').value.trim() || 'Software Engineer';
        const tone = document.getElementById('clTone').value;
        const resumeText = document.getElementById('clResumeText').value.trim();
        const jobDesc = document.getElementById('clJobDesc').value.trim();

        if (!resumeText && !jobDesc) {
            alert('Please provide your experience summary or the target job description.');
            return;
        }

        btnGenerate.disabled = true;
        if (spinner) spinner.classList.remove('hidden');
        if (btnText) btnText.textContent = 'Generating Cover Letter...';

        try {
            const res = await fetch('/api/cover-letter', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    target_job_title: role,
                    tone: tone,
                    resume_text: resumeText,
                    job_description: jobDesc
                })
            });

            const data = await res.json();
            if (data.success && data.cover_letter) {
                resultArea.value = data.cover_letter;
                btnCopy.disabled = false;
                btnDownload.disabled = false;
                showToast('Tailored cover letter generated!');
            } else {
                alert('Generation Error: ' + (data.error || 'Failed to generate cover letter.'));
            }
        } catch (e) {
            alert('Failed to generate cover letter: ' + e.message);
        } finally {
            btnGenerate.disabled = false;
            if (spinner) spinner.classList.add('hidden');
            if (btnText) btnText.textContent = 'Generate Tailored Cover Letter';
        }
    });

    btnCopy.addEventListener('click', () => {
        if (!resultArea.value) return;
        navigator.clipboard.writeText(resultArea.value);
        showToast('Cover letter copied to clipboard!');
    });

    btnDownload.addEventListener('click', () => {
        if (!resultArea.value) return;
        const blob = new Blob([resultArea.value], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'Cover_Letter.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        showToast('Cover letter downloaded as Cover_Letter.txt');
    });
}

// PRIVATE SCAN HISTORY TABLE
async function loadScanHistory() {
    const tbody = document.getElementById('historyTableBody');
    const promptBox = document.getElementById('historyAuthPrompt');
    const tableWrapper = document.getElementById('historyTableWrapper');

    if (!currentUser) {
        promptBox?.classList.remove('hidden');
        tableWrapper?.classList.add('hidden');
        return;
    }

    promptBox?.classList.add('hidden');
    tableWrapper?.classList.remove('hidden');

    try {
        const res = await fetch('/api/history');
        const data = await res.json();

        if (data.success && data.scans && data.scans.length > 0) {
            tbody.innerHTML = '';
            data.scans.forEach(scan => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>#${scan.id}</td>
                    <td><strong>${escapeHtml(scan.target_job_title)}</strong></td>
                    <td>${escapeHtml(scan.filename || 'Upload')}</td>
                    <td><span class="pill pill-green">${scan.overall_match_score}%</span></td>
                    <td><span class="pill pill-blue">${scan.ats_formatting_score}%</span></td>
                    <td>${scan.analyzed_at ? scan.analyzed_at.substring(0, 16) : ''}</td>
                    <td><button class="btn btn-secondary btn-sm" onclick="window.viewHistoryItem(${scan.id})">View Report</button></td>
                `;
                tbody.appendChild(tr);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted">No scan history records found for your account yet. Run an ATS analysis to save your first private report!</td></tr>';
        }
    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted">Could not load private scan history.</td></tr>';
    }
}

async function viewHistoryItem(id) {
    try {
        const res = await fetch(`/api/analysis/${id}`);
        const data = await res.json();
        if (data.success) {
            lastAnalysisResult = data;
            document.querySelector('[data-tab="tab-analyze"]').click();
            renderDashboard(data);
            showToast(`Loaded Report #${id}`);
        }
    } catch (e) {
        alert('Failed to load analysis record.');
    }
}

window.viewHistoryItem = viewHistoryItem;

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}
