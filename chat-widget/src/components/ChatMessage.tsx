import { useEffect, useState, useRef } from "react";
import { MDBIcon } from "mdb-react-ui-kit";

function UserChatMessage({ message }: { message: string }): JSX.Element {
  return (
    <div className="d-flex flex-row justify-content-end mb-4">
      <div
        className="p-3 ms-3 border"
        style={{ borderRadius: "15px", backgroundColor: "#fbfbfb" }}
      >
        <p className="small mb-0">{message}</p>
      </div>
      <img
        src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava2-bg.webp"
        alt="User"
        style={{ width: "45px", height: "100%" }}
      />
    </div>
  );
}

function AgentChatMessage({
  message,
  movie_url,
  feedback,
}: {
  message: string;
  movie_url?: string;
  feedback: (message: string, event: string) => void;
}): JSX.Element {
  const [liked, setLiked] = useState<boolean | null>(null);
  const thumbsUp = useRef<HTMLAnchorElement>(null);
  const thumbsDown = useRef<HTMLAnchorElement>(null);

  useEffect(() => {
    if (!!thumbsUp.current) {
      thumbsUp.current.addEventListener("click", () => {
        setLiked(true);
        feedback(message, "thumbs_up");
      });
    }
  }, [thumbsUp, feedback, message]);

  useEffect(() => {
    if (!!thumbsDown.current) {
      thumbsDown.current.addEventListener("click", () => {
        setLiked(false);
        feedback(message, "thumbs_down");
      });
    }
  }, [thumbsDown, feedback, message]);

  return (
    <div className="d-flex flex-row justify-content-start mb-4">
      {/* <img
          src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava1-bg.webp"
          alt="Agent"
          style={{ width: "45px", height: "100%" }}
        /> */}
      <div
      // style={{ width: "50px", height: "40px", borderRadius: "25px", backgroundColor: "lightblue"}}
      // className="d-flex align-items-center"
      >
        <MDBIcon fas size="2x" style={{ color: "black" }} icon="robot" />
      </div>
      <div
        className="p-3 ms-3"
        style={{
          borderRadius: "15px",
          backgroundColor: "rgba(57, 192, 237,.2)",
        }}
      >
        {!!movie_url && (
          <div className="d-flex flex-row justify-content-center">
            <img
              src={movie_url}
              alt="Movie Poster"
              style={{ width: "200px", height: "100%" }}
            />
          </div>
        )}
        <p className="small mb-0">{message}</p>
        <div className="d-flex flex-row justify-content-end">
          <a className="p-1 text-muted" href="#!" ref={thumbsUp}>
            <MDBIcon
              className={`${liked ? "fas" : "far"}`}
              style={{ color: "DodgerBlue" }}
              size="lg"
              icon="thumbs-up"
            />
          </a>
          <a className="p-1 text-muted" href="#!" ref={thumbsDown}>
            <MDBIcon
              className={`${liked !== null && !liked ? "fas" : "far"}`}
              style={{ color: "DodgerBlue" }}
              size="lg"
              icon="thumbs-down"
            />
          </a>
        </div>
      </div>
    </div>
  );
}

export { UserChatMessage, AgentChatMessage };
