import { useState, useEffect, useRef } from "react";
import io, { Socket } from "socket.io-client";
import { AgentMessage, UserMessage, ChatMessage } from "../types";

export default function useSocketConnection(
  url: string = "http://127.0.0.1:5000/chat",
  makeNewConnection: boolean = false
) {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const onMessageRef = useRef<(message: ChatMessage) => void>();
  const onRestartRef = useRef<() => void>();

  useEffect(() => {
    if (!makeNewConnection) {
      return;
    }
    const newSocket = io(url);
    setSocket(newSocket);

    newSocket.on("connect", () => {
      setIsConnected(true);
    });

    newSocket.on("disconnect", () => {
      setIsConnected(false);
    });

    newSocket.on("message", (response: AgentMessage) => {
      if (response.info) {
        console.log(response.info);
      }
      if (response.message) {
        onMessageRef.current && onMessageRef.current(response.message);
      }
    });

    newSocket.on("restart", () => {
      onRestartRef.current && onRestartRef.current();
    });

    return () => {
      newSocket.disconnect();
    };
  }, [url, makeNewConnection]);

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
    onMessageRef.current = callback;
  };

  const onRestart = (callback: () => void) => {
    onRestartRef.current = callback;
  };

  return {
    isConnected,
    sendMessage,
    giveFeedback,
    quickReply,
    onRestart,
    onMessage,
  };
}
