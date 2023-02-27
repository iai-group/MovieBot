import { useEffect, useState, useRef } from "react";
import { MDBIcon } from "mdb-react-ui-kit";

export default function Feedback({
  message,
  on_feedback,
}: {
  message: string;
  on_feedback: (message: string, event: string) => void;
}): JSX.Element {
  const [liked, setLiked] = useState<boolean | null>(null);
  const thumbsUp = useRef<HTMLAnchorElement>(null);
  const thumbsDown = useRef<HTMLAnchorElement>(null);

  useEffect(() => {
    if (!!thumbsUp.current) {
      thumbsUp.current.addEventListener("click", () => {
        setLiked(true);
        on_feedback(message, "thumbs_up");
      });
    }
  }, [thumbsUp, on_feedback, message]);

  useEffect(() => {
    if (!!thumbsDown.current) {
      thumbsDown.current.addEventListener("click", () => {
        setLiked(false);
        on_feedback(message, "thumbs_down");
      });
    }
  }, [thumbsDown, on_feedback, message]);

  return (
    <div className="d-flex flex-row justify-content-end">
      <a className="text-muted px-1" href="#!" ref={thumbsUp}>
        <MDBIcon className={`${liked ? "fas" : "far"}`} icon="thumbs-up" />
      </a>
      <a className="text-muted pe-1" href="#!" ref={thumbsDown}>
        <MDBIcon
          className={`${liked !== null && !liked ? "fas" : "far"}`}
          icon="thumbs-down"
        />
      </a>
    </div>
  );
}
