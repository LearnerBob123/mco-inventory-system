const toneMap = {
  OPEN: "is-open",
  IN_PROGRESS: "is-progress",
  QA_PENDING: "is-qa",
  COMPLETED: "is-completed",
};

export default function StatusPill({ status }) {
  const toneClass = toneMap[status] ?? "is-neutral";
  return <span className={`status-pill ${toneClass}`}>{status}</span>;
}
