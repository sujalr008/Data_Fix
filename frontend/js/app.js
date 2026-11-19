/**
 * DataFix Master Application Coordinator
 * Connects UI interactions, 3D animations, Speedometer HUD (0-100 scale),
 * Authentication Gateway (Student vs Admin), Layer-1 Option Cards, and Autonomous Workflows.
 */

document.addEventListener("DOMContentLoaded", async () => {
  console.log("Initializing DataFix Autonomous Quality & Repair Engine...");

  // 1. Initialize Subsystems
  if (window.threeScene) window.threeScene.init();
  if (window.telemetry) window.telemetry.init();

  // 2. Setup Authentication Gateway & Role Logic
  setupAuthGateway();

  // 3. Setup Navigation & Actions
  setupGlobalNav();

  // 4. Setup Layer-1 Option Cards
  setupLayer1OptionCards();

  // 5. Setup Layer-2 Modals & Form Actions
  setupLayer2Modals();

  // 6. Setup Bulk Upload Dropzone & Reset
  setupFileDropzone();

  // 7. Setup Nitro Booster (0-100 Scale)
  setupNitroBooster();

  // 8. Restore Active Session if Present
  const activeUser = getActiveUserSession();
  if (activeUser) {
    applyUserRoleView(activeUser);
    await window.DataFixAPI.getHealth();
    const activeData = window.CollegeDataService.getInitialData();
    if (activeData && activeData.length > 0) {
      await window.DataFixAPI.uploadFile(activeData, "csv");
    }
    refreshDashboardTelemetry();
  } else {
    showAuthScreen();
  }
});

/**
 * -------------------------------------------------------------
 * Authentication Gateway & Role Routing
 * -------------------------------------------------------------
 */
function setupAuthGateway() {
  const tabStudent = document.getElementById("tab-btn-student");
  const tabAdmin = document.getElementById("tab-btn-admin");
  const studentForm = document.getElementById("student-auth-form");
  const adminForm = document.getElementById("admin-auth-form");

  if (tabStudent && tabAdmin) {
    tabStudent.addEventListener("click", () => {
      tabStudent.classList.add("active");
      tabAdmin.classList.remove("active");
      if (studentForm) studentForm.style.display = "block";
      if (adminForm) adminForm.style.display = "none";
    });

    tabAdmin.addEventListener("click", () => {
      tabAdmin.classList.add("active");
      tabStudent.classList.remove("active");
      if (adminForm) adminForm.style.display = "block";
      if (studentForm) studentForm.style.display = "none";
    });
  }

  // Student Form Submit
  if (studentForm) {
    studentForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const name = document.getElementById("auth-student-name").value.trim();
      const age = document.getElementById("auth-student-age").value.trim();
      const phone = document.getElementById("auth-student-phone").value.trim();
      const dept = document.getElementById("auth-student-dept").value;
      const sem = document.getElementById("auth-student-sem").value;
      const year = document.getElementById("auth-student-year").value;
      const section = document.getElementById("auth-student-section").value;

      const userSession = {
        role: "student",
        name,
        age,
        phoneNumber: phone,
        department: dept,
        semester: sem,
        year,
        section
      };

      saveActiveUserSession(userSession);
      applyUserRoleView(userSession);

      // Submit student intake record into active database
      await window.DataFixAPI.insertSingleRecord({
        name,
        age,
        phoneNumber: phone,
        department: dept,
        semester: sem,
        year,
        section
      });

      refreshDashboardTelemetry();
      showToast(`Welcome, ${name}! Logged into Student Portal.`, "success");
      if (window.telemetry) window.telemetry.playSuccessChime();
    });
  }

  // Admin Form Submit (Only Admin Name, Department Name, and Year)
  if (adminForm) {
    adminForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const name = document.getElementById("auth-admin-name").value.trim();
      const dept = document.getElementById("auth-admin-dept").value;
      const year = document.getElementById("auth-admin-year").value.trim();

      const userSession = {
        role: "admin",
        name,
        department: dept,
        year
      };

      saveActiveUserSession(userSession);
      applyUserRoleView(userSession);
      refreshDashboardTelemetry();

      showToast(`Welcome, Admin ${name}! Full Dataset Management Unlocked.`, "success");
      if (window.telemetry) window.telemetry.playSuccessChime();
    });
  }

  // Sign Out Button
  const signoutBtn = document.getElementById("nav-signout-btn");
  if (signoutBtn) {
    signoutBtn.addEventListener("click", () => {
      clearActiveUserSession();
      showAuthScreen();
      showToast("Signed out. Select role to log in again.", "info");
    });
  }
}

function showAuthScreen() {
  const authView = document.getElementById("auth-view");
  const mainDash = document.getElementById("main-dashboard");
  if (authView) authView.style.display = "flex";
  if (mainDash) mainDash.style.display = "none";
}

function applyUserRoleView(user) {
  const authView = document.getElementById("auth-view");
  const mainDash = document.getElementById("main-dashboard");
  if (authView) authView.style.display = "none";
  if (mainDash) mainDash.style.display = "block";

  const navBadge = document.getElementById("nav-user-badge");
  const navUserIcon = document.getElementById("nav-user-icon");
  const navUserLabel = document.getElementById("nav-user-label");
  const banner = document.getElementById("dashboard-role-banner");
  const bannerLeft = document.getElementById("banner-text-left");
  const bannerRight = document.getElementById("banner-text-right");
  const bulkCard = document.getElementById("card-bulk-engine");
  const bulkZone = document.getElementById("bulk-upload-zone");

  if (user.role === "admin") {
    // ADMIN DASHBOARD
    if (navBadge) navBadge.style.borderColor = "rgba(157, 78, 221, 0.4)";
    if (navUserIcon) navUserIcon.textContent = "🛡️";
    if (navUserLabel) navUserLabel.textContent = `Admin: ${user.name}`;

    if (banner) {
      banner.className = "role-banner admin";
      if (bannerLeft) bannerLeft.innerHTML = `🛡️ <strong>Organisation Admin Control Center</strong> — ${user.name} (${user.department} | Batch: ${user.year})`;
      if (bannerRight) bannerRight.innerHTML = `<span>Institutional Bulk Ingestion & Deep Auto-Repair Active</span>`;
    }

    // Admin CAN upload huge bulk datasets
    if (bulkCard) bulkCard.style.display = "flex";
    if (bulkZone) bulkZone.style.display = "block";

  } else {
    // STUDENT DASHBOARD
    if (navBadge) navBadge.style.borderColor = "rgba(0, 245, 160, 0.4)";
    if (navUserIcon) navUserIcon.textContent = "👤";
    if (navUserLabel) navUserLabel.textContent = `Student: ${user.name}`;

    if (banner) {
      banner.className = "role-banner student";
      if (bannerLeft) bannerLeft.innerHTML = `👤 <strong>Student Portal</strong> — ${user.name} (${user.department} | Year ${user.year || 2}, Sem ${user.semester || 4}, Sec ${user.section || 'A'})`;
      if (bannerRight) bannerRight.innerHTML = `<span>Personal Intake & Category Purity Telemetry</span>`;
    }

    // Student CANNOT upload huge bulk datasets (Only individual intake & category review)
    if (bulkCard) bulkCard.style.display = "none";
    if (bulkZone) bulkZone.style.display = "none";
  }
}

function saveActiveUserSession(user) {
  sessionStorage.setItem("datafix_active_user", JSON.stringify(user));
}

function getActiveUserSession() {
  const raw = sessionStorage.getItem("datafix_active_user");
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch (e) {
    return null;
  }
}

function clearActiveUserSession() {
  sessionStorage.removeItem("datafix_active_user");
}

/**
 * -------------------------------------------------------------
 * UI Updates & Telemetry Sync (0-100 Scale)
 * -------------------------------------------------------------
 */
function refreshDashboardTelemetry() {
  const dataset = window.DataFixAPI.currentDataset || [];
  const issues = window.DataFixAPI.currentIssues || [];
  const diff = window.DataFixAPI.currentDiff || [];
  const qualityScore = dataset.length > 0 ? (window.DataFixAPI.qualityScore || 0) : 0;

  // Update Hero Metric Badges
  const scoreElem = document.getElementById("hero-quality-score");
  const totalElem = document.getElementById("hero-total-records");
  const anomalyElem = document.getElementById("hero-anomaly-count");
  const healedElem = document.getElementById("hero-healed-count");

  if (scoreElem) scoreElem.textContent = dataset.length > 0 ? `${qualityScore}%` : "--";
  if (totalElem) totalElem.textContent = dataset.length;
  if (anomalyElem) anomalyElem.textContent = issues.length;
  if (healedElem) healedElem.textContent = diff.length;

  // Update Speedometer HUD (0 to 100 Scale)
  if (window.telemetry) {
    window.telemetry.updateDisplay(qualityScore, false);
  }
}

/**
 * -------------------------------------------------------------
 * Navigation & WebApp Launch Actions
 * -------------------------------------------------------------
 */
function setupGlobalNav() {
  // Sound Toggle Button
  const soundBtn = document.getElementById("sound-toggle-btn");
  if (soundBtn) {
    soundBtn.addEventListener("click", () => {
      const isEnabled = window.telemetry.toggleSound();
      soundBtn.textContent = isEnabled ? "🔊" : "🔇";
      showToast(isEnabled ? "Turbo Sound Effects: Active" : "Turbo Sound Effects: Muted", "info");
    });
  }

  // PWA & Service Worker Registration
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("./service-worker.js").catch((err) => {
      console.warn("ServiceWorker registration notice:", err);
    });
  }

  // PWA & Web Application Installer Setup
  let deferredInstallPrompt = null;
  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferredInstallPrompt = e;
  });

  // TOP-RIGHT WEB APPLICATION LAUNCH / DOWNLOAD BUTTON
  const launchWebAppBtn = document.getElementById("launch-webapp-btn");
  if (launchWebAppBtn) {
    launchWebAppBtn.addEventListener("click", async () => {
      // 1. If native PWA install prompt is ready, trigger browser installation prompt
      if (deferredInstallPrompt) {
        deferredInstallPrompt.prompt();
        const choice = await deferredInstallPrompt.userChoice;
        if (choice.outcome === "accepted") {
          showToast("✓ DataFix App installed successfully to your device!", "success");
        }
        deferredInstallPrompt = null;
        return;
      }

      // 2. Download Windows Desktop Application Launcher / Installer
      const currentUrl = window.location.href;
      const batContent = `@echo off\r\ntitle DataFix Autonomous Application\r\necho Launching DataFix Desktop Application...\r\nif exist "%ProgramFiles%\\Google\\Chrome\\Application\\chrome.exe" (\r\n    start "" "%ProgramFiles%\\Google\\Chrome\\Application\\chrome.exe" --app="${currentUrl}"\r\n) else if exist "%ProgramFiles(x86)%\\Microsoft\\Edge\\Application\\msedge.exe" (\r\n    start "" "%ProgramFiles(x86)%\\Microsoft\\Edge\\Application\\msedge.exe" --app="${currentUrl}"\r\n) else (\r\n    start "" "${currentUrl}"\r\n)\r\nexit\r\n`;

      const blob = new Blob([batContent], { type: "application/bat" });
      const downloadLink = document.createElement("a");
      downloadLink.href = URL.createObjectURL(blob);
      downloadLink.download = "DataFix-Desktop-App.bat";
      document.body.appendChild(downloadLink);
      downloadLink.click();
      setTimeout(() => {
        document.body.removeChild(downloadLink);
        URL.revokeObjectURL(downloadLink.href);
      }, 300);

      // 3. Simultaneously launch standalone desktop window
      const appWindow = window.open(
        currentUrl,
        "DataFixApp",
        "width=1280,height=820,menubar=no,toolbar=no,location=no,status=no,resizable=yes,scrollbars=yes"
      );

      showToast("📥 DataFix Desktop App installer downloaded & standalone window launched!", "success");
    });
  }
}

/**
 * -------------------------------------------------------------
 * Layer-1 Option Cards Setup
 * -------------------------------------------------------------
 */
function setupLayer1OptionCards() {
  // Card 1: Enter Your Data
  const cardEnter = document.getElementById("card-enter-data");
  if (cardEnter) {
    cardEnter.addEventListener("click", () => {
      // Pre-fill user data if student
      const user = getActiveUserSession();
      if (user && user.role === "student") {
        if (document.getElementById("intake-name")) document.getElementById("intake-name").value = user.name || "";
        if (document.getElementById("intake-age")) document.getElementById("intake-age").value = user.age || "";
        if (document.getElementById("intake-phone")) document.getElementById("intake-phone").value = user.phoneNumber || "";
        if (document.getElementById("intake-dept")) document.getElementById("intake-dept").value = user.department || "Computer Science";
        if (document.getElementById("intake-sem")) document.getElementById("intake-sem").value = user.semester || "4";
        if (document.getElementById("intake-year")) document.getElementById("intake-year").value = user.year || "2";
        if (document.getElementById("intake-section")) document.getElementById("intake-section").value = user.section || "A";
      }
      openModal("modal-enter-data");
    });
  }

  // Card 2: Continuous Data Quality Checks
  const cardQuality = document.getElementById("card-quality-checks");
  if (cardQuality) {
    cardQuality.addEventListener("click", async () => {
      await populateQualityChecksModal();
      openModal("modal-quality-checks");
    });
  }

  // Card 3: Recheck & Correct Specific Category
  const cardRecheck = document.getElementById("card-recheck-category");
  if (cardRecheck) {
    cardRecheck.addEventListener("click", () => {
      populateCategoryDropdowns();
      updateCategoryPreview();
      openModal("modal-recheck-category");
    });
  }

  // Card 4: History of All Changes in Category
  const cardHistory = document.getElementById("card-history-changes");
  if (cardHistory) {
    cardHistory.addEventListener("click", () => {
      populateHistoryModal();
      openModal("modal-history-changes");
    });
  }

  // Card 5: Download Specific Category Records
  const cardDownload = document.getElementById("card-download-category");
  if (cardDownload) {
    cardDownload.addEventListener("click", () => {
      populateDownloadDropdowns();
      openModal("modal-download-category");
    });
  }

  // Card 6: Autonomous Bulk Engine (ADMIN ONLY)
  const cardBulk = document.getElementById("card-bulk-engine");
  if (cardBulk) {
    cardBulk.addEventListener("click", () => {
      const dropzone = document.getElementById("bulk-upload-zone");
      if (dropzone) {
        dropzone.scrollIntoView({ behavior: "smooth" });
        dropzone.classList.add("dragover");
        setTimeout(() => dropzone.classList.remove("dragover"), 800);
      }
    });
  }
}

/**
 * -------------------------------------------------------------
 * Layer-2 Modals & Forms
 * -------------------------------------------------------------
 */
function setupLayer2Modals() {
  document.querySelectorAll("[data-close]").forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-close");
      if (targetId) closeModal(targetId);
    });
  });

  document.querySelectorAll(".modal-overlay").forEach(overlay => {
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) {
        closeModal(overlay.id);
      }
    });
  });

  // Modal 1: Intake Form Submission
  const intakeForm = document.getElementById("intake-form");
  if (intakeForm) {
    intakeForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const name = document.getElementById("intake-name").value.trim();
      const age = document.getElementById("intake-age").value.trim();
      const phone = document.getElementById("intake-phone").value.trim();
      const email = document.getElementById("intake-email").value.trim();
      const dept = document.getElementById("intake-dept").value;
      const sem = document.getElementById("intake-sem").value;
      const year = document.getElementById("intake-year").value;
      const section = document.getElementById("intake-section").value;

      const record = {
        name,
        age,
        phoneNumber: phone,
        email,
        department: dept,
        semester: sem,
        year,
        section
      };

      await window.DataFixAPI.insertSingleRecord(record);
      refreshDashboardTelemetry();
      closeModal("modal-enter-data");
      intakeForm.reset();

      showToast(`Record for ${name} submitted and verified!`, "success");
      if (window.telemetry) window.telemetry.playSuccessChime();
    });
  }

  // Modal 2: Quality Checks -> View AI Insights
  const viewInsightsBtn = document.getElementById("qc-view-ai-insights-btn");
  if (viewInsightsBtn) {
    viewInsightsBtn.addEventListener("click", async () => {
      closeModal("modal-quality-checks");
      await populateAIInsightsModal();
      openModal("modal-ai-insights");
    });
  }

  // Modal 3: Category Recheck & Auto-Repair Execution
  const deptSelect = document.getElementById("recheck-dept-select");
  const secSelect = document.getElementById("recheck-section-select");
  if (deptSelect && secSelect) {
    deptSelect.addEventListener("change", () => updateCategoryPreview());
    secSelect.addEventListener("change", () => updateCategoryPreview());
  }

  const execRepairBtn = document.getElementById("category-execute-repair-btn");
  if (execRepairBtn) {
    execRepairBtn.addEventListener("click", async () => {
      const dept = deptSelect ? deptSelect.value : "all";
      const sec = secSelect ? secSelect.value : "all";

      execRepairBtn.disabled = true;
      execRepairBtn.textContent = "⏳ Healing Anomalies...";

      if (window.telemetry) window.telemetry.playRevSFX(95);

      const repairResult = await window.DataFixAPI.applyRepair(window.DataFixAPI.activeSessionId, {
        fixMissing: true,
        removeDuplicates: true,
        fixFormats: true,
        fixOutliers: true
      });

      refreshDashboardTelemetry();
      updateCategoryPreview();

      const feedback = document.getElementById("category-repair-feedback");
      if (feedback) {
        feedback.textContent = `✓ Auto-repaired ${repairResult.data.repairCount} issues. New quality score: ${repairResult.data.newQualityScore}%`;
      }

      execRepairBtn.disabled = false;
      execRepairBtn.textContent = "⚡ Clean & Repair This Category";

      showToast(`Category [${dept} / Sec ${sec}] successfully repaired!`, "success");
      if (window.telemetry) window.telemetry.playSuccessChime();
    });
  }

  // Modal 4: History Search & Category Filter
  const histFilter = document.getElementById("history-category-filter");
  const histSearch = document.getElementById("history-search-input");
  if (histFilter) histFilter.addEventListener("change", () => renderHistoryRows());
  if (histSearch) histSearch.addEventListener("input", () => renderHistoryRows());

  // Modal 5: Download Category Confirm
  const downloadConfirmBtn = document.getElementById("download-confirm-btn");
  if (downloadConfirmBtn) {
    downloadConfirmBtn.addEventListener("click", async () => {
      const dept = document.getElementById("download-dept-select").value;
      const sec = document.getElementById("download-section-select").value;
      const format = document.getElementById("download-format-select").value;

      await window.DataFixAPI.downloadFile(window.DataFixAPI.activeSessionId, format, {
        department: dept,
        section: sec
      });

      closeModal("modal-download-category");
      showToast(`Exported ${format.toUpperCase()} dataset for ${dept} (Sec: ${sec})`, "success");
    });
  }

  // Modal 7: Diff Inspector -> Certificate View
  const diffCertBtn = document.getElementById("diff-view-cert-btn");
  if (diffCertBtn) {
    diffCertBtn.addEventListener("click", () => {
      closeModal("modal-diff-inspector");
      openModal("modal-certificate");
    });
  }

  // Modal 8: Print Certificate
  const printCertBtn = document.getElementById("cert-print-btn");
  if (printCertBtn) {
    printCertBtn.addEventListener("click", () => {
      window.print();
    });
  }
}

/**
 * -------------------------------------------------------------
 * File Dropzone (Admin Only) & Clear Action
 * -------------------------------------------------------------
 */
function setupFileDropzone() {
  const dropzone = document.getElementById("bulk-upload-zone");
  const fileInput = document.getElementById("file-input-elem");
  const browseBtn = document.getElementById("browse-files-btn");

  if (browseBtn && fileInput) {
    browseBtn.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", async (e) => {
      if (e.target.files && e.target.files[0]) {
        handleIncomingFile(e.target.files[0]);
      }
    });
  }

  if (dropzone) {
    ["dragenter", "dragover"].forEach(name => {
      dropzone.addEventListener(name, (e) => {
        e.preventDefault();
        dropzone.classList.add("dragover");
      });
    });

    ["dragleave", "drop"].forEach(name => {
      dropzone.addEventListener(name, (e) => {
        e.preventDefault();
        dropzone.classList.remove("dragover");
      });
    });

    dropzone.addEventListener("drop", (e) => {
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleIncomingFile(e.dataTransfer.files[0]);
      }
    });
  }

  // Clear / Reset Database Button
  const clearDbBtn = document.getElementById("clear-database-btn");
  if (clearDbBtn) {
    clearDbBtn.addEventListener("click", () => {
      window.DataFixAPI.clearActiveData();
      refreshDashboardTelemetry();
      updateCategoryPreview();
      showToast("Database reset. 0 records stored. Ready for new file upload.", "info");
    });
  }
}

async function handleIncomingFile(file) {
  showToast(`Parsing and analyzing ${file.name}...`, "info");
  const fileExt = file.name.split(".").pop().toLowerCase();
  const res = await window.DataFixAPI.uploadFile(file, fileExt);

  refreshDashboardTelemetry();
  showToast(`Dataset loaded: ${res.data.rowCount} rows. Detected ${res.data.issueCount} anomalies.`, "success");

  setTimeout(async () => {
    await populateAIInsightsModal();
    openModal("modal-ai-insights");
  }, 600);
}

/**
 * -------------------------------------------------------------
 * Nitro Booster (0 - 100 Scale)
 * -------------------------------------------------------------
 */
function setupNitroBooster() {
  const boosterBtn = document.getElementById("nitro-booster-btn");
  if (boosterBtn) {
    boosterBtn.addEventListener("click", () => {
      const dataset = window.DataFixAPI.currentDataset || [];
      if (dataset.length === 0) {
        showToast("No dataset loaded. Enter your data or upload a file first!", "warning");
        return;
      }

      showToast("🔥 NITRO BOOSTER ENGAGED! Boosting Quality to 100%...", "warning");
      window.telemetry.triggerBoost(async () => {
        const repairResult = await window.DataFixAPI.applyRepair(window.DataFixAPI.activeSessionId);
        refreshDashboardTelemetry();
        showToast("✓ Boost Complete! Quality boosted to 100%. Opening Diff Inspector...", "success");

        setTimeout(() => {
          populateDiffInspectorModal();
          openModal("modal-diff-inspector");
        }, 400);
      });
    });
  }
}

/**
 * -------------------------------------------------------------
 * Modal Helpers & View Rendering
 * -------------------------------------------------------------
 */
async function populateQualityChecksModal() {
  const issues = window.DataFixAPI.currentIssues || [];

  const missing = issues.filter(i => i.type === "missing_values").length;
  const dups = issues.filter(i => i.type === "duplicates").length;
  const formats = issues.filter(i => i.type === "format_errors").length;
  const outliers = issues.filter(i => i.type === "outliers").length;

  document.getElementById("qc-missing-count").textContent = missing;
  document.getElementById("qc-dup-count").textContent = dups;
  document.getElementById("qc-format-count").textContent = formats;
  document.getElementById("qc-outlier-count").textContent = outliers;

  const tbody = document.querySelector("#qc-columns-table tbody");
  if (tbody) {
    tbody.innerHTML = "";
    const report = await window.DataFixAPI.getReport();
    const cols = report.data.columnAnalysis || [];

    if (cols.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: #64748b; padding: 24px;">No dataset loaded. Submit a record or upload a file to view completeness.</td></tr>`;
      return;
    }

    cols.forEach(col => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td style="color: #ffffff; font-weight: 600;">${col.column}</td>
        <td style="color: #94a3b8;">${col.type}</td>
        <td>
          <span style="color: ${col.issues > 0 ? '#ff0054' : '#00f5a0'}; font-weight: 700;">
            ${col.issues} issue${col.issues === 1 ? '' : 's'}
          </span>
        </td>
        <td>
          <div style="display: flex; align-items: center; gap: 8px;">
            <div style="flex: 1; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden;">
              <div style="width: ${col.completeness}%; height: 100%; background: #00f3ff;"></div>
            </div>
            <span>${col.completeness}%</span>
          </div>
        </td>
      `;
      tbody.appendChild(tr);
    });
  }
}

function populateCategoryDropdowns() {
  const dataset = window.DataFixAPI.currentDataset || [];
  const deptSelect = document.getElementById("recheck-dept-select");
  const secSelect = document.getElementById("recheck-section-select");

  if (deptSelect) {
    const depts = window.CollegeDataService.getDepartments(dataset);
    deptSelect.innerHTML = `<option value="all">All Departments</option>` +
      depts.map(d => `<option value="${d}">${d}</option>`).join("");
  }

  if (secSelect) {
    const secs = window.CollegeDataService.getSections(dataset);
    secSelect.innerHTML = `<option value="all">All Sections</option>` +
      secs.map(s => `<option value="${s}">Section ${s}</option>`).join("");
  }
}

function updateCategoryPreview() {
  const dataset = window.DataFixAPI.currentDataset || [];
  const dept = document.getElementById("recheck-dept-select") ? document.getElementById("recheck-dept-select").value : "all";
  const sec = document.getElementById("recheck-section-select") ? document.getElementById("recheck-section-select").value : "all";

  const filtered = window.CollegeDataService.filterByCategory(dataset, { department: dept, section: sec });
  const summary = document.getElementById("category-records-summary");
  if (summary) {
    summary.textContent = `Showing ${filtered.length} records for: ${dept === "all" ? "All Departments" : dept} ${sec === "all" ? "" : "(Sec " + sec + ")"}`;
  }

  const tbody = document.querySelector("#category-preview-table tbody");
  if (tbody) {
    tbody.innerHTML = "";
    if (filtered.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: #64748b; padding: 28px;">No records in database. Enter a record or upload an Excel/CSV file to view.</td></tr>`;
      return;
    }
    filtered.slice(0, 15).forEach(row => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${row.id || '-'}</td>
        <td style="color: #ffffff;">${row.name || '<span style="color:#ff0054">[NULL]</span>'}</td>
        <td>${row.registrationNumber || '-'}</td>
        <td>${row.age !== undefined && row.age !== null ? row.age : '<span style="color:#ffb703">[NULL]</span>'}</td>
        <td>${row.phoneNumber || '<span style="color:#ff0054">[MISSING]</span>'}</td>
        <td>${row.department || '-'}</td>
        <td>${row.section || '-'}</td>
      `;
      tbody.appendChild(tr);
    });
  }
}

function populateHistoryModal() {
  const dataset = window.DataFixAPI.currentDataset || [];
  const filterSelect = document.getElementById("history-category-filter");
  if (filterSelect) {
    const depts = window.CollegeDataService.getDepartments(dataset);
    filterSelect.innerHTML = `<option value="all">All Categories & Departments</option>` +
      depts.map(d => `<option value="${d}">${d}</option>`).join("");
  }
  renderHistoryRows();
}

function renderHistoryRows() {
  const historyList = window.DataFixAPI.getAuditHistory() || [];
  const searchVal = document.getElementById("history-search-input") ? document.getElementById("history-search-input").value.toLowerCase().trim() : "";

  const tbody = document.querySelector("#history-audit-table tbody");
  if (!tbody) return;

  tbody.innerHTML = "";
  const diffs = window.DataFixAPI.currentDiff || [];

  const combinedEntries = [];
  diffs.forEach(d => {
    combinedEntries.push({
      timestamp: new Date().toLocaleTimeString(),
      action: "AUTO_REPAIR",
      field: d.field,
      original: d.original,
      fixed: d.fixed
    });
  });

  historyList.forEach(h => {
    combinedEntries.push({
      timestamp: new Date(h.timestamp).toLocaleTimeString(),
      action: h.action,
      field: "SYSTEM",
      original: "-",
      fixed: h.details
    });
  });

  const filtered = combinedEntries.filter(item => {
    if (searchVal) {
      const matchSearch = String(item.action).toLowerCase().includes(searchVal) ||
        String(item.field).toLowerCase().includes(searchVal) ||
        String(item.fixed).toLowerCase().includes(searchVal) ||
        String(item.original).toLowerCase().includes(searchVal);
      if (!matchSearch) return false;
    }
    return true;
  });

  document.getElementById("history-total-count").textContent = `Total Changes Recorded: ${filtered.length}`;

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #64748b; padding: 20px;">No change history recorded yet.</td></tr>`;
    return;
  }

  filtered.forEach(entry => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td style="color: #64748b;">${entry.timestamp}</td>
      <td><span class="status-pill local" style="display:inline-block; padding: 2px 8px; font-size: 0.7rem;">${entry.action}</span></td>
      <td style="color: #00f3ff;">${entry.field}</td>
      <td style="color: #ff0054;">${entry.original !== undefined ? entry.original : '-'}</td>
      <td style="color: #00f5a0;">${entry.fixed !== undefined ? entry.fixed : '-'}</td>
    `;
    tbody.appendChild(tr);
  });
}

function populateDownloadDropdowns() {
  const dataset = window.DataFixAPI.currentDataset || [];
  const deptSelect = document.getElementById("download-dept-select");
  const secSelect = document.getElementById("download-section-select");

  if (deptSelect) {
    const depts = window.CollegeDataService.getDepartments(dataset);
    deptSelect.innerHTML = `<option value="all">Entire Database (All Departments)</option>` +
      depts.map(d => `<option value="${d}">${d}</option>`).join("");
  }

  if (secSelect) {
    const secs = window.CollegeDataService.getSections(dataset);
    secSelect.innerHTML = `<option value="all">All Sections</option>` +
      secs.map(s => `<option value="${s}">Section ${s}</option>`).join("");
  }
}

async function populateAIInsightsModal() {
  const insightsRes = await window.DataFixAPI.generateAIInsights();
  const data = insightsRes.data;

  const banner = document.getElementById("ai-risk-banner");
  if (banner) banner.textContent = data.riskAssessment;

  const rootList = document.getElementById("ai-root-causes-list");
  if (rootList) {
    rootList.innerHTML = (data.rootCauses || []).map(rc => `<li>${rc}</li>`).join("");
  }

  const prioList = document.getElementById("ai-priority-list");
  if (prioList) {
    prioList.innerHTML = (data.priorityOrder || []).map(p => `<li>${p}</li>`).join("");
  }
}

function populateDiffInspectorModal() {
  const diffs = window.DataFixAPI.currentDiff || [];
  const tbody = document.querySelector("#diff-inspector-table tbody");
  if (!tbody) return;

  tbody.innerHTML = "";

  if (diffs.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #00f5a0; padding: 24px;">No differences detected. Dataset is fully sanitized.</td></tr>`;
    return;
  }

  diffs.forEach(diff => {
    let tag = '<span class="diff-tag-repaired">FORMAT FIXED</span>';
    if (diff.fixed && diff.fixed.includes("REMOVED")) {
      tag = '<span class="diff-tag-deleted">DUPLICATE REMOVED</span>';
    } else if (diff.original === "null" || diff.original === null || diff.original === "") {
      tag = '<span class="diff-tag-imputed">IMPUTED VALUE</span>';
    }

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td style="color: #64748b;">Row #${diff.rowIndex + 1}</td>
      <td style="color: #00f3ff; font-weight: 600;">${diff.field}</td>
      <td style="color: #ff0054; text-decoration: line-through;">${diff.original || '[BLANK]'}</td>
      <td style="color: #00f5a0; font-weight: 600;">${diff.fixed}</td>
      <td>${tag}</td>
    `;
    tbody.appendChild(tr);
  });
}

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.add("active");
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove("active");
}

function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;

  let icon = "ℹ️";
  if (type === "success") icon = "✓";
  if (type === "error") icon = "⚠️";
  if (type === "warning") icon = "⚡";

  toast.innerHTML = `
    <span style="font-size: 1.1rem;">${icon}</span>
    <span>${message}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(50px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

window.showToast = showToast;
