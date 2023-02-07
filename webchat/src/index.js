import 'bootstrap';
import ChatBox from "./lib/chat";

const chatWidget = document.createElement("chat-widget");
document.body.appendChild(chatWidget);
customElements.define("chat-widget", ChatBox);
