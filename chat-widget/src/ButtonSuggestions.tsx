import React from "react";


function ButtonSuggestion({ message }: {message: string}): JSX.Element {
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
