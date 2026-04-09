import { useEffect, useMemo, useState } from "react";

import SectionCard from "./components/SectionCard";
import StatusPill from "./components/StatusPill";
import WorkflowConsole from "./components/WorkflowConsole";
import {
  API_BASE_URL,
  approveComponent,
  assignWorker,
  clearStoredAuthToken,
  createGun,
  createInventoryItem,
  createUser,
  createWorkOrder,
  fetchCurrentSession,
  getStoredAuthToken,
  getWorkOrderById,
  listGuns,
  listInventory,
  listUsers,
  listWorkOrders,
  loginUser,
  logoutUser,
  rejectComponent,
  requestComponent,
} from "./services/api";

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

export default function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [isRestoringSession, setIsRestoringSession] = useState(true);
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [activeTab, setActiveTab] = useState("workflow");
  const [loginName, setLoginName] = useState("Admin One");
  const [loginRole, setLoginRole] = useState("admin");
  const [loginPassword, setLoginPassword] = useState("Admin@123");
  const [gunId, setGunId] = useState("");
  const [gunName, setGunName] = useState("");
  const [userName, setUserName] = useState("");
  const [userRole, setUserRole] = useState("worker");
  const [userPassword, setUserPassword] = useState("");
  const [inventoryPartNumber, setInventoryPartNumber] = useState("");
  const [inventoryName, setInventoryName] = useState("");
  const [inventoryStock, setInventoryStock] = useState("0");
  const [selectedWorkOrderId, setSelectedWorkOrderId] = useState("");
  const [assignUserId, setAssignUserId] = useState("");
  const [componentPartNumber, setComponentPartNumber] = useState("");
  const [componentQty, setComponentQty] = useState("1");
  const [decisionComponentId, setDecisionComponentId] = useState("");
  const [guns, setGuns] = useState([]);
  const [users, setUsers] = useState([]);
  const [inventoryItems, setInventoryItems] = useState([]);
  const [workOrders, setWorkOrders] = useState([]);
  const [workOrder, setWorkOrder] = useState(null);
  const [message, setMessage] = useState("Log in to continue.");
  const [isSubmittingUser, setIsSubmittingUser] = useState(false);
  const [isSubmittingInventory, setIsSubmittingInventory] = useState(false);
  const [isCreatingGun, setIsCreatingGun] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [isLoadingWorkOrder, setIsLoadingWorkOrder] = useState(false);
  const [isAssigningWorker, setIsAssigningWorker] = useState(false);
  const [isRequestingComponent, setIsRequestingComponent] = useState(false);
  const [isDecidingComponent, setIsDecidingComponent] = useState(false);
  const [isRefreshingData, setIsRefreshingData] = useState(false);

  const isAdmin = currentUser?.role === "admin";
  const workers = users.filter((user) => user.role === "worker");
  const pendingComponents = workOrder?.components.filter((component) => component.status === "REQUESTED") ?? [];
  const appTabs = useMemo(
    () =>
      isAdmin
        ? [
            { id: "workflow", label: "Workflow Console" },
            { id: "users", label: "Users" },
            { id: "inventory", label: "Inventory" },
            { id: "guns", label: "Guns" },
            { id: "work-orders", label: "Work Orders" },
          ]
        : [
            { id: "workflow", label: "Workflow Console" },
            { id: "work-orders", label: "Work Orders" },
          ],
    [isAdmin],
  );

  async function refreshWorkOrders(selectedId = selectedWorkOrderId) {
    const orders = await listWorkOrders();
    setWorkOrders(orders);

    const nextId = selectedId || (orders[0] ? String(orders[0].id) : "");
    setSelectedWorkOrderId(nextId);

    if (nextId) {
      const detailedWorkOrder = await getWorkOrderById(nextId);
      setWorkOrder(detailedWorkOrder);
      return detailedWorkOrder;
    }

    setWorkOrder(null);
    return null;
  }

  async function refreshAllData(preferredWorkOrderId = selectedWorkOrderId) {
    if (!currentUser) {
      return;
    }

    setIsRefreshingData(true);
    try {
      const requests = [listGuns(), listInventory(), listWorkOrders()];
      if (isAdmin) {
        requests.unshift(listUsers());
      }

      const [usersOrGuns, gunsOrInventory, inventoryOrWorkOrders, maybeWorkOrders] = await Promise.all(requests);
      const nextUsers = isAdmin ? usersOrGuns : [];
      const nextGuns = isAdmin ? gunsOrInventory : usersOrGuns;
      const nextInventory = isAdmin ? inventoryOrWorkOrders : gunsOrInventory;
      const nextWorkOrders = isAdmin ? maybeWorkOrders : inventoryOrWorkOrders;

      setUsers(nextUsers ?? []);
      setGuns(nextGuns ?? []);
      setInventoryItems(nextInventory ?? []);
      setWorkOrders(nextWorkOrders ?? []);

      if ((nextGuns ?? []).length > 0 && !gunId) {
        setGunId(String(nextGuns[0].id));
      }
      if ((nextUsers ?? []).length > 0 && isAdmin) {
        const firstWorker = nextUsers.find((user) => user.role === "worker");
        if (firstWorker && !assignUserId) {
          setAssignUserId(String(firstWorker.id));
        }
      }
      if ((nextInventory ?? []).length > 0 && !componentPartNumber) {
        setComponentPartNumber(nextInventory[0].part_number);
      }

      const nextId = preferredWorkOrderId || ((nextWorkOrders ?? [])[0] ? String(nextWorkOrders[0].id) : "");
      setSelectedWorkOrderId(nextId);
      if (nextId) {
        const detailedWorkOrder = await getWorkOrderById(nextId);
        setWorkOrder(detailedWorkOrder);
      } else {
        setWorkOrder(null);
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to load application data.");
    } finally {
      setIsRefreshingData(false);
    }
  }

  useEffect(() => {
    async function restoreSession() {
      if (!getStoredAuthToken()) {
        setIsRestoringSession(false);
        return;
      }

      try {
        const session = await fetchCurrentSession();
        setCurrentUser(session.user);
        setMessage(`Logged in as ${session.user.name}.`);
      } catch (error) {
        clearStoredAuthToken();
        setCurrentUser(null);
        setMessage(error instanceof Error ? error.message : "Session expired. Please log in again.");
      } finally {
        setIsRestoringSession(false);
      }
    }

    restoreSession();
  }, []);

  useEffect(() => {
    if (!currentUser) {
      return;
    }

    setActiveTab("workflow");
    refreshAllData();
  }, [currentUser]);

  useEffect(() => {
    if (pendingComponents.length > 0 && !pendingComponents.some((component) => String(component.id) === decisionComponentId)) {
      setDecisionComponentId(String(pendingComponents[0].id));
    }
    if (pendingComponents.length === 0) {
      setDecisionComponentId("");
    }
  }, [decisionComponentId, pendingComponents]);

  async function handleLogin(event) {
    event.preventDefault();
    setIsLoggingIn(true);
    setMessage("");

    try {
      const session = await loginUser({
        name: loginName.trim(),
        role: loginRole,
        password: loginPassword,
      });
      setCurrentUser(session.user);
      setMessage(`Logged in as ${session.user.name}.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to log in.");
    } finally {
      setIsLoggingIn(false);
    }
  }

  async function handleLogout() {
    try {
      await logoutUser();
    } finally {
      setCurrentUser(null);
      setUsers([]);
      setGuns([]);
      setInventoryItems([]);
      setWorkOrders([]);
      setWorkOrder(null);
      setSelectedWorkOrderId("");
      setMessage("Logged out.");
    }
  }

  async function handleCreateUser(event) {
    event.preventDefault();
    setIsSubmittingUser(true);
    setMessage("");

    try {
      const createdName = userName.trim();
      const createdRole = userRole;
      const createdPassword = userPassword;
      const createdUser = await createUser(createdName, createdRole, createdPassword);
      setLoginName(createdName);
      setLoginRole(createdRole);
      setLoginPassword(createdPassword);
      setUserName("");
      setUserPassword("");
      await refreshAllData();
      setMessage(`User ${createdUser.name} created. Login is prepared for role ${createdUser.role} after logout.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to create user.");
    } finally {
      setIsSubmittingUser(false);
    }
  }

  async function handleCreateInventory(event) {
    event.preventDefault();
    setIsSubmittingInventory(true);
    setMessage("");

    try {
      const createdItem = await createInventoryItem({
        partNumber: inventoryPartNumber.trim(),
        name: inventoryName.trim(),
        stock: inventoryStock,
      });
      setInventoryPartNumber("");
      setInventoryName("");
      setInventoryStock("0");
      await refreshAllData();
      setMessage(`Inventory item ${createdItem.part_number} created.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to create inventory item.");
    } finally {
      setIsSubmittingInventory(false);
    }
  }

  async function handleCreateGun(event) {
    event.preventDefault();
    setIsCreatingGun(true);
    setMessage("");

    try {
      const createdGun = await createGun(gunName.trim());
      setGunName("");
      setGunId(String(createdGun.id));
      await refreshAllData();
      setMessage(`Gun ${createdGun.name} created with id ${createdGun.id}.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to create gun.");
    } finally {
      setIsCreatingGun(false);
    }
  }

  async function handleCreate(event) {
    event.preventDefault();
    setIsCreating(true);
    setMessage("");

    try {
      const createdWorkOrder = await createWorkOrder(gunId);
      setWorkOrder(createdWorkOrder);
      setSelectedWorkOrderId(String(createdWorkOrder.id));
      await refreshAllData(String(createdWorkOrder.id));
      setMessage(`Work order ${createdWorkOrder.id} created successfully.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to create work order.");
    } finally {
      setIsCreating(false);
    }
  }

  async function handleLoadWorkOrder(event) {
    event.preventDefault();
    setIsLoadingWorkOrder(true);
    setMessage("");

    try {
      const loadedWorkOrder = await getWorkOrderById(selectedWorkOrderId);
      setWorkOrder(loadedWorkOrder);
      setMessage(`Work order ${loadedWorkOrder.id} loaded.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to load work order.");
      setWorkOrder(null);
    } finally {
      setIsLoadingWorkOrder(false);
    }
  }

  async function handleAssignWorker(event) {
    event.preventDefault();
    setIsAssigningWorker(true);
    setMessage("");

    try {
      const updatedWorkOrder = await assignWorker(selectedWorkOrderId, assignUserId);
      setWorkOrder(updatedWorkOrder);
      await refreshWorkOrders(String(updatedWorkOrder.id));
      setMessage("Worker assigned to work order.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to assign worker.");
    } finally {
      setIsAssigningWorker(false);
    }
  }

  async function handleRequestComponent(event) {
    event.preventDefault();
    setIsRequestingComponent(true);
    setMessage("");

    try {
      const updatedWorkOrder = await requestComponent(selectedWorkOrderId, {
        partNumber: componentPartNumber,
        requestedQty: componentQty,
      });
      setWorkOrder(updatedWorkOrder);
      await refreshWorkOrders(String(updatedWorkOrder.id));
      setMessage("Component request submitted.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to request component.");
    } finally {
      setIsRequestingComponent(false);
    }
  }

  async function handleDecideComponent(decision) {
    setIsDecidingComponent(true);
    setMessage("");

    try {
      if (decision === "approve") {
        await approveComponent(decisionComponentId);
      } else {
        await rejectComponent(decisionComponentId);
      }

      await refreshWorkOrders(selectedWorkOrderId);
      setMessage(`Component request ${decision === "approve" ? "approved" : "rejected"}.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to update component request.");
    } finally {
      setIsDecidingComponent(false);
    }
  }

  if (isRestoringSession) {
    return (
      <main className="app-shell">
        <header className="page-header">
          <h1>Gun Repair Workflow</h1>
          <p>Restoring session...</p>
        </header>
      </main>
    );
  }

  if (!currentUser) {
    return (
      <main className="app-shell">
        <header className="page-header">
          <h1>Gun Repair Workflow</h1>
          <p>Sign in to work as the active admin or worker. Workflow and component actions now use this logged-in identity.</p>
          <p>Login requires the exact saved role for that user. A worker account will not log in while the role selector is set to admin.</p>
          <p className="api-line">API: {API_BASE_URL}</p>
        </header>

        <p className="message-banner">{message}</p>

        <SectionCard title="Login">
          <div className="section-grid">
            <form className="stack-form" onSubmit={handleLogin}>
              <label>
                <span>Name</span>
                <input value={loginName} onChange={(event) => setLoginName(event.target.value)} required />
              </label>
              <label>
                <span>Role</span>
                <select value={loginRole} onChange={(event) => setLoginRole(event.target.value)}>
                  <option value="admin">Admin</option>
                  <option value="worker">Worker</option>
                </select>
              </label>
              <label>
                <span>Password</span>
                <input type="password" minLength="8" value={loginPassword} onChange={(event) => setLoginPassword(event.target.value)} required />
              </label>
              <button type="submit" disabled={isLoggingIn}>
                {isLoggingIn ? "Signing in..." : "Login"}
              </button>
            </form>

            <div className="detail-stack">
              <p className="empty-text">Seeded test accounts:</p>
              <p className="empty-text">Admin One / admin / Admin@123</p>
              <p className="empty-text">Worker One / worker / Worker@123</p>
              <p className="empty-text">Worker Two / worker / Worker2@123</p>
              <p className="empty-text">If a newly created user fails to log in, verify the role selector matches the role used when that user was created.</p>
            </div>
          </div>
        </SectionCard>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <header className="page-header">
        <div className="header-row">
          <div>
            <h1>Gun Repair Workflow</h1>
            <p>Logged in as {describeUser(currentUser)}. Admin approves and assigns. Workers request components and execute assigned work.</p>
            <p className="api-line">API: {API_BASE_URL}</p>
          </div>
          <button type="button" className="button-secondary" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </header>

      <p className="message-banner">{message}</p>

      <div className="tab-bar" role="tablist" aria-label="Application sections">
        {appTabs.map((tab) => (
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

      <div className="simple-layout">
        {activeTab === "workflow" ? <WorkflowConsole currentUser={currentUser} /> : null}

        {isAdmin && activeTab === "users" ? (
          <SectionCard title="Users">
            <div className="section-grid">
              <form className="stack-form" onSubmit={handleCreateUser}>
                <label>
                  <span>Name</span>
                  <input value={userName} onChange={(event) => setUserName(event.target.value)} placeholder="Enter user name" required />
                </label>
                <label>
                  <span>Role</span>
                  <select value={userRole} onChange={(event) => setUserRole(event.target.value)}>
                    <option value="worker">Worker</option>
                    <option value="admin">Admin</option>
                  </select>
                </label>
                <label>
                  <span>Password</span>
                  <input type="password" minLength="8" value={userPassword} onChange={(event) => setUserPassword(event.target.value)} placeholder="Minimum 8 characters" required />
                </label>
                <button type="submit" disabled={isSubmittingUser}>
                  {isSubmittingUser ? "Saving..." : "Add user"}
                </button>
              </form>

              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Role</th>
                  </tr>
                </thead>
                <tbody>
                  {users.length > 0 ? (
                    users.map((user) => (
                      <tr key={user.id}>
                        <td>{user.id}</td>
                        <td>{user.name}</td>
                        <td>{user.role}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="3" className="empty-row">
                        No users found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </SectionCard>
        ) : null}

        {isAdmin && activeTab === "inventory" ? (
          <SectionCard title="Inventory">
            <div className="section-grid">
              <form className="stack-form" onSubmit={handleCreateInventory}>
                <label>
                  <span>Part number</span>
                  <input value={inventoryPartNumber} onChange={(event) => setInventoryPartNumber(event.target.value)} placeholder="Example: P010" required />
                </label>
                <label>
                  <span>Part name</span>
                  <input value={inventoryName} onChange={(event) => setInventoryName(event.target.value)} placeholder="Example: Rear sight" required />
                </label>
                <label>
                  <span>Stock</span>
                  <input type="number" min="0" value={inventoryStock} onChange={(event) => setInventoryStock(event.target.value)} required />
                </label>
                <button type="submit" disabled={isSubmittingInventory}>
                  {isSubmittingInventory ? "Saving..." : "Add inventory item"}
                </button>
              </form>

              <table>
                <thead>
                  <tr>
                    <th>Part Number</th>
                    <th>Name</th>
                    <th>Stock</th>
                  </tr>
                </thead>
                <tbody>
                  {inventoryItems.length > 0 ? (
                    inventoryItems.map((item) => (
                      <tr key={item.part_number}>
                        <td>{item.part_number}</td>
                        <td>{item.name}</td>
                        <td>{item.stock}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="3" className="empty-row">
                        No inventory items found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </SectionCard>
        ) : null}

        {isAdmin && activeTab === "guns" ? (
          <SectionCard title="Guns">
            <form className="stack-form" onSubmit={handleCreateGun}>
              <label>
                <span>Gun name</span>
                <input type="text" value={gunName} onChange={(event) => setGunName(event.target.value)} placeholder="Example: INSAS LMG" required />
              </label>
              <div className="button-row">
                <button type="submit" disabled={isCreatingGun}>
                  {isCreatingGun ? "Saving..." : "Add gun"}
                </button>
                <button type="button" className="button-secondary" onClick={() => refreshAllData()} disabled={isRefreshingData}>
                  {isRefreshingData ? "Refreshing..." : "Refresh data"}
                </button>
              </div>
            </form>

            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                </tr>
              </thead>
              <tbody>
                {guns.length > 0 ? (
                  guns.map((gun) => (
                    <tr key={gun.id}>
                      <td>{gun.id}</td>
                      <td>{gun.name}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="2" className="empty-row">
                      No guns found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </SectionCard>
        ) : null}

        {activeTab === "work-orders" ? (
          <>
            {isAdmin ? (
              <SectionCard title="Create Work Order">
                <form className="stack-form" onSubmit={handleCreate}>
                  <label>
                    <span>Available guns</span>
                    <select value={gunId} onChange={(event) => setGunId(event.target.value)} required>
                      <option value="">Select gun</option>
                      {guns.map((gun) => (
                        <option key={gun.id} value={gun.id}>
                          {gun.id} - {gun.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <button type="submit" disabled={isCreating || !gunId}>
                    {isCreating ? "Creating..." : "Create work order"}
                  </button>
                </form>
              </SectionCard>
            ) : null}

            <SectionCard title="Select Work Order">
              <form className="stack-form" onSubmit={handleLoadWorkOrder}>
                <label>
                  <span>Work orders</span>
                  <select value={selectedWorkOrderId} onChange={(event) => setSelectedWorkOrderId(event.target.value)} required>
                    <option value="">Select work order</option>
                    {workOrders.map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.id} - Gun {item.gun_id} - {item.status}
                      </option>
                    ))}
                  </select>
                </label>
                <button type="submit" disabled={isLoadingWorkOrder || !selectedWorkOrderId}>
                  {isLoadingWorkOrder ? "Loading..." : "Load work order"}
                </button>
              </form>
            </SectionCard>

            {isAdmin ? (
              <SectionCard title="Assign Worker To Work Order">
                <form className="stack-form" onSubmit={handleAssignWorker}>
                  <label>
                    <span>Selected work order</span>
                    <input value={selectedWorkOrderId} readOnly placeholder="Load or create a work order first" />
                  </label>
                  <label>
                    <span>Worker</span>
                    <select value={assignUserId} onChange={(event) => setAssignUserId(event.target.value)} required>
                      <option value="">Select worker</option>
                      {workers.map((user) => (
                        <option key={user.id} value={user.id}>
                          {describeUser(user)}
                        </option>
                      ))}
                    </select>
                  </label>
                  <button type="submit" disabled={isAssigningWorker || !selectedWorkOrderId || !assignUserId}>
                    {isAssigningWorker ? "Assigning..." : "Assign worker"}
                  </button>
                </form>
              </SectionCard>
            ) : null}

            {!isAdmin ? (
              <SectionCard title="Request Component">
                <form className="stack-form" onSubmit={handleRequestComponent}>
                  <label>
                    <span>Selected work order</span>
                    <input value={selectedWorkOrderId} readOnly placeholder="Load a work order first" />
                  </label>
                  <label>
                    <span>Part</span>
                    <select value={componentPartNumber} onChange={(event) => setComponentPartNumber(event.target.value)} required>
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
                    <input type="number" min="1" value={componentQty} onChange={(event) => setComponentQty(event.target.value)} required />
                  </label>
                  <button type="submit" disabled={isRequestingComponent || !selectedWorkOrderId || !componentPartNumber}>
                    {isRequestingComponent ? "Submitting..." : "Request component"}
                  </button>
                </form>
              </SectionCard>
            ) : null}

            {isAdmin ? (
              <SectionCard title="Approve Or Reject Component Request">
                <form className="stack-form" onSubmit={(event) => event.preventDefault()}>
                  <label>
                    <span>Pending component request</span>
                    <select value={decisionComponentId} onChange={(event) => setDecisionComponentId(event.target.value)} required>
                      <option value="">Select request</option>
                      {pendingComponents.map((component) => (
                        <option key={component.id} value={component.id}>
                          {component.id} - {component.part_number} - Qty {component.requested_qty}
                        </option>
                      ))}
                    </select>
                  </label>
                  <div className="button-row">
                    <button type="button" disabled={isDecidingComponent || !decisionComponentId} onClick={() => handleDecideComponent("approve")}>
                      {isDecidingComponent ? "Saving..." : "Approve"}
                    </button>
                    <button type="button" className="button-secondary" disabled={isDecidingComponent || !decisionComponentId} onClick={() => handleDecideComponent("reject")}>
                      {isDecidingComponent ? "Saving..." : "Reject"}
                    </button>
                  </div>
                </form>
              </SectionCard>
            ) : null}

            <SectionCard title="Current Work Order Details" aside={workOrder ? <StatusPill status={workOrder.status} /> : null}>
              {workOrder ? (
                <div className="detail-stack">
                  <table>
                    <tbody>
                      <tr>
                        <th>Work Order ID</th>
                        <td>{workOrder.id}</td>
                      </tr>
                      <tr>
                        <th>Gun ID</th>
                        <td>{workOrder.gun_id}</td>
                      </tr>
                      <tr>
                        <th>Created At</th>
                        <td>{formatDate(workOrder.created_at)}</td>
                      </tr>
                    </tbody>
                  </table>

                  <div className="section-grid">
                    <div>
                      <h3 className="subheading">Assigned Workers</h3>
                      {workOrder.assigned_workers.length > 0 ? (
                        <table>
                          <thead>
                            <tr>
                              <th>ID</th>
                              <th>Name</th>
                              <th>Role</th>
                            </tr>
                          </thead>
                          <tbody>
                            {workOrder.assigned_workers.map((assignment) => (
                              <tr key={assignment.id}>
                                <td>{assignment.user.id}</td>
                                <td>{assignment.user.name}</td>
                                <td>{assignment.user.role}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      ) : (
                        <p className="empty-text">No workers assigned.</p>
                      )}
                    </div>

                    <div>
                      <h3 className="subheading">Component Requests</h3>
                      {workOrder.components.length > 0 ? (
                        <div className="table-wrap">
                          <table>
                            <thead>
                              <tr>
                                <th>ID</th>
                                <th>Part Number</th>
                                <th>Qty</th>
                                <th>Status</th>
                                <th>Requested By</th>
                                <th>Approved By</th>
                              </tr>
                            </thead>
                            <tbody>
                              {workOrder.components.map((component) => (
                                <tr key={component.id}>
                                  <td>{component.id}</td>
                                  <td>{component.part_number}</td>
                                  <td>{component.requested_qty}</td>
                                  <td>{component.status}</td>
                                  <td>{component.requested_by_user?.name ?? component.requested_by}</td>
                                  <td>{component.approved_by_user?.name ?? "-"}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      ) : (
                        <p className="empty-text">No components requested.</p>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <p className="empty-text">No work order selected.</p>
              )}
            </SectionCard>

            <SectionCard title="Work Orders In Database">
              {workOrders.length > 0 ? (
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Gun ID</th>
                      <th>Status</th>
                      <th>Workers</th>
                      <th>Components</th>
                    </tr>
                  </thead>
                  <tbody>
                    {workOrders.map((item) => (
                      <tr key={item.id}>
                        <td>{item.id}</td>
                        <td>{item.gun_id}</td>
                        <td>{item.status}</td>
                        <td>{item.assigned_workers.length}</td>
                        <td>{item.components.length}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p className="empty-text">No work orders found.</p>
              )}
            </SectionCard>
          </>
        ) : null}
      </div>
    </main>
  );
}
