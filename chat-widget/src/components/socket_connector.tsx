import { useState, useEffect } from "react";
import io, { Socket } from "socket.io-client";
import { AgentMessage, UserMessage, ChatMessage } from "../types";

export default function useSocketConnection(
  url: string = "http://127.0.0.1:5000/chat"
) {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const newSocket = io(url);
    setSocket(newSocket);

    newSocket.on("connect", () => {
      setIsConnected(true);
    });

    newSocket.on("disconnect", () => {
      setIsConnected(false);
    });

    return () => {
      newSocket.disconnect();
    };
  }, [url]);

  const sendMessage = (message: UserMessage) => {
    socket?.emit("message", message);
  };

  const quickReply = (message: UserMessage) => {
    socket?.emit("message", message);
  };

  const giveFeedback = (message: string, event: string) => {
    socket?.emit("feedback", { message: message, event: event });
  };

  const onMessage = (callback: (response: ChatMessage) => void) => {
    socket?.on("message", (response: AgentMessage) => {
      if (response.info) {
        console.log(response.info);
      }
      if (response.message) {
        callback(response.message);
      }
    });
  };

  const onRestart = (callback: () => void) => {
    socket?.on("restart", callback);
  };

  return {
    isConnected,
    sendMessage,
    giveFeedback,
    quickReply,
    onMessage,
    onRestart,
  };
}
