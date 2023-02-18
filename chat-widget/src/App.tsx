import React, { useState, useEffect, useRef } from "react";
import io from "socket.io-client";

import {
  MDBContainer,
  MDBRow,
  MDBCol,
  MDBCard,
  MDBCardHeader,
  MDBCardBody,
  MDBIcon,
  MDBCardFooter,
  MDBBtn,
} from "mdb-react-ui-kit";
import { AgentChatMessage, UserChatMessage } from "./ChatMessage";

const socket = io("http://127.0.0.1:5000");

type ChatMessage = {
  message: string;
  id?: string;
  buttons?: string[];
};

export default function App() {
  const [chatMessages, setChatMessages] = useState<JSX.Element[]>([]);
  const [chatButtons, setChatButtons] = useState<JSX.Element[]>([]);
  const [inputValue, setInputValue] = useState<string>("");
  const inputRef = useRef<HTMLInputElement>(null);
  const thumbsUp = useRef<HTMLButtonElement>(null);
  const thumbsDown = useRef<HTMLButtonElement>(null);

  function handleInput(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (inputValue.trim() === "") return;
    setChatMessages([
      ...chatMessages,  
      <UserChatMessage key={chatMessages.length} message={inputValue} />,
    ]);
    socket.emit("message", {"message": inputValue});
    setInputValue("");
    if (inputRef.current) {
      inputRef.current.value = "";
    }
  }

  useEffect(() => {
    socket.on('message', (data: ChatMessage) => {
      setChatMessages([
        ...chatMessages,
        <AgentChatMessage key={chatMessages.length} message={data.message} />,
      ]);
      if (data.buttons && data.buttons?.length > 0) {
        setChatButtons(data.buttons.map((button, index) => {
          return (
            <MDBBtn
              key={index}
              outline className='btn-sm' color='secondary'
            >
              {button}
            </MDBBtn>
          );
        }));
      }
    });
  });

useEffect(() => {
  socket.on('reset', (data: string) => {
    setChatMessages([]);
    setChatButtons([]);
  });
});

  return (
    <MDBContainer className="py-5">
      <MDBRow className="d-flex justify-content-center">
        <MDBCol md="8" lg="6" xl="4">
          <MDBCard id="chat1" style={{ borderRadius: "15px" }}>
            <MDBCardHeader
              className="d-flex justify-content-between align-items-center p-3 bg-info text-white border-bottom-0"
              style={{
                borderTopLeftRadius: "15px",
                borderTopRightRadius: "15px",
              }}
            >
              <p className="mb-0 fw-bold">Parrot Bot</p>
              <MDBIcon fas icon="angle-down" />
            </MDBCardHeader>

            <MDBCardBody>
              {chatMessages}
              <div className="d-flex flex-wrap justify-content-between">
              {chatButtons}
              </div>
            </MDBCardBody>
            <MDBCardFooter className="text-muted d-flex justify-content-start align-items-center p-2">
              <a  className="p-2 text-muted" href="#!"><MDBIcon far style={{ color: 'DodgerBlue' }} size="2x" icon="thumbs-up" ref={thumbsUp}/></a>
              <a  className="pe-2 text-muted" href="#!"><MDBIcon far style={{ color: 'DodgerBlue' }} size="2x" icon="thumbs-down" ref={thumbsDown}/></a>
              <form className="d-flex" onSubmit={handleInput}>
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
                <button type='submit' className="btn btn-link"><MDBIcon fas size="2x" style={{ color: 'Green' }} icon="paper-plane"/></button>
              </form>
            </MDBCardFooter>
          </MDBCard>
        </MDBCol>
      </MDBRow>
    </MDBContainer>
  );
}