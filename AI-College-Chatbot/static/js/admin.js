/* ==========================================================================
   AI College Assistant - Admin Panel frontend logic
   Handles: login, dashboard stats, FAQ CRUD, notice CRUD.
   ========================================================================== */

(function () {
  "use strict";

  const page = document.currentScript.getAttribute("data-page");
  const CSRF_TOKEN = window.CSRF_TOKEN || "";

  function apiHeaders(withJson) {
    const headers = {};
    if (withJson) headers["Content-Type"] = "application/json";
    if (CSRF_TOKEN) headers["X-CSRF-Token"] = CSRF_TOKEN;
    return headers;
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str == null ? "" : str;
    return div.innerHTML;
  }

  function formatDateTime(iso) {
    if (!iso) return "—";
    const d = new Date(iso);
    return d.toLocaleString([], { dateStyle: "medium", timeStyle: "short" });
  }

  // =========================================================================
  // LOGOUT (shared across all admin pages with a sidebar)
  // =========================================================================
  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
      try {
        await fetch("/api/admin/logout", { method: "POST", headers: apiHeaders(false) });
      } finally {
        window.location.href = "/admin/login";
      }
    });
  }

  // =========================================================================
  // LOGIN PAGE
  // =========================================================================
  if (page === "login") {
    const form = document.getElementById("loginForm");
    const errorBox = document.getElementById("loginError");
    const loginBtn = document.getElementById("loginBtn");

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      errorBox.hidden = true;
      loginBtn.disabled = true;
      loginBtn.textContent = "Logging in...";

      const username = document.getElementById("username").value.trim();
      const password = document.getElementById("password").value;

      try {
        const res = await fetch("/api/admin/login", {
          method: "POST",
          headers: apiHeaders(true),
          body: JSON.stringify({ username, password }),
        });
        const payload = await res.json();

        if (!res.ok || !payload.success) {
          errorBox.textContent = payload.error || "Login failed. Please try again.";
          errorBox.hidden = false;
          return;
        }

        window.location.href = "/admin/dashboard";
      } catch (err) {
        errorBox.textContent = "Could not reach the server. Please try again.";
        errorBox.hidden = false;
      } finally {
        loginBtn.disabled = false;
        loginBtn.textContent = "Log In";
      }
    });
  }

  // =========================================================================
  // DASHBOARD PAGE
  // =========================================================================
  if (page === "dashboard") {
    async function loadStats() {
      try {
        const res = await fetch("/api/dashboard/stats", { headers: apiHeaders(false) });
        if (res.status === 401) { window.location.href = "/admin/login"; return; }
        const payload = await res.json();
        if (!payload.success) return;

        const data = payload.data;
        document.getElementById("statFaqs").textContent = data.total_faqs;
        document.getElementById("statCategories").textContent = data.total_categories;
        document.getElementById("statQueries").textContent = data.total_queries;
        document.getElementById("statUnanswered").textContent = data.unanswered_queries;

        const tbody = document.getElementById("recentQueriesBody");
        if (!data.recent_queries.length) {
          tbody.innerHTML = '<tr><td colspan="3" class="table-loading">No queries yet.</td></tr>';
          return;
        }

        tbody.innerHTML = data.recent_queries.map((q) => `
          <tr>
            <td>${escapeHtml(q.user_question)}</td>
            <td>${q.matched_faq_id ? (q.similarity_score * 100).toFixed(0) + "%" : "No match"}</td>
            <td>${formatDateTime(q.created_at)}</td>
          </tr>
        `).join("");
      } catch (err) {
        document.getElementById("recentQueriesBody").innerHTML =
          '<tr><td colspan="3" class="table-loading">Could not load data.</td></tr>';
      }
    }

    loadStats();
  }

  // =========================================================================
  // FAQ MANAGEMENT PAGE
  // =========================================================================
  if (page === "faqs") {
    const tableBody = document.getElementById("faqTableBody");
    const searchInput = document.getElementById("searchInput");
    const categoryFilter = document.getElementById("categoryFilter");

    const modalOverlay = document.getElementById("faqModalOverlay");
    const modalTitle = document.getElementById("faqModalTitle");
    const faqForm = document.getElementById("faqForm");
    const faqFormError = document.getElementById("faqFormError");

    const deleteOverlay = document.getElementById("deleteModalOverlay");
    let pendingDeleteId = null;
    let debounceTimer = null;

    function openModal(faq) {
      faqFormError.hidden = true;
      if (faq) {
        modalTitle.textContent = "Edit FAQ";
        document.getElementById("faqId").value = faq.id;
        document.getElementById("faqQuestion").value = faq.question;
        document.getElementById("faqAnswer").value = faq.answer;
        document.getElementById("faqCategory").value = faq.category;
        document.getElementById("faqKeywords").value = faq.keywords || "";
      } else {
        modalTitle.textContent = "Add FAQ";
        faqForm.reset();
        document.getElementById("faqId").value = "";
      }
      modalOverlay.hidden = false;
    }

    function closeModal() { modalOverlay.hidden = true; }

    document.getElementById("addFaqBtn").addEventListener("click", () => openModal(null));
    document.getElementById("cancelFaqBtn").addEventListener("click", closeModal);

    faqForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      faqFormError.hidden = true;

      const id = document.getElementById("faqId").value;
      const body = {
        question: document.getElementById("faqQuestion").value.trim(),
        answer: document.getElementById("faqAnswer").value.trim(),
        category: document.getElementById("faqCategory").value.trim(),
        keywords: document.getElementById("faqKeywords").value.trim(),
      };

      const url = id ? `/api/faqs/${id}` : "/api/faqs";
      const method = id ? "PUT" : "POST";

      try {
        const res = await fetch(url, { method, headers: apiHeaders(true), body: JSON.stringify(body) });
        const payload = await res.json();

        if (!res.ok || !payload.success) {
          faqFormError.textContent = payload.error || "Could not save FAQ.";
          faqFormError.hidden = false;
          return;
        }

        closeModal();
        loadFaqs();
      } catch (err) {
        faqFormError.textContent = "Could not reach the server.";
        faqFormError.hidden = false;
      }
    });

    document.getElementById("cancelDeleteBtn").addEventListener("click", () => {
      deleteOverlay.hidden = true;
      pendingDeleteId = null;
    });

    document.getElementById("confirmDeleteBtn").addEventListener("click", async () => {
      if (!pendingDeleteId) return;
      try {
        await fetch(`/api/faqs/${pendingDeleteId}`, { method: "DELETE", headers: apiHeaders(false) });
      } finally {
        deleteOverlay.hidden = true;
        pendingDeleteId = null;
        loadFaqs();
      }
    });

    function renderFaqRow(faq) {
      return `
        <tr>
          <td>${escapeHtml(faq.question)}</td>
          <td><span class="category-badge">${escapeHtml(faq.category)}</span></td>
          <td>${escapeHtml(faq.keywords || "—")}</td>
          <td class="cell-actions">
            <button class="action-link edit-link" data-edit="${faq.id}">Edit</button>
            <button class="action-link delete-link" data-delete="${faq.id}">Delete</button>
          </td>
        </tr>
      `;
    }

    let allFaqsCache = [];

    async function loadFaqs() {
      const search = searchInput.value.trim();
      const category = categoryFilter.value;
      const params = new URLSearchParams();
      if (search) params.set("search", search);
      if (category && category !== "all") params.set("category", category);

      try {
        const res = await fetch(`/api/faqs?${params.toString()}`, { headers: apiHeaders(false) });
        if (res.status === 401) { window.location.href = "/admin/login"; return; }
        const payload = await res.json();
        if (!payload.success) return;

        allFaqsCache = payload.data;

        if (!payload.data.length) {
          tableBody.innerHTML = '<tr><td colspan="4" class="table-loading">No FAQs found.</td></tr>';
          return;
        }

        tableBody.innerHTML = payload.data.map(renderFaqRow).join("");

        tableBody.querySelectorAll("[data-edit]").forEach((btn) => {
          btn.addEventListener("click", () => {
            const faq = allFaqsCache.find((f) => f.id === parseInt(btn.getAttribute("data-edit"), 10));
            if (faq) openModal(faq);
          });
        });
        tableBody.querySelectorAll("[data-delete]").forEach((btn) => {
          btn.addEventListener("click", () => {
            pendingDeleteId = btn.getAttribute("data-delete");
            deleteOverlay.hidden = false;
          });
        });
      } catch (err) {
        tableBody.innerHTML = '<tr><td colspan="4" class="table-loading">Could not load FAQs.</td></tr>';
      }
    }

    async function loadCategoriesIntoFilter() {
      try {
        const res = await fetch("/api/categories", { headers: apiHeaders(false) });
        const payload = await res.json();
        if (!payload.success) return;

        payload.data.forEach((cat) => {
          const opt = document.createElement("option");
          opt.value = cat;
          opt.textContent = cat;
          categoryFilter.appendChild(opt);
        });
      } catch (err) { /* non-critical */ }
    }

    searchInput.addEventListener("input", () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(loadFaqs, 300);
    });
    categoryFilter.addEventListener("change", loadFaqs);

    loadCategoriesIntoFilter();
    loadFaqs();
  }

  // =========================================================================
  // NOTICE MANAGEMENT PAGE
  // =========================================================================
  if (page === "notices") {
    const tableBody = document.getElementById("noticeTableBody");
    const modalOverlay = document.getElementById("noticeModalOverlay");
    const modalTitle = document.getElementById("noticeModalTitle");
    const noticeForm = document.getElementById("noticeForm");
    const noticeFormError = document.getElementById("noticeFormError");
    const deleteOverlay = document.getElementById("deleteNoticeModalOverlay");
    let pendingDeleteId = null;
    let allNoticesCache = [];

    function openModal(notice) {
      noticeFormError.hidden = true;
      if (notice) {
        modalTitle.textContent = "Edit Notice";
        document.getElementById("noticeId").value = notice.id;
        document.getElementById("noticeTitle").value = notice.title;
        document.getElementById("noticeContent").value = notice.content;
        document.getElementById("noticeActive").checked = notice.active;
      } else {
        modalTitle.textContent = "Add Notice";
        noticeForm.reset();
        document.getElementById("noticeId").value = "";
        document.getElementById("noticeActive").checked = true;
      }
      modalOverlay.hidden = false;
    }

    function closeModal() { modalOverlay.hidden = true; }

    document.getElementById("addNoticeBtn").addEventListener("click", () => openModal(null));
    document.getElementById("cancelNoticeBtn").addEventListener("click", closeModal);

    noticeForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      noticeFormError.hidden = true;

      const id = document.getElementById("noticeId").value;
      const body = {
        title: document.getElementById("noticeTitle").value.trim(),
        content: document.getElementById("noticeContent").value.trim(),
        active: document.getElementById("noticeActive").checked,
      };

      const url = id ? `/api/notices/${id}` : "/api/notices";
      const method = id ? "PUT" : "POST";

      try {
        const res = await fetch(url, { method, headers: apiHeaders(true), body: JSON.stringify(body) });
        const payload = await res.json();

        if (!res.ok || !payload.success) {
          noticeFormError.textContent = payload.error || "Could not save notice.";
          noticeFormError.hidden = false;
          return;
        }

        closeModal();
        loadNotices();
      } catch (err) {
        noticeFormError.textContent = "Could not reach the server.";
        noticeFormError.hidden = false;
      }
    });

    document.getElementById("cancelDeleteNoticeBtn").addEventListener("click", () => {
      deleteOverlay.hidden = true;
      pendingDeleteId = null;
    });

    document.getElementById("confirmDeleteNoticeBtn").addEventListener("click", async () => {
      if (!pendingDeleteId) return;
      try {
        await fetch(`/api/notices/${pendingDeleteId}`, { method: "DELETE", headers: apiHeaders(false) });
      } finally {
        deleteOverlay.hidden = true;
        pendingDeleteId = null;
        loadNotices();
      }
    });

    function renderNoticeRow(notice) {
      return `
        <tr>
          <td>${escapeHtml(notice.title)}</td>
          <td>${escapeHtml(notice.content.slice(0, 80))}${notice.content.length > 80 ? "…" : ""}</td>
          <td><span class="status-badge ${notice.active ? "status-active" : "status-inactive"}">${notice.active ? "Active" : "Inactive"}</span></td>
          <td class="cell-actions">
            <button class="action-link edit-link" data-edit="${notice.id}">Edit</button>
            <button class="action-link delete-link" data-delete="${notice.id}">Delete</button>
          </td>
        </tr>
      `;
    }

    async function loadNotices() {
      try {
        const res = await fetch("/api/notices", { headers: apiHeaders(false) });
        const payload = await res.json();
        if (!payload.success) return;

        allNoticesCache = payload.data;

        if (!payload.data.length) {
          tableBody.innerHTML = '<tr><td colspan="4" class="table-loading">No notices found.</td></tr>';
          return;
        }

        tableBody.innerHTML = payload.data.map(renderNoticeRow).join("");

        tableBody.querySelectorAll("[data-edit]").forEach((btn) => {
          btn.addEventListener("click", () => {
            const notice = allNoticesCache.find((n) => n.id === parseInt(btn.getAttribute("data-edit"), 10));
            if (notice) openModal(notice);
          });
        });
        tableBody.querySelectorAll("[data-delete]").forEach((btn) => {
          btn.addEventListener("click", () => {
            pendingDeleteId = btn.getAttribute("data-delete");
            deleteOverlay.hidden = false;
          });
        });
      } catch (err) {
        tableBody.innerHTML = '<tr><td colspan="4" class="table-loading">Could not load notices.</td></tr>';
      }
    }

    loadNotices();
  }
})();
