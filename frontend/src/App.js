import 'bootstrap/dist/css/bootstrap.min.css';
import React from 'react';

import Main from './Main';
import {Link} from "react-router-dom";

const Navbar = () => {
      return (
    <nav className="navbar navbar-expand-lg navbar-light bg-light">
      <Link className="navbar-brand" to="/">
        BAR Tech Pool
      </Link>
      <button
        className="navbar-toggler"
        type="button"
        data-toggle="collapse"
        data-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span className="navbar-toggler-icon"></span>
      </button>
      <div className="collapse navbar-collapse" id="navbarNav">
        <ul className="navbar-nav">
          <li className="nav-item">
            <Link className="nav-link" to="/">
              Rankings
            </Link>
          </li>
          <li className="nav-item">
            <Link className="nav-link" to="/matches">
              Matches
            </Link>
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
