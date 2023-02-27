import React from "react";
import ReactDOM from "react-dom/client";
import "mdb-react-ui-kit/dist/css/mdb.min.css";
import "@fortawesome/fontawesome-free/css/all.min.css";
import "./index.css";
import App from "./App";
import reportWebVitals from "./reportWebVitals";
import { Config } from "./types";

let root: ReactDOM.Root;

const initChatWidget = (
  config: Config | undefined = undefined,
  widgetContainerID: string | undefined = "chatWidgetContainer"
) => {
  let widgetContainer: HTMLElement | null =
    document.getElementById(widgetContainerID);
  if (!widgetContainer) {
    widgetContainer = document.createElement("div");
    widgetContainer.id = "chatWidgetContainer";
    document.body.appendChild(widgetContainer);
  }

  config = {
    serverUrl:
      config?.serverUrl ||
      widgetContainer?.getAttribute("data-server-url") ||
      "http://127.0.0.1:5000/chat",
    useFeedback:
      config?.useFeedback ?? widgetContainer?.hasAttribute("data-use-feedback"),
    useLogin:
      config?.useLogin ?? widgetContainer?.hasAttribute("data-use-login"),
  };

  if (!root) {
    root = ReactDOM.createRoot(widgetContainer as HTMLElement);
  }

  root.render(
    <React.StrictMode>
      <App {...config} />
    </React.StrictMode>
  );
};

declare global {
  interface Window {
    ChatWidget: typeof initChatWidget;
  }
}

if (document.getElementById("chatWidgetContainer")) {
  initChatWidget();
}
window.ChatWidget = initChatWidget;

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
