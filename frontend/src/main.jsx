import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import "@gravity-ui/uikit/styles/fonts.css";
import "@gravity-ui/uikit/styles/styles.css";
import "./gravityStyles.css";
import App from "./App.jsx";

import { ThemeProvider } from "@gravity-ui/uikit";

createRoot(document.getElementById("root")).render(
  <ThemeProvider theme="light">
    <StrictMode>
      <App />
    </StrictMode>
  </ThemeProvider>
);
