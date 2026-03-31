export default function FormInput({
  label,
  name,
  value,
  onChange,
  type = "text",
  options = [],
  placeholder,
  required = false,
}) {
  return (
    <label className="form-field">
      <span className="form-field__label">{label}</span>
      {type === "select" ? (
        <select name={name} value={value} onChange={onChange} required={required}>
          <option value="">{placeholder || `Select ${label}`}</option>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      ) : type === "textarea" ? (
        <textarea
          name={name}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          required={required}
          rows={3}
        />
      ) : (
        <input
          type={type}
          name={name}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          required={required}
        />
      )}
    </label>
  );
}