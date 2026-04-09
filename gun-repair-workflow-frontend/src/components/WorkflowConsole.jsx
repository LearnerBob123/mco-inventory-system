import { useEffect, useMemo, useState } from "react";

import SectionCard from "./SectionCard";
import StatusPill from "./StatusPill";
import {
  approveWorkflowRequest,
  assignWorkflowWorkers,
  completeWorkflowTask,
  createWorkflow,
  finalizeWorkflow,
  getWorkflowById,
  listInventory,
  listPendingWorkflowRequests,
  listUsers,
  listWorkOrders,
  listWorkflows,
  rejectWorkflowRequest,
  reworkWorkflow,
  sendWorkflowFeedback,
  submitWorkflowResourceRequest,
} from "../services/api";

function formatDate(value) {
  if (!value) {
    return "-";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function describeUser(user) {
  if (!user) {
    return "-";
  }
  return `${user.name} (${user.role})`;
}

export default function WorkflowConsole({ currentUser }) {
  const role = currentUser.role;
  const activeUserId = String(currentUser.id);
  const [activeTab, setActiveTab] = useState("overview");
  const [users, setUsers] = useState([]);
  const [inventoryItems, setInventoryItems] = useState([]);
  const [workOrders, setWorkOrders] = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [pendingRequests, setPendingRequests] = useState([]);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState("");
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [workflowTitle, setWorkflowTitle] = useState("");
  const [workflowWorkOrderId, setWorkflowWorkOrderId] = useState("");
  const [assignWorkerIds, setAssignWorkerIds] = useState([]);
  const [resourcePartNumber, setResourcePartNumber] = useState("");
  const [resourceQty, setResourceQty] = useState("1");
  const [selectedPendingRequestId, setSelectedPendingRequestId] = useState("");
  const [requestFeedback, setRequestFeedback] = useState("");
  const [workflowFeedback, setWorkflowFeedback] = useState("");
  const [feedbackTargetUserId, setFeedbackTargetUserId] = useState("");
  const [reworkFeedback, setReworkFeedback] = useState("");
  const [message, setMessage] = useState("Workflow data is linked to the active logged-in user.");
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const roleTabs = role === "admin"
    ? [
        { id: "overview", label: "Overview" },
        { id: "create", label: "Create Workflow" },
        { id: "assign", label: "Assign Workers" },
        { id: "requests", label: "Pending Requests" },
        { id: "review", label: "Final Review" },
        { id: "details", label: "Workflow Details" },
      ]
    : [
        { id: "overview", label: "Overview" },
        { id: "actions", label: "My Actions" },
        { id: "details", label: "Workflow Details" },
      ];
  const workers = useMemo(() => users.filter((user) => user.role === "worker"), [users]);
  const selectedPendingRequest = pendingRequests.find((item) => String(item.id) === selectedPendingRequestId) ?? null;
  const selectedWorkflowAssignments = selectedWorkflow?.assignments ?? [];
  const linkedWorkOrder = useMemo(
    () => workOrders.find((item) => item.id === selectedWorkflow?.work_order_id) ?? null,
    [selectedWorkflow, workOrders],
  );
  const linkedWorkOrderComponents = useMemo(
    () =>
      role === "admin"
        ? linkedWorkOrder?.components ?? []
        : (linkedWorkOrder?.components ?? []).filter((component) => String(component.requested_by) === activeUserId),
    [activeUserId, linkedWorkOrder, role],
  );
  const selectableFeedbackTargets = role === "admin" ? selectedWorkflowAssignments.map((item) => item.user) : [];
  const visibleAssignments = useMemo(
    () => (role === "admin" ? selectedWorkflowAssignments : selectedWorkflowAssignments.filter((item) => String(item.user.id) === activeUserId)),
    [activeUserId, role, selectedWorkflowAssignments],
  );
  const visibleResourceRequests = useMemo(
    () =>
      role === "admin"
        ? selectedWorkflow?.resource_requests ?? []
        : (selectedWorkflow?.resource_requests ?? []).filter((item) => String(item.requested_by) === activeUserId),
    [activeUserId, role, selectedWorkflow],
  );
  const visibleFeedbackEntries = useMemo(
    () =>
      (selectedWorkflow?.feedback_entries ?? []).filter(
        (entry) => role === "admin" || entry.to_user_id === null || String(entry.to_user_id) === activeUserId,
      ),
    [activeUserId, role, selectedWorkflow],
  );
  const canFinalizeWorkflow = selectedWorkflow?.state === "pending_approval";
  const canSendRework = selectedWorkflow?.state === "pending_approval";
  const canWorkerActOnWorkflow = Boolean(selectedWorkflowId) && selectedWorkflow?.state === "in_progress";

  async function loadWorkflowDetails(workflowId, { clearOnError = false } = {}) {
    if (!workflowId) {
      setSelectedWorkflow(null);
      return null;
    }

    try {
      const workflow = await getWorkflowById(workflowId);
      setSelectedWorkflow(workflow);
      return workflow;
    } catch (error) {
      if (clearOnError) {
        setSelectedWorkflow(null);
      }
      throw error;
    }
  }

  async function refreshReferenceData() {
    const requests = [listInventory(), listWorkOrders()];
    if (role === "admin") {
      requests.unshift(listUsers());
    }

    const [userListOrInventory, inventoryListOrWorkOrders, maybeWorkOrders] = await Promise.all(requests);
    const nextUsers = role === "admin" ? userListOrInventory : [];
    const nextInventory = role === "admin" ? inventoryListOrWorkOrders : userListOrInventory;
    const nextWorkOrders = role === "admin" ? maybeWorkOrders : inventoryListOrWorkOrders;

    setUsers(nextUsers ?? []);
    setInventoryItems(nextInventory ?? []);
    setWorkOrders(nextWorkOrders ?? []);

    if ((nextInventory ?? []).length > 0 && !resourcePartNumber) {
      setResourcePartNumber(nextInventory[0].part_number);
    }
    if ((nextWorkOrders ?? []).length > 0 && !workflowWorkOrderId) {
      setWorkflowWorkOrderId(String(nextWorkOrders[0].id));
    }
  }

  async function refreshWorkflowData(preferredWorkflowId = selectedWorkflowId) {
    const workflowsResponse = await listWorkflows();
    setWorkflows(workflowsResponse);

    if (role === "admin") {
      const pending = await listPendingWorkflowRequests();
      setPendingRequests(pending);
      if (pending.length > 0 && !pending.some((item) => String(item.id) === selectedPendingRequestId)) {
        setSelectedPendingRequestId(String(pending[0].id));
      }
      if (pending.length === 0) {
        setSelectedPendingRequestId("");
      }
    } else {
      setPendingRequests([]);
      setSelectedPendingRequestId("");
    }

    const requestedWorkflowId = preferredWorkflowId ? String(preferredWorkflowId) : "";
    const nextWorkflowId = workflowsResponse.some((workflow) => String(workflow.id) === requestedWorkflowId)
      ? requestedWorkflowId
      : (workflowsResponse[0] ? String(workflowsResponse[0].id) : "");
    setSelectedWorkflowId(nextWorkflowId);

    await loadWorkflowDetails(nextWorkflowId, { clearOnError: true });
  }

  async function refreshAll(preferredWorkflowId = selectedWorkflowId) {
    setIsRefreshing(true);
    try {
      await refreshReferenceData();
      await refreshWorkflowData(preferredWorkflowId);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to load workflow data.");
    } finally {
      setIsRefreshing(false);
    }
  }

  useEffect(() => {
    setActiveTab("overview");
    setSelectedWorkflowId("");
    setSelectedWorkflow(null);
    refreshAll("");
  }, [role]);

  useEffect(() => {
    if (selectedWorkflowAssignments.length > 0 && feedbackTargetUserId && !selectedWorkflowAssignments.some((item) => String(item.user.id) === feedbackTargetUserId)) {
      setFeedbackTargetUserId("");
    }
  }, [feedbackTargetUserId, selectedWorkflowAssignments]);

  useEffect(() => {
    async function loadSelectedWorkflow() {
      try {
        await loadWorkflowDetails(selectedWorkflowId, { clearOnError: true });
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Unable to load workflow details.");
      }
    }

    loadSelectedWorkflow();
  }, [selectedWorkflowId]);

  async function handleCreateWorkflow(event) {
    event.preventDefault();
    setIsSaving(true);
    setMessage("");
    try {
      const workflow = await createWorkflow({
        title: workflowTitle.trim(),
        workOrderId: workflowWorkOrderId,
      });
      setWorkflowTitle("");
      await refreshAll(String(workflow.id));
      setMessage(`Workflow ${workflow.id} created.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to create workflow.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleAssignWorkers(event) {
    event.preventDefault();
    setIsSaving(true);
    setMessage("");
    try {
      const workflow = await assignWorkflowWorkers(selectedWorkflowId, { workerIds: assignWorkerIds });
      setAssignWorkerIds([]);
      await refreshAll(String(workflow.id));
      setMessage("Workers assigned to workflow.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to assign workers.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleSubmitResourceRequest(event) {
    event.preventDefault();
    setIsSaving(true);
    setMessage("");
    try {
      const workflow = await submitWorkflowResourceRequest(selectedWorkflowId, {
        partNumber: resourcePartNumber,
        requestedQty: resourceQty,
      });
      setResourceQty("1");
      await refreshAll(String(workflow.id));
      setMessage("Resource request submitted.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to submit resource request.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleRequestDecision(decision) {
    if (!selectedPendingRequestId) {
      return;
    }

    setIsSaving(true);
    setMessage("");
    try {
      const handler = decision === "approve" ? approveWorkflowRequest : rejectWorkflowRequest;
      const workflow = await handler(selectedPendingRequestId, {
        feedbackMessage: requestFeedback.trim(),
      });
      setRequestFeedback("");
      await refreshAll(String(workflow.id));
      setMessage(`Request ${decision}d.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to review request.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleWorkerComplete() {
    setIsSaving(true);
    setMessage("");
    try {
      const workflow = await completeWorkflowTask(selectedWorkflowId);
      await refreshAll(String(workflow.id));
      setMessage("Worker completion submitted.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to mark task complete.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleFinalizeWorkflow() {
    setIsSaving(true);
    setMessage("");
    try {
      const workflow = await finalizeWorkflow(selectedWorkflowId);
      await refreshAll(String(workflow.id));
      setMessage(`Workflow ${workflow.id} finalized.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to finalize workflow.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleReworkWorkflow() {
    setIsSaving(true);
    setMessage("");
    try {
      const workflow = await reworkWorkflow(selectedWorkflowId, { feedbackMessage: reworkFeedback.trim() });
      setReworkFeedback("");
      await refreshAll(String(workflow.id));
      setMessage(`Workflow ${workflow.id} returned for rework.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to send workflow for rework.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleSendFeedback(event) {
    event.preventDefault();
    setIsSaving(true);
    setMessage("");
    try {
      const workflow = await sendWorkflowFeedback(selectedWorkflowId, {
        toUserId: feedbackTargetUserId,
        message: workflowFeedback.trim(),
      });
      setWorkflowFeedback("");
      setFeedbackTargetUserId("");
      await refreshAll(String(workflow.id));
      setMessage("Feedback sent.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to send feedback.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="simple-layout">
      <SectionCard title={role === "admin" ? "Admin Workflow Console" : "Worker Workflow Console"}>
        <div className="section-grid">
          <table>
            <tbody>
              <tr>
                <th>Active user</th>
                <td>{describeUser(currentUser)}</td>
              </tr>
              <tr>
                <th>Access mode</th>
                <td>{role === "admin" ? "Admin management" : "Worker execution"}</td>
              </tr>
              <tr>
                <th>Identity source</th>
                <td>Authenticated session token</td>
              </tr>
            </tbody>
          </table>

          <div className="stack-form">
            <p className="empty-text">Workflow linkage is now derived from the logged-in user instead of manual role and ID selectors.</p>
            <p className="empty-text">Admins can review and approve. Workers can request resources and complete their own assigned tasks.</p>
            <button type="button" className="button-secondary" onClick={() => refreshAll()} disabled={isRefreshing}>
              {isRefreshing ? "Refreshing..." : "Refresh workflow data"}
            </button>
          </div>
        </div>
      </SectionCard>

      <p className="message-banner">{message}</p>

      <div className="tab-bar" role="tablist" aria-label="Workflow role sections">
        {roleTabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            role="tab"
            className={activeTab === tab.id ? "tab-button tab-button--active" : "tab-button"}
            aria-selected={activeTab === tab.id}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {role === "admin" && activeTab === "overview" ? (
        <SectionCard title="Admin Overview">
          <div className="section-grid">
            <table>
              <tbody>
                <tr>
                  <th>Total workflows</th>
                  <td>{workflows.length}</td>
                </tr>
                <tr>
                  <th>Pending requests</th>
                  <td>{pendingRequests.length}</td>
                </tr>
                <tr>
                  <th>Selected workflow</th>
                  <td>{selectedWorkflow ? `${selectedWorkflow.id} - ${selectedWorkflow.title}` : "-"}</td>
                </tr>
              </tbody>
            </table>

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>State</th>
                    <th>Created By</th>
                  </tr>
                </thead>
                <tbody>
                  {workflows.length > 0 ? (
                    workflows.map((workflow) => (
                      <tr key={workflow.id}>
                        <td>{workflow.id}</td>
                        <td>{workflow.title}</td>
                        <td>{workflow.state}</td>
                        <td>{workflow.created_by_user?.name ?? workflow.created_by}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="4" className="empty-row">
                        No workflows found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </SectionCard>
      ) : null}

      {role === "admin" && activeTab === "create" ? (
        <SectionCard title="Create Workflow">
          <form className="stack-form" onSubmit={handleCreateWorkflow}>
            <label>
              <span>Workflow title</span>
              <input value={workflowTitle} onChange={(event) => setWorkflowTitle(event.target.value)} placeholder="Example: Barrel inspection run" required />
            </label>
            <label>
              <span>Linked work order</span>
              <select value={workflowWorkOrderId} onChange={(event) => setWorkflowWorkOrderId(event.target.value)} required>
                <option value="">Select work order</option>
                {workOrders.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.id} - Gun {item.gun_id} - {item.status}
                  </option>
                ))}
              </select>
            </label>
            <button type="submit" disabled={isSaving || !workflowWorkOrderId}>
              {isSaving ? "Saving..." : "Create workflow"}
            </button>
          </form>
        </SectionCard>
      ) : null}

      {role === "admin" && activeTab === "assign" ? (
        <SectionCard title="Assign Workers">
          <form className="stack-form" onSubmit={handleAssignWorkers}>
            <label>
              <span>Workflow</span>
              <select value={selectedWorkflowId} onChange={(event) => setSelectedWorkflowId(event.target.value)} required>
                <option value="">Select workflow</option>
                {workflows.map((workflow) => (
                  <option key={workflow.id} value={workflow.id}>
                    {workflow.id} - {workflow.title} - {workflow.state}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>Workers</span>
              <select multiple value={assignWorkerIds} onChange={(event) => setAssignWorkerIds(Array.from(event.target.selectedOptions, (option) => option.value))}>
                {workers.map((worker) => (
                  <option key={worker.id} value={worker.id}>
                    {describeUser(worker)}
                  </option>
                ))}
              </select>
            </label>
            <button type="submit" disabled={isSaving || !selectedWorkflowId || assignWorkerIds.length === 0}>
              {isSaving ? "Saving..." : "Assign selected workers"}
            </button>
          </form>
        </SectionCard>
      ) : null}

      {role === "admin" && activeTab === "requests" ? (
        <SectionCard title="Pending Resource Requests">
          <div className="section-grid">
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Workflow</th>
                    <th>Part</th>
                    <th>Qty</th>
                    <th>Worker</th>
                  </tr>
                </thead>
                <tbody>
                  {pendingRequests.length > 0 ? (
                    pendingRequests.map((request) => (
                      <tr key={request.id}>
                        <td>{request.id}</td>
                        <td>{request.workflow_id}</td>
                        <td>{request.part_number}</td>
                        <td>{request.requested_qty}</td>
                        <td>{request.requested_by_user?.name ?? request.requested_by}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="5" className="empty-row">
                        No pending requests.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            <form className="stack-form" onSubmit={(event) => event.preventDefault()}>
              <label>
                <span>Select pending request</span>
                <select value={selectedPendingRequestId} onChange={(event) => setSelectedPendingRequestId(event.target.value)}>
                  <option value="">Select request</option>
                  {pendingRequests.map((request) => (
                    <option key={request.id} value={request.id}>
                      {request.id} - Workflow {request.workflow_id} - {request.part_number}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                <span>Feedback message</span>
                <input value={requestFeedback} onChange={(event) => setRequestFeedback(event.target.value)} placeholder="Optional approval or rejection note" />
              </label>
              <div className="button-row">
                <button type="button" disabled={isSaving || !selectedPendingRequestId} onClick={() => handleRequestDecision("approve")}>
                  {isSaving ? "Saving..." : "Approve request"}
                </button>
                <button type="button" className="button-secondary" disabled={isSaving || !selectedPendingRequestId} onClick={() => handleRequestDecision("reject")}>
                  {isSaving ? "Saving..." : "Reject request"}
                </button>
              </div>
              {selectedPendingRequest ? <p className="empty-text">Selected request belongs to workflow {selectedPendingRequest.workflow_id}.</p> : null}
            </form>
          </div>
        </SectionCard>
      ) : null}

      {role === "admin" && activeTab === "review" ? (
        <SectionCard title="Final Review And Feedback">
          <div className="section-grid">
            <div className="stack-form">
              <label>
                <span>Workflow</span>
                <select value={selectedWorkflowId} onChange={(event) => setSelectedWorkflowId(event.target.value)}>
                  <option value="">Select workflow</option>
                  {workflows.map((workflow) => (
                    <option key={workflow.id} value={workflow.id}>
                      {workflow.id} - {workflow.title} - {workflow.state}
                    </option>
                  ))}
                </select>
              </label>
              <div className="button-row">
                <button type="button" disabled={isSaving || !selectedWorkflowId || !canFinalizeWorkflow} onClick={handleFinalizeWorkflow}>
                  {isSaving ? "Saving..." : "Finalize workflow"}
                </button>
              </div>
              <div className="stack-form">
                <label>
                  <span>Rework feedback</span>
                  <input value={reworkFeedback} onChange={(event) => setReworkFeedback(event.target.value)} placeholder="Reason for rework" required />
                </label>
                <button type="button" className="button-secondary" disabled={isSaving || !selectedWorkflowId || !reworkFeedback.trim() || !canSendRework} onClick={handleReworkWorkflow}>
                  {isSaving ? "Saving..." : "Send for rework"}
                </button>
              </div>
            </div>

            <form className="stack-form" onSubmit={handleSendFeedback}>
              <label>
                <span>Feedback target</span>
                <select value={feedbackTargetUserId} onChange={(event) => setFeedbackTargetUserId(event.target.value)}>
                  <option value="">All assigned workers</option>
                  {selectableFeedbackTargets.map((user) => (
                    <option key={user.id} value={user.id}>
                      {describeUser(user)}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                <span>Message</span>
                <input value={workflowFeedback} onChange={(event) => setWorkflowFeedback(event.target.value)} placeholder="Targeted feedback for worker or workflow" required />
              </label>
              <button type="submit" disabled={isSaving || !selectedWorkflowId}>
                {isSaving ? "Saving..." : "Send feedback"}
              </button>
            </form>
          </div>
        </SectionCard>
      ) : null}

      {role === "worker" && activeTab === "overview" ? (
        <SectionCard title="Worker Overview">
          <div className="section-grid">
            <table>
              <tbody>
                <tr>
                  <th>Assigned workflows</th>
                  <td>{workflows.length}</td>
                </tr>
                <tr>
                  <th>Selected workflow</th>
                  <td>{selectedWorkflow ? `${selectedWorkflow.id} - ${selectedWorkflow.title}` : "-"}</td>
                </tr>
                <tr>
                  <th>Visible feedback entries</th>
                  <td>{visibleFeedbackEntries.length}</td>
                </tr>
              </tbody>
            </table>

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>State</th>
                  </tr>
                </thead>
                <tbody>
                  {workflows.length > 0 ? (
                    workflows.map((workflow) => (
                      <tr key={workflow.id}>
                        <td>{workflow.id}</td>
                        <td>{workflow.title}</td>
                        <td>{workflow.state}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="3" className="empty-row">
                        No assigned workflows.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </SectionCard>
      ) : null}

      {role === "worker" && activeTab === "actions" ? (
        <SectionCard title="Assigned Workflow Actions">
          <div className="section-grid">
            <form className="stack-form" onSubmit={handleSubmitResourceRequest}>
              <label>
                <span>Assigned workflow</span>
                <select value={selectedWorkflowId} onChange={(event) => setSelectedWorkflowId(event.target.value)} required>
                  <option value="">Select workflow</option>
                  {workflows.map((workflow) => (
                    <option key={workflow.id} value={workflow.id}>
                      {workflow.id} - {workflow.title} - {workflow.state}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                <span>Inventory item</span>
                <select value={resourcePartNumber} onChange={(event) => setResourcePartNumber(event.target.value)} required>
                  <option value="">Select part</option>
                  {inventoryItems.map((item) => (
                    <option key={item.part_number} value={item.part_number}>
                      {item.part_number} - {item.name} - Stock {item.stock}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                <span>Requested quantity</span>
                <input type="number" min="1" value={resourceQty} onChange={(event) => setResourceQty(event.target.value)} required />
              </label>
              <div className="button-row">
                <button type="submit" disabled={isSaving || !canWorkerActOnWorkflow}>
                  {isSaving ? "Saving..." : "Submit request"}
                </button>
                <button type="button" className="button-secondary" disabled={isSaving || !canWorkerActOnWorkflow} onClick={handleWorkerComplete}>
                  {isSaving ? "Saving..." : "Mark task completed"}
                </button>
              </div>
            </form>

            <div>
              <h3 className="subheading">Assigned Workflows</h3>
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>State</th>
                  </tr>
                </thead>
                <tbody>
                  {workflows.length > 0 ? (
                    workflows.map((workflow) => (
                      <tr key={workflow.id}>
                        <td>{workflow.id}</td>
                        <td>{workflow.title}</td>
                        <td>{workflow.state}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="3" className="empty-row">
                        No assigned workflows.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </SectionCard>
      ) : null}

      {activeTab === "details" ? (
        <SectionCard title="Selected Workflow Details" aside={selectedWorkflow ? <StatusPill status={selectedWorkflow.state.toUpperCase()} /> : null}>
          {selectedWorkflow ? (
            <div className="detail-stack">
              <table>
                <tbody>
                  <tr>
                    <th>Linked Work Order</th>
                    <td>{linkedWorkOrder ? `${linkedWorkOrder.id} - ${linkedWorkOrder.status}` : "-"}</td>
                  </tr>
                  <tr>
                    <th>Workflow ID</th>
                    <td>{selectedWorkflow.id}</td>
                  </tr>
                  <tr>
                    <th>Title</th>
                    <td>{selectedWorkflow.title}</td>
                  </tr>
                  <tr>
                    <th>Linked Work Order</th>
                    <td>{selectedWorkflow.work_order_id}</td>
                  </tr>
                  <tr>
                    <th>Created By</th>
                    <td>{describeUser(selectedWorkflow.created_by_user)}</td>
                  </tr>
                  <tr>
                    <th>Finalized By</th>
                    <td>{describeUser(selectedWorkflow.finalized_by_user)}</td>
                  </tr>
                  <tr>
                    <th>Created At</th>
                    <td>{formatDate(selectedWorkflow.created_at)}</td>
                  </tr>
                </tbody>
              </table>

              <div className="section-grid">
                <div>
                  <h3 className="subheading">Assignments</h3>
                  <table>
                    <thead>
                      <tr>
                        <th>Worker</th>
                        <th>Status</th>
                        <th>Completed At</th>
                      </tr>
                    </thead>
                    <tbody>
                      {visibleAssignments.length > 0 ? (
                        visibleAssignments.map((assignment) => (
                          <tr key={assignment.id}>
                            <td>{describeUser(assignment.user)}</td>
                            <td>{assignment.completion_state}</td>
                            <td>{formatDate(assignment.completed_at)}</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan="3" className="empty-row">
                            No assignments yet.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>

                <div>
                  <h3 className="subheading">Workflow Resource Requests</h3>
                  <div className="table-wrap">
                    <table>
                      <thead>
                        <tr>
                          <th>ID</th>
                          <th>Part</th>
                          <th>Qty</th>
                          <th>Status</th>
                          <th>Requested By</th>
                          <th>Reviewed By</th>
                        </tr>
                      </thead>
                      <tbody>
                        {visibleResourceRequests.length > 0 ? (
                          visibleResourceRequests.map((request) => (
                            <tr key={request.id}>
                              <td>{request.id}</td>
                              <td>{request.part_number}</td>
                              <td>{request.requested_qty}</td>
                              <td>{request.status}</td>
                              <td>{describeUser(request.requested_by_user)}</td>
                              <td>{describeUser(request.reviewed_by_user)}</td>
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td colSpan="6" className="empty-row">
                              No resource requests yet.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="subheading">Linked Work Order Components</h3>
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Part</th>
                        <th>Qty</th>
                        <th>Status</th>
                        <th>Requested By</th>
                        <th>Approved By</th>
                      </tr>
                    </thead>
                    <tbody>
                      {linkedWorkOrderComponents.length > 0 ? (
                        linkedWorkOrderComponents.map((component) => (
                          <tr key={component.id}>
                            <td>{component.id}</td>
                            <td>{component.part_number}</td>
                            <td>{component.requested_qty}</td>
                            <td>{component.status}</td>
                            <td>{describeUser(component.requested_by_user)}</td>
                            <td>{describeUser(component.approved_by_user)}</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan="6" className="empty-row">
                            No linked work order components.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              <div>
                <h3 className="subheading">Feedback Log</h3>
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>From</th>
                        <th>To</th>
                        <th>Message</th>
                        <th>Created At</th>
                      </tr>
                    </thead>
                    <tbody>
                      {visibleFeedbackEntries.length > 0 ? (
                        visibleFeedbackEntries.map((entry) => (
                          <tr key={entry.id}>
                            <td>{describeUser(entry.from_user)}</td>
                            <td>{entry.to_user ? describeUser(entry.to_user) : "All assigned workers"}</td>
                            <td>{entry.message}</td>
                            <td>{formatDate(entry.created_at)}</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan="4" className="empty-row">
                            No feedback entries yet.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          ) : (
            <p className="empty-text">No workflow selected.</p>
          )}
        </SectionCard>
      ) : null}
    </div>
  );
}
