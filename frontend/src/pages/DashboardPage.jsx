import { Link } from "react-router-dom";
import { useEffect, useState } from "react";

import { getComponents, getHierarchyNodes, getInventory, getTransactions } from "../services/api";

export default function DashboardPage() {
  const [stats, setStats] = useState({ components: 0, hierarchyNodes: 0, stockRows: 0, transactions: 0 });

  useEffect(() => {
    async function loadStats() {
      try {
        const [components, hierarchyNodes, inventory, transactions] = await Promise.all([
          getComponents(),
          getHierarchyNodes(),
          getInventory(),
          getTransactions(),
        ]);
        setStats({
          components: components.length,
          hierarchyNodes: hierarchyNodes.length,
          stockRows: inventory.length,
          transactions: transactions.length,
        });
      } catch {
        setStats({ components: 0, hierarchyNodes: 0, stockRows: 0, transactions: 0 });
      }
    }

    loadStats();
  }, []);

  return (
    <section className="stack-lg">
      <div>
        <h1>Dashboard</h1>
        <p>Minimal Phase 1 frontend for component, inventory, transaction, and lifecycle flows.</p>
      </div>

      <div className="card-grid">
        <article className="card">
          <h2>{stats.components}</h2>
          <p>Components</p>
        </article>
        <article className="card">
          <h2>{stats.hierarchyNodes}</h2>
          <p>Hierarchy Nodes</p>
        </article>
        <article className="card">
          <h2>{stats.stockRows}</h2>
          <p>Inventory Rows</p>
        </article>
        <article className="card">
          <h2>{stats.transactions}</h2>
          <p>Transactions</p>
        </article>
      </div>

      <div className="card-grid">
        <Link className="card card--link" to="/components">
          Manage Components
        </Link>
        <Link className="card card--link" to="/hierarchy">
          Manage Hierarchy
        </Link>
        <Link className="card card--link" to="/inventory">
          View Inventory
        </Link>
        <Link className="card card--link" to="/transactions">
          Record Transactions
        </Link>
        <Link className="card card--link" to="/lifecycle">
          Lifecycle Status
        </Link>
      </div>
    </section>
  );
}