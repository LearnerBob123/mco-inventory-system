export default function SectionCard({ eyebrow, title, children, aside }) {
  return (
    <section className="section-card">
      <div className="section-card__header">
        <div>
          {eyebrow ? <p className="section-card__eyebrow">{eyebrow}</p> : null}
          <h2>{title}</h2>
        </div>
        {aside ? <div className="section-card__aside">{aside}</div> : null}
      </div>
      <div className="section-card__body">{children}</div>
    </section>
  );
}
