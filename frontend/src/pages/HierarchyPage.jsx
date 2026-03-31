import { useEffect, useState } from "react";

import FormInput from "../components/FormInput";
import { createHierarchyNode, getHierarchyNodes, getHierarchyTree } from "../services/api";

const initialForm = {
  type: "",
  name: "",
  parent_id: "",
};

function TreeNode({ node, level = 0 }) {
  return (
    <div className="tree-node" style={{ marginLeft: `${level * 16}px` }}>
      <div className="tree-node__label">
        <strong>{node.type}</strong> #{node.id} - {node.name}
      </div>
      {node.component_usages?.length ? (
        <div className="tree-node__meta">
          Components: {node.component_usages.map((usage) => usage.part_number).join(", ")}
        </div>
      ) : null}
      {node.children?.map((child) => (
        <TreeNode key={child.id} node={child} level={level + 1} />
      ))}
    </div>
  );
}

export default function HierarchyPage() {
  const [form, setForm] = useState(initialForm);
  const [nodes, setNodes] = useState([]);
  const [tree, setTree] = useState([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function loadData() {
    const [nodeData, treeData] = await Promise.all([getHierarchyNodes(), getHierarchyTree()]);
    setNodes(nodeData);
    setTree(treeData.tree || []);
  }

  useEffect(() => {
    loadData().catch(() => setError("Failed to load hierarchy data."));
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
      await createHierarchyNode({
        type: form.type,
        name: form.name,
        parent_id: form.parent_id ? Number(form.parent_id) : null,
      });
      setForm(initialForm);
      setMessage("Hierarchy node created successfully.");
      await loadData();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Failed to create hierarchy node.");
    }
  }

  const typeSpecificParents =
    form.type === "MAJOR"
      ? nodes.filter((node) => node.type === "GUN")
      : form.type === "SUB"
        ? nodes.filter((node) => node.type === "MAJOR")
        : [];

  return (
    <section className="page-grid">
      <div className="card">
        <h1>Hierarchy Management</h1>
        <p>Create guns, major assemblies, and sub assemblies in hierarchy_node.</p>
        <form className="form-grid" onSubmit={handleSubmit}>
          <FormInput
            label="Node Type"
            name="type"
            value={form.type}
            onChange={handleChange}
            type="select"
            required
            options={[
              { value: "GUN", label: "GUN" },
              { value: "MAJOR", label: "MAJOR" },
              { value: "SUB", label: "SUB" },
            ]}
          />
          <FormInput label="Name" name="name" value={form.name} onChange={handleChange} required />
          <FormInput
            label="Parent"
            name="parent_id"
            value={form.parent_id}
            onChange={handleChange}
            type="select"
            options={typeSpecificParents.map((node) => ({
              value: String(node.id),
              label: `${node.id} - ${node.name} (${node.type})`,
            }))}
            placeholder={form.type === "GUN" ? "No parent for GUN" : "Select parent"}
          />
          <button className="button" type="submit">Create Node</button>
        </form>
        {message ? <p className="message message--success">{message}</p> : null}
        {error ? <p className="message message--error">{error}</p> : null}
      </div>

      <div className="card">
        <h2>Hierarchy Tree</h2>
        {tree.length ? tree.map((node) => <TreeNode key={node.id} node={node} />) : <div className="empty-state">No hierarchy nodes found.</div>}
      </div>
    </section>
  );
}