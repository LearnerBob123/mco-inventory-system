import { useEffect, useState } from "react";

import TableView from "../components/TableView";
import { getInventory } from "../services/api";

const columns = [
  { key: "stock_id", label: "Stock ID" },
  { key: "part_number", label: "Part Number" },
  { key: "current_stock", label: "Current Stock" },
  { key: "low_stock_threshold", label: "Low Stock Threshold" },
  { key: "last_updated", label: "Last Updated" },
];

export default function InventoryPage() {
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getInventory()
      .then(setRows)
      .catch((requestError) => {
        setError(requestError.response?.data?.detail || "Failed to load inventory.");
      });
  }, []);

  return (
    <section className="stack-lg">
      <div>
        <h1>Inventory</h1>
        <p>Global stock rows from inventory_stock.</p>
      </div>
      {error ? <p className="message message--error">{error}</p> : null}
      <div className="card">
        <TableView columns={columns} rows={rows} emptyText="No inventory rows found." />
      </div>
    </section>
  );
}