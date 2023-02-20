import "./App.css";
import React, { useState, useEffect, useRef, MouseEvent } from "react";
import ChatBox from "./components/ChatBox";
import { MDBIcon } from "mdb-react-ui-kit";

export default function App() {
  const [isChatBoxOpen, setIsChatBoxOpen] = useState<Boolean>(false);
  const contentRef = useRef<HTMLDivElement>(null);
  const elementRef = useRef<HTMLDivElement>(null);

  function handleClick(event: MouseEvent<HTMLAnchorElement>) {
    setIsChatBoxOpen(isChatBoxOpen ? false : true);
  }

  // useEffect(() => {
  //   if (contentRef.current && elementRef.current) {
  //     const contentHeight = contentRef.current.offsetHeight;
  //     elementRef.current.style.height = `${contentHeight}px`;
  //   }
  // }, []);

  return (
    <div className="chat-widget-container">
      <div className="chat-widget-icon">
        <a href="#" onClick={handleClick}>
          <MDBIcon fas icon="robot" />
        </a>
      </div>
      {/* <MDBContainer className="py-5">
        <MDBRow className="d-flex justify-content-center">
          <MDBCol md="8" lg="6" xl="4"> */}
      <div className="chat-widget-box" ref={elementRef}>
        <div className="chat-widget-content" ref={contentRef}>
          {isChatBoxOpen && <ChatBox onClose={handleClick} />}
        </div>
      </div>
      {/* </MDBCol>
        </MDBRow>
      </MDBContainer> */}
    </div>
  );
}
