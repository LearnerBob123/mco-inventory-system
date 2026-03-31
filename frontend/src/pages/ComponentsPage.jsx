import { useEffect, useState } from "react";

import FormInput from "../components/FormInput";
import TableView from "../components/TableView";
import {
  createComponent,
  createComponentUsage,
  getComponents,
  getHierarchyNodes,
} from "../services/api";

const initialForm = {
  part_number: "",
  nomenclature: "",
  gun_id: "",
  major_assembly_id: "",
  sub_assembly_id: "",
  ved_status: "",
  change_category: "",
  item_type: "",
  source_type: "",
  node_id: "",
  number_of: "",
  scale_percent: "",
};

const componentColumns = [
  { key: "part_number", label: "Part Number" },
  { key: "nomenclature", label: "Nomenclature" },
  { key: "gun_id", label: "Gun ID" },
  { key: "major_assembly_id", label: "Major Assembly ID" },
  { key: "sub_assembly_id", label: "Sub Assembly ID" },
  { key: "ved_status", label: "VED" },
  { key: "change_category", label: "Change Category" },
  { key: "item_type", label: "Item Type" },
  { key: "source_type", label: "Source Type" },
];

export default function ComponentsPage() {
  const [form, setForm] = useState(initialForm);
  const [components, setComponents] = useState([]);
  const [nodes, setNodes] = useState([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function loadData() {
    const [componentData, nodeData] = await Promise.all([getComponents(), getHierarchyNodes()]);
    setComponents(componentData);
    setNodes(nodeData);
  }

  useEffect(() => {
    loadData().catch(() => setError("Failed to load components or hierarchy nodes."));
  }, []);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((current) => {
      const next = { ...current, [name]: value };

      if (name === "gun_id") {
        next.major_assembly_id = "";
        next.sub_assembly_id = "";
      }

      if (name === "major_assembly_id") {
        next.sub_assembly_id = "";
      }

      return next;
    });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setMessage("");
    setError("");

    try {
      await createComponent({
        part_number: form.part_number,
        nomenclature: form.nomenclature,
        gun_id: Number(form.gun_id),
        major_assembly_id: form.major_assembly_id ? Number(form.major_assembly_id) : null,
        sub_assembly_id: form.sub_assembly_id ? Number(form.sub_assembly_id) : null,
        ved_status: form.ved_status,
        change_category: form.change_category,
        item_type: form.item_type,
        source_type: form.source_type,
      });

      if (form.node_id && form.number_of && form.scale_percent) {
        await createComponentUsage({
          node_id: Number(form.node_id),
          part_number: form.part_number,
          number_of: Number(form.number_of),
          scale_percent: Number(form.scale_percent),
        });
      }

      setForm(initialForm);
      setMessage("Component created successfully.");
      await loadData();
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail || requestError.message || "Failed to create component."
      );
    }
  }

  const nodeOptions = nodes.map((node) => ({
    value: String(node.id),
    label: `${node.id} - ${node.name} (${node.type})`,
  }));

  const gunOptions = nodes
    .filter((node) => node.type === "GUN")
    .map((node) => ({ value: String(node.id), label: `${node.id} - ${node.name}` }));

  const majorOptions = nodes
    .filter((node) => node.type === "MAJOR" && String(node.parent_id) === form.gun_id)
    .map((node) => ({ value: String(node.id), label: `${node.id} - ${node.name}` }));

  const subOptions = nodes
    .filter((node) => node.type === "SUB" && String(node.parent_id) === form.major_assembly_id)
    .map((node) => ({ value: String(node.id), label: `${node.id} - ${node.name}` }));

  return (
    <section className="page-grid">
      <div className="card">
        <h1>Component Management</h1>
        <p>Add records to component_v2 and optionally attach usage mapping.</p>
        <form className="form-grid" onSubmit={handleSubmit}>
          <FormInput label="Part Number" name="part_number" value={form.part_number} onChange={handleChange} required />
          <FormInput label="Nomenclature" name="nomenclature" value={form.nomenclature} onChange={handleChange} required />
          <FormInput
            label="Gun"
            name="gun_id"
            value={form.gun_id}
            onChange={handleChange}
            type="select"
            required
            options={gunOptions}
            placeholder="Select gun"
          />
          <FormInput
            label="Major Assembly"
            name="major_assembly_id"
            value={form.major_assembly_id}
            onChange={handleChange}
            type="select"
            options={majorOptions}
            placeholder="Optional major assembly"
          />
          <FormInput
            label="Sub Assembly"
            name="sub_assembly_id"
            value={form.sub_assembly_id}
            onChange={handleChange}
            type="select"
            options={subOptions}
            placeholder="Optional sub assembly"
          />
          <FormInput
            label="VED Status"
            name="ved_status"
            value={form.ved_status}
            onChange={handleChange}
            type="select"
            required
            options={[
              { value: "V", label: "V" },
              { value: "E", label: "E" },
              { value: "D", label: "D" },
            ]}
          />
          <FormInput
            label="Change Category"
            name="change_category"
            value={form.change_category}
            onChange={handleChange}
            type="select"
            required
            options={[
              { value: "MC", label: "MC" },
              { value: "CC", label: "CC" },
            ]}
          />
          <FormInput
            label="Item Type"
            name="item_type"
            value={form.item_type}
            onChange={handleChange}
            type="select"
            required
            options={[
              { value: "Expendable", label: "Expendable" },
              { value: "Non-Expendable", label: "Non-Expendable" },
            ]}
          />
          <FormInput
            label="Source Type"
            name="source_type"
            value={form.source_type}
            onChange={handleChange}
            type="select"
            required
            options={[
              "OSS",
              "LP",
              "IR&D",
              "LRC",
              "LM",
              "Cannibalization",
              "Reclamation",
              "ERC",
            ].map((value) => ({ value, label: value }))}
          />
          <FormInput
            label="Usage Node ID"
            name="node_id"
            value={form.node_id}
            onChange={handleChange}
            type="select"
            options={nodeOptions}
            placeholder="Optional usage node"
          />
          <FormInput label="Number Of" name="number_of" value={form.number_of} onChange={handleChange} type="number" />
          <FormInput label="Scale Percent" name="scale_percent" value={form.scale_percent} onChange={handleChange} type="number" />
          <button className="button" type="submit">Submit</button>
        </form>
        {message ? <p className="message message--success">{message}</p> : null}
        {error ? <p className="message message--error">{error}</p> : null}
      </div>

      <div className="card">
        <h2>All Components</h2>
        <TableView columns={componentColumns} rows={components} emptyText="No component_v2 records found." />
      </div>
    </section>
  );
}