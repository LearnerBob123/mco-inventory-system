import { useEffect, useState } from "react";

import FormInput from "../components/FormInput";
import TableView from "../components/TableView";
import { getLifecycleStatus, transitionLifecycle } from "../services/api";

const columns = [
  { key: "component_id", label: "Component ID" },
  { key: "old_state", label: "Old State" },
  { key: "new_state", label: "New State" },
];

const initialForm = {
  component_id: "",
  new_state: "",
};

export default function LifecyclePage() {
  const [rows, setRows] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function loadLifecycle() {
    const lifecycleData = await getLifecycleStatus();
    setRows(lifecycleData);
  }

  useEffect(() => {
    loadLifecycle().catch(() => setError("Failed to load lifecycle status."));
  }, []);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setMessage("");
    setError("");

    try {
      const response = await transitionLifecycle({
        component_id: form.component_id,
        new_state: form.new_state,
      });
      setMessage(response.message || "Lifecycle transition submitted.");
      setForm(initialForm);
      await loadLifecycle();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Failed to submit lifecycle transition.");
    }
  }

  return (
    <section className="page-grid">
      <div className="card">
        <h1>Lifecycle Status</h1>
        <p>The current backend lifecycle endpoint is legacy-oriented and uses component IDs from the older flow.</p>
        <form className="form-grid" onSubmit={handleSubmit}>
          <FormInput label="Component ID" name="component_id" value={form.component_id} onChange={handleChange} required />
          <FormInput label="New State" name="new_state" value={form.new_state} onChange={handleChange} required />
          <button className="button" type="submit">Trigger Transition</button>
        </form>
        {message ? <p className="message message--success">{message}</p> : null}
        {error ? <p className="message message--error">{error}</p> : null}
      </div>

      <div className="card">
        <h2>Lifecycle Log</h2>
        <TableView columns={columns} rows={rows} emptyText="No lifecycle records found." />
      </div>
    </section>
  );
}