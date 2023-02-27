import React from "react";
import { render, screen } from "@testing-library/react";
import App from "../App";
import { Config } from "../types";

test("renders learn react link", () => {
  const config: Config = {
    serverUrl: "http://localhost:5000/chat",
    useFeedback: false,
    useLogin: false,
  };
  render(<App {...config} />);
  const linkElement = screen.getByText(/learn react/i);
  expect(linkElement).toBeInTheDocument();
});
