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
    click(message);
  };

  return (
    <MDBBtn outline className="btn-sm" color="secondary" onClick={handleClick}>
      {text}
    </MDBBtn>
  );
}
