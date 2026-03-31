import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
});

export function getComponents() {
  return api.get("/v2/component/list").then((response) => response.data);
}

export function createComponent(payload) {
  return api.post("/v2/component/add", payload).then((response) => response.data);
}

export function createComponentUsage(payload) {
  return api.post("/v2/hierarchy/usage", payload).then((response) => response.data);
}

export function getHierarchyNodes() {
  return api.get("/v2/hierarchy/node/list").then((response) => response.data);
}

export function createHierarchyNode(payload) {
  return api.post("/v2/hierarchy/node", payload).then((response) => response.data);
}

export function getHierarchyTree() {
  return api.get("/v2/hierarchy/tree").then((response) => response.data);
}

export function getInventory() {
  return api.get("/v2/inventory/stock").then((response) => response.data);
}

export function upsertInventoryStock(payload) {
  return api.post("/v2/inventory/stock/upsert", payload).then((response) => response.data);
}

export function createTransaction(payload) {
  return api.post("/v2/inventory/transaction", payload).then((response) => response.data);
}

export function getTransactions() {
  return api.get("/v2/inventory/transaction").then((response) => response.data);
}

export function getLifecycleStatus() {
  return api.get("/lifecycle/").then((response) => response.data);
}

export function transitionLifecycle(payload) {
  return api.post("/component/transition", payload).then((response) => response.data);
}

export default api;