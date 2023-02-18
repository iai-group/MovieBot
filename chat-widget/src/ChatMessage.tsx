import React from "react";

interface ChatMessageProps {
  key: number;
  message: string;
  name?: string;
  image?: string;
}


function UserChatMessage({ message }: {message: string}): JSX.Element {
  return (
    <div className="d-flex flex-row justify-content-end mb-4">
      <div
        className="p-3 ms-3 border"
        style={{ borderRadius: "15px", backgroundColor: "#fbfbfb" }}
      >
        <p className="small mb-0">
          {message}
        </p>
      </div>
      <img
        src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava2-bg.webp"
        alt="User"
        style={{ width: "45px", height: "100%" }}
      />
    </div>
  );
}

function AgentChatMessage({ message }: {message: string}): JSX.Element {
    return (
      <div className="d-flex flex-row justify-content-start mb-4">
        <img
          src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava1-bg.webp"
          alt="Agent"
          style={{ width: "45px", height: "100%" }}
        />
        <div
          className="p-3 ms-3"
          style={{
            borderRadius: "15px",
            backgroundColor: "rgba(57, 192, 237,.2)",
          }}
        >
          <p className="small mb-0">
            {message}
          </p>
        </div>
      </div>
    );
  }

export { UserChatMessage, AgentChatMessage };