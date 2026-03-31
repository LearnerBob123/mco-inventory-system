import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard" },
  { to: "/hierarchy", label: "Hierarchy" },
  { to: "/components", label: "Components" },
  { to: "/inventory", label: "Inventory" },
  { to: "/transactions", label: "Transactions" },
  { to: "/lifecycle", label: "Lifecycle" },
];

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar__brand">MCO Inventory</div>
      <div className="navbar__links">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              isActive ? "navbar__link navbar__link--active" : "navbar__link"
            }
          >
            {link.label}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}