import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import "./styles/tokens.css";
import "./styles/base.css";
import "./styles/materials.css";
import "./styles/motion.css";

const container = document.createElement("div");
document.body.append(container);
createRoot(container).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
