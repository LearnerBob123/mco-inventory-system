import { useEffect, useState } from "react";

import FormInput from "../components/FormInput";
import TableView from "../components/TableView";
import { createTransaction, getComponents, getTransactions } from "../services/api";
import GeneratePDF from "../components/GeneratePDF";

const initialForm = {
  part_number: "",
  transaction_type: "",
  quantity: "",
  performed_by: "",
  remarks: "",
};

const columns = [
  { key: "transaction_id", label: "Transaction ID" },
  { key: "part_number", label: "Part Number" },
  { key: "transaction_type", label: "Type" },
  { key: "quantity", label: "Quantity" },
  { key: "performed_by", label: "Performed By" },
  { key: "transaction_date", label: "Date" },
  { key: "remarks", label: "Remarks" },
];

export default function TransactionsPage() {
  const [form, setForm] = useState(initialForm);
  const [transactions, setTransactions] = useState([]);
  const [components, setComponents] = useState([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function loadData() {
    const [transactionData, componentData] = await Promise.all([getTransactions(), getComponents()]);
    setTransactions(transactionData);
    setComponents(componentData);
  }

  useEffect(() => {
    loadData().catch(() => setError("Failed to load transactions."));
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
      await createTransaction({
        part_number: form.part_number,
        transaction_type: form.transaction_type,
        quantity: Number(form.quantity),
        performed_by: form.performed_by || null,
        remarks: form.remarks || null,
      });
      setForm(initialForm);
      setMessage("Transaction recorded successfully.");
      await loadData();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Failed to create transaction.");
    }
  }

  return (
    <section className="page-grid">
      <div className="card">
        <h1>Transactions</h1>
        <form className="form-grid" onSubmit={handleSubmit}>
          <FormInput
            label="Part Number"
            name="part_number"
            value={form.part_number}
            onChange={handleChange}
            type="select"
            required
            options={components.map((component) => ({
              value: component.part_number,
              label: `${component.part_number} - ${component.nomenclature}`,
            }))}
          />
          <FormInput
            label="Transaction Type"
            name="transaction_type"
            value={form.transaction_type}
            onChange={handleChange}
            type="select"
            required
            options={[
              { value: "Receipt", label: "Receipt" },
              { value: "Issue", label: "Issue" },
              { value: "Adjustment", label: "Adjustment" },
            ]}
          />
          <FormInput label="Quantity" name="quantity" value={form.quantity} onChange={handleChange} type="number" required />
          <FormInput label="Performed By" name="performed_by" value={form.performed_by} onChange={handleChange} />
          <FormInput label="Remarks" name="remarks" value={form.remarks} onChange={handleChange} type="textarea" />
          <button className="button" type="submit">Submit Transaction</button>
        </form>
        {message ? <p className="message message--success">{message}</p> : null}
        {error ? <p className="message message--error">{error}</p> : null}
      </div>

      <div className="card">
        <h2>Transaction Log</h2>
        <GeneratePDF data={transactions} />
        <TableView columns={columns} rows={transactions} emptyText="No transactions found." />
      </div>
    </section>
  );
}