const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

function buildUrl(path, query = {}) {
  const url = new URL(`${API_BASE_URL}${path}`);
  Object.entries(query).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, String(value));
    }
  });
  return url.toString();
}

async function handleResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json") ? await response.json() : await response.text();

  if (!response.ok) {
    const message = typeof payload === "object" && payload !== null && "detail" in payload ? payload.detail : "Request failed.";
    throw new Error(String(message));
  }

  return payload;
}

export async function createWorkOrder(gunId) {
  const response = await fetch(buildUrl("/work-orders"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ gun_id: Number(gunId) }),
  });

  return handleResponse(response);
}

export async function listWorkOrders() {
  const response = await fetch(buildUrl("/work-orders"));
  return handleResponse(response);
}

export async function getWorkOrderById(workOrderId) {
  const response = await fetch(buildUrl(`/work-orders/${workOrderId}`));
  return handleResponse(response);
}

export async function assignWorker(workOrderId, userId) {
  const response = await fetch(buildUrl(`/work-orders/${workOrderId}/assign-worker`), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_id: Number(userId) }),
  });

  return handleResponse(response);
}

export async function requestComponent(workOrderId, payload) {
  const response = await fetch(buildUrl(`/work-orders/${workOrderId}/components/request`), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      part_number: payload.partNumber,
      requested_qty: Number(payload.requestedQty),
      requested_by: Number(payload.requestedBy),
    }),
  });

  return handleResponse(response);
}

export async function approveComponent(componentRequestId, approvedBy) {
  const response = await fetch(buildUrl(`/components/${componentRequestId}/approve`), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ approved_by: Number(approvedBy) }),
  });

  return handleResponse(response);
}

export async function rejectComponent(componentRequestId, approvedBy) {
  const response = await fetch(buildUrl(`/components/${componentRequestId}/reject`), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ approved_by: Number(approvedBy) }),
  });

  return handleResponse(response);
}

export async function listGuns() {
  const response = await fetch(buildUrl("/guns"));
  return handleResponse(response);
}

export async function createGun(name) {
  const response = await fetch(buildUrl("/guns"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name }),
  });

  return handleResponse(response);
}

export async function listUsers() {
  const response = await fetch(buildUrl("/users"));
  return handleResponse(response);
}

export async function createUser(name, role) {
  const response = await fetch(buildUrl("/users"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name, role }),
  });

  return handleResponse(response);
}

export async function listInventory() {
  const response = await fetch(buildUrl("/inventory"));
  return handleResponse(response);
}

export async function createInventoryItem(payload) {
  const response = await fetch(buildUrl("/inventory"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      part_number: payload.partNumber,
      name: payload.name,
      stock: Number(payload.stock),
    }),
  });

  return handleResponse(response);
}

export async function listWorkflows(role, userId) {
  const response = await fetch(buildUrl("/workflows", { role, user_id: userId }));
  return handleResponse(response);
}

export async function getWorkflowById(workflowId, role, userId) {
  const response = await fetch(buildUrl(`/workflows/${workflowId}`, { role, user_id: userId }));
  return handleResponse(response);
}

export async function createWorkflow(payload, role) {
  const response = await fetch(buildUrl("/workflows", { role }), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      title: payload.title,
      work_order_id: Number(payload.workOrderId),
      admin_user_id: Number(payload.adminUserId),
    }),
  });

  return handleResponse(response);
}

export async function assignWorkflowWorkers(workflowId, payload, role) {
  const response = await fetch(buildUrl(`/workflows/${workflowId}/assign-workers`, { role }), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      worker_ids: payload.workerIds.map((item) => Number(item)),
      admin_user_id: Number(payload.adminUserId),
    }),
  });

  return handleResponse(response);
}

export async function listPendingWorkflowRequests(role) {
  const response = await fetch(buildUrl("/workflows/pending-requests", { role }));
  return handleResponse(response);
}

export async function submitWorkflowResourceRequest(workflowId, payload, role) {
  const response = await fetch(buildUrl(`/workflows/${workflowId}/resource-requests`, { role }), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      part_number: payload.partNumber,
      requested_qty: Number(payload.requestedQty),
      requested_by: Number(payload.requestedBy),
    }),
  });

  return handleResponse(response);
}

export async function approveWorkflowRequest(requestId, payload, role) {
  const response = await fetch(buildUrl(`/workflows/resource-requests/${requestId}/approve`, { role }), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      admin_user_id: Number(payload.adminUserId),
      feedback_message: payload.feedbackMessage || null,
    }),
  });

  return handleResponse(response);
}

export async function rejectWorkflowRequest(requestId, payload, role) {
  const response = await fetch(buildUrl(`/workflows/resource-requests/${requestId}/reject`, { role }), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      admin_user_id: Number(payload.adminUserId),
      feedback_message: payload.feedbackMessage || null,
    }),
  });

  return handleResponse(response);
}

export async function completeWorkflowTask(workflowId, workerId, role) {
  const response = await fetch(buildUrl(`/workflows/${workflowId}/complete-task`, { role }), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ worker_id: Number(workerId) }),
  });

  return handleResponse(response);
}

export async function finalizeWorkflow(workflowId, adminUserId, role) {
  const response = await fetch(buildUrl(`/workflows/${workflowId}/finalize`, { role }), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ admin_user_id: Number(adminUserId) }),
  });

  return handleResponse(response);
}

export async function reworkWorkflow(workflowId, payload, role) {
  const response = await fetch(buildUrl(`/workflows/${workflowId}/rework`, { role }), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      admin_user_id: Number(payload.adminUserId),
      feedback_message: payload.feedbackMessage,
    }),
  });

  return handleResponse(response);
}

export async function sendWorkflowFeedback(workflowId, payload, role) {
  const response = await fetch(buildUrl(`/workflows/${workflowId}/feedback`, { role }), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      admin_user_id: Number(payload.adminUserId),
      to_user_id: payload.toUserId ? Number(payload.toUserId) : null,
      message: payload.message,
    }),
  });

  return handleResponse(response);
}

export { API_BASE_URL };
