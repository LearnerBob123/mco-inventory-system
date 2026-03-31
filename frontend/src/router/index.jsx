import { Outlet, createBrowserRouter } from "react-router-dom";

import Navbar from "../components/Navbar";
import ComponentsPage from "../pages/ComponentsPage";
import DashboardPage from "../pages/DashboardPage";
import HierarchyPage from "../pages/HierarchyPage";
import InventoryPage from "../pages/InventoryPage";
import LifecyclePage from "../pages/LifecyclePage";
import TransactionsPage from "../pages/TransactionsPage";

function RootLayout() {
  return (
    <div className="app-shell">
      <Navbar />
      <main className="page-shell">
        <Outlet />
      </main>
    </div>
  );
}

const router = createBrowserRouter([
  {
    path: "/",
    element: <RootLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: "hierarchy", element: <HierarchyPage /> },
      { path: "components", element: <ComponentsPage /> },
      { path: "inventory", element: <InventoryPage /> },
      { path: "transactions", element: <TransactionsPage /> },
      { path: "lifecycle", element: <LifecyclePage /> },
    ],
  },
]);

export default router;