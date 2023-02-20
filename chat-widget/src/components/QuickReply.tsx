import React from "react";
import { MDBBtn } from "mdb-react-ui-kit";

export default function QuickReplyButton({
  text,
  message,
  click,
}: {
  text: string;
  message: string;
  click: (message: string) => void;
}): JSX.Element {
  const handleClick = () => {
    console.log("Quick reply button clicked");
    click(message);
  };

  return (
    <MDBBtn outline className="btn-sm" color="secondary" onClick={handleClick}>
      {text}
    </MDBBtn>
  );
}
