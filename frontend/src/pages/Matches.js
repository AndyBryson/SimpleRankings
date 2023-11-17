import 'bootstrap/dist/css/bootstrap.min.css';
import React from 'react';
import SubmitMatch from "../components/SubmitMatch";

function Matches({players, update_players}) {

    return (
        <div className="App">
            <div className="container">
                <div className="row">
                    <div className="col">
                        <SubmitMatch players={players} update_players={update_players} />
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Matches;
