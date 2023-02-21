import "./ChatBox.css";

import React, { useState, useEffect, useRef } from "react";
import useSocketConnection from "./socket_connector";
import QuickReplyButton from "./QuickReply";

import {
  MDBCard,
  MDBCardHeader,
  MDBCardBody,
  MDBIcon,
  MDBCardFooter,
} from "mdb-react-ui-kit";
import { AgentChatMessage, UserChatMessage } from "./ChatMessage";
import { ChatMessage } from "../types";

export default function ChatBox({
  onClose,
}: {
  onClose: (event: React.MouseEvent<HTMLAnchorElement>) => void;
}) {
  const [chatMessages, setChatMessages] = useState<JSX.Element[]>([]);
  const [chatButtons, setChatButtons] = useState<JSX.Element[]>([]);
  const [inputValue, setInputValue] = useState<string>("");
  const chatMessagesRef = useRef(chatMessages);
  const inputRef = useRef<HTMLInputElement>(null);
  const connector = useSocketConnection();

  const handleInput = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (inputValue.trim() === "") return;
    chatMessagesRef.current = [
      ...chatMessagesRef.current,
      <UserChatMessage
        key={chatMessagesRef.current.length}
        message={inputValue}
      />,
    ];
    setChatMessages(chatMessagesRef.current);
    connector.sendMessage({ message: inputValue });
    setInputValue("");
    if (inputRef.current) {
      inputRef.current.value = "";
    }
  };

  const handleQuickReply = (message: string) => {
    chatMessagesRef.current = [
      ...chatMessagesRef.current,
      <UserChatMessage
        key={chatMessagesRef.current.length}
        message={message}
      />,
    ];
    setChatMessages(chatMessagesRef.current);
    connector.quickReply({ message: message });
  };

  useEffect(() => {
    connector.onMessage((message: ChatMessage) => {
      if (!!message.text) {
        const movie_url = message.attachment?.payload.url;
        chatMessagesRef.current = [
          ...chatMessages,
          <AgentChatMessage
            key={chatMessages.length}
            feedback={connector.giveFeedback}
            message={message.text}
            movie_url={movie_url}
          />,
        ];
        setChatMessages(chatMessagesRef.current);
      }
      const buttons = message.attachment?.payload.buttons;
      if (!!buttons && buttons.length > 0) {
        setChatButtons(
          buttons.map((button, index) => {
            return (
              <QuickReplyButton
                key={index}
                text={button.title}
                message={button.payload}
                click={handleQuickReply}
              />
            );
          })
        );
      } else {
        setChatButtons([]);
      }
    });
  }, [connector, chatMessages]);

  useEffect(() => {
    connector.onRestart(() => {
      setChatMessages([]);
      setChatButtons([]);
    });
  }, [connector]);

  return (
    <MDBCard
      id="chatBox"
      className="chat-widget-card"
      style={{ borderRadius: "15px" }}
    >
      <MDBCardHeader
        className="d-flex justify-content-between align-items-center p-3 bg-info text-white border-bottom-0"
        style={{
          borderTopLeftRadius: "15px",
          borderTopRightRadius: "15px",
        }}
      >
        <p className="mb-0 fw-bold">MovieBot</p>
        <a href="!#" onClick={onClose} style={{ color: "white" }}>
          <MDBIcon fas icon="angle-down" />
        </a>
      </MDBCardHeader>

      <MDBCardBody>
        <div className="card-body-messages">
          {chatMessages}
          <div className="d-flex flex-wrap justify-content-between">
            {chatButtons}
          </div>
        </div>
      </MDBCardBody>
      <MDBCardFooter className="text-muted d-flex justify-content-start align-items-center p-2">
        <form className="d-flex flex-grow-1" onSubmit={handleInput}>
          <input
            type="text"
            className="form-control form-control-lg"
            id="ChatInput"
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type message"
            ref={inputRef}
          ></input>
          {/* <MTDTextArea 
                  className="form-control form-control-lg" 
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Type message"
                ></MTDTextArea> */}
          <button type="submit" className="btn btn-link">
            <MDBIcon
              fas
              size="2x"
              style={{ color: "Green" }}
              icon="paper-plane"
            />
          </button>
        </form>
      </MDBCardFooter>
    </MDBCard>
  );
}
