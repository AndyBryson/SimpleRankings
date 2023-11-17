import 'bootstrap/dist/css/bootstrap.min.css';
import React from 'react';

import Main from './Main';
import {Navbar} from "react-bootstrap";

function App() {
    return (
        <div className="App">
            <Navbar />
            <Main />
        </div>
    );
}

export default App;
