import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter } from "react-router-dom";
import "./index.css";
import App from "./components/App";

fetch('http://localhost:5000/restaurants')  // or use the actual backend IP and port
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(err => console.error("Fetch error:", err));



ReactDOM.render(
  <BrowserRouter>
    <App />
  </BrowserRouter>,
  document.getElementById("root")
);
