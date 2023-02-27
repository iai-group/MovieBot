import "./App.css";
import { useState, MouseEvent } from "react";
import ChatBox from "./components/ChatBox";
import { MDBIcon } from "mdb-react-ui-kit";
import useSocketConnection from "./components/socket_connector";
import { Config } from "./types";

export default function App(props: Config) {
  const [isChatBoxOpen, setIsChatBoxOpen] = useState<boolean>(false);
  const connector = useSocketConnection(props.serverUrl, isChatBoxOpen);

  function handleClick(event: MouseEvent<HTMLAnchorElement>) {
    setIsChatBoxOpen(isChatBoxOpen ? false : true);
  }

  return (
    <div className="chat-widget-container">
      <div className="chat-widget-icon">
        <a href="#!" onClick={handleClick} className="text-muted">
          <MDBIcon fas icon="robot" />
        </a>
      </div>
      {/* <MDBContainer className="py-5">
        <MDBRow className="d-flex justify-content-center">
          <MDBCol md="8" lg="6" xl="4"> */}
      <div className="chat-widget-box">
        <div className="chat-widget-content">
          {isChatBoxOpen && (
            <ChatBox
              onClose={handleClick}
              connector={connector}
              use_feedback={props.useFeedback || false}
            />
          )}
        </div>
      </div>
      {/* </MDBCol>
        </MDBRow>
      </MDBContainer> */}
    </div>
  );
}
