import 'bootstrap/dist/css/bootstrap.min.css';
import React from 'react';

import Main from './Main';
import {NavLink} from "react-router-dom";

const Navbar = () => {
      return (
    <nav className="navbar navbar-expand-lg navbar-light">
      <NavLink className="navbar-brand" to="/">
          Pool
      </NavLink>
      <button
        className="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span className="navbar-toggler-icon"></span>
      </button>
      <div className="collapse navbar-collapse" id="navbarNav">
        <ul className="navbar-nav">
          <li className="nav-item">
            <NavLink className="nav-link" to="/">
              Rankings
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink className="nav-link" to="/matches">
              Matches
            </NavLink>
          </li>
        </ul>
      </div>
    </nav>
  );
};

function App() {
    return (
        <div className="App container">
            <Navbar />
            <Main />
        </div>
    );
}

export default App;
