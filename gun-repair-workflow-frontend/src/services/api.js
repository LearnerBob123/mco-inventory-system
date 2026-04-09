const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
const TOKEN_STORAGE_KEY = "gun-repair-auth-token";

function buildUrl(path, query = {}) {
  const url = new URL(`${API_BASE_URL}${path}`);
  Object.entries(query).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, String(value));
    }
  });
  return url.toString();
}

export function getStoredAuthToken() {
  return window.localStorage.getItem(TOKEN_STORAGE_KEY);
}

function setStoredAuthToken(token) {
  window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function clearStoredAuthToken() {
  window.localStorage.removeItem(TOKEN_STORAGE_KEY);
}

function formatDetail(detail) {
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }
        if (item && typeof item === "object") {
          const location = Array.isArray(item.loc) ? item.loc.slice(1).join(".") : "field";
          const message = item.msg || "Invalid value.";
          return `${location}: ${message}`;
        }
        return String(item);
      })
      .join("; ");
  }

  if (detail && typeof detail === "object") {
    return JSON.stringify(detail);
  }

  return String(detail);
}

async function handleResponse(response, { clearTokenOnUnauthorized = true } = {}) {
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json") ? await response.json() : await response.text();

  if (!response.ok) {
    if (response.status === 401 && clearTokenOnUnauthorized) {
      clearStoredAuthToken();
    }
    const message = typeof payload === "object" && payload !== null && "detail" in payload ? formatDetail(payload.detail) : "Request failed.";
    throw new Error(message);
  }

  return payload;
}

async function apiFetch(path, { method = "GET", query, body, auth = true } = {}) {
  const headers = {};
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  if (auth) {
    const token = getStoredAuthToken();
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
  }

  const response = await fetch(buildUrl(path, query), {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  return handleResponse(response, { clearTokenOnUnauthorized: auth });
}

export async function loginUser(payload) {
  const response = await apiFetch("/auth/login", {
    method: "POST",
    auth: false,
    body: {
      name: payload.name,
      role: payload.role,
      password: payload.password,
    },
  });
  setStoredAuthToken(response.access_token);
  return response;
}

export async function fetchCurrentSession() {
  return apiFetch("/auth/me");
}

export async function logoutUser() {
  try {
    await apiFetch("/auth/logout", { method: "POST", body: {} });
  } finally {
    clearStoredAuthToken();
  }
}

export async function createWorkOrder(gunId) {
  return apiFetch("/work-orders", {
    method: "POST",
    body: { gun_id: Number(gunId) },
  });
}

export async function listWorkOrders() {
  return apiFetch("/work-orders");
}

export async function getWorkOrderById(workOrderId) {
  return apiFetch(`/work-orders/${workOrderId}`);
}

export async function assignWorker(workOrderId, userId) {
  return apiFetch(`/work-orders/${workOrderId}/assign-worker`, {
    method: "POST",
    body: { user_id: Number(userId) },
  });
}

export async function requestComponent(workOrderId, payload) {
  return apiFetch(`/work-orders/${workOrderId}/components/request`, {
    method: "POST",
    body: {
      part_number: payload.partNumber,
      requested_qty: Number(payload.requestedQty),
    },
  });
}

export async function approveComponent(componentRequestId) {
  return apiFetch(`/components/${componentRequestId}/approve`, {
    method: "POST",
    body: {},
  });
}

export async function rejectComponent(componentRequestId) {
  return apiFetch(`/components/${componentRequestId}/reject`, {
    method: "POST",
    body: {},
  });
}

export async function listGuns() {
  return apiFetch("/guns");
}

export async function createGun(name) {
  return apiFetch("/guns", {
    method: "POST",
    body: { name },
  });
}

export async function listUsers() {
  return apiFetch("/users");
}

export async function createUser(name, role, password) {
  return apiFetch("/users", {
    method: "POST",
    body: { name, role, password },
  });
}

export async function listInventory() {
  return apiFetch("/inventory");
}

export async function createInventoryItem(payload) {
  return apiFetch("/inventory", {
    method: "POST",
    body: {
      part_number: payload.partNumber,
      name: payload.name,
      stock: Number(payload.stock),
    },
  });
}

export async function listWorkflows() {
  return apiFetch("/workflows");
}

export async function getWorkflowById(workflowId) {
  return apiFetch(`/workflows/${workflowId}`);
}

export async function createWorkflow(payload) {
  return apiFetch("/workflows", {
    method: "POST",
    body: {
      title: payload.title,
      work_order_id: Number(payload.workOrderId),
    },
  });
}

export async function assignWorkflowWorkers(workflowId, payload) {
  return apiFetch(`/workflows/${workflowId}/assign-workers`, {
    method: "POST",
    body: {
      worker_ids: payload.workerIds.map((item) => Number(item)),
    },
  });
}

export async function listPendingWorkflowRequests() {
  return apiFetch("/workflows/pending-requests");
}

export async function submitWorkflowResourceRequest(workflowId, payload) {
  return apiFetch(`/workflows/${workflowId}/resource-requests`, {
    method: "POST",
    body: {
      part_number: payload.partNumber,
      requested_qty: Number(payload.requestedQty),
    },
  });
}

export async function approveWorkflowRequest(requestId, payload) {
  return apiFetch(`/workflows/resource-requests/${requestId}/approve`, {
    method: "POST",
    body: {
      feedback_message: payload.feedbackMessage || null,
    },
  });
}

export async function rejectWorkflowRequest(requestId, payload) {
  return apiFetch(`/workflows/resource-requests/${requestId}/reject`, {
    method: "POST",
    body: {
      feedback_message: payload.feedbackMessage || null,
    },
  });
}

export async function completeWorkflowTask(workflowId) {
  return apiFetch(`/workflows/${workflowId}/complete-task`, {
    method: "POST",
    body: {},
  });
}

export async function finalizeWorkflow(workflowId) {
  return apiFetch(`/workflows/${workflowId}/finalize`, {
    method: "POST",
    body: {},
  });
}

export async function reworkWorkflow(workflowId, payload) {
  return apiFetch(`/workflows/${workflowId}/rework`, {
    method: "POST",
    body: {
      feedback_message: payload.feedbackMessage,
    },
  });
}

export async function sendWorkflowFeedback(workflowId, payload) {
  return apiFetch(`/workflows/${workflowId}/feedback`, {
    method: "POST",
    body: {
      to_user_id: payload.toUserId ? Number(payload.toUserId) : null,
      message: payload.message,
    },
  });
}

export { API_BASE_URL };
