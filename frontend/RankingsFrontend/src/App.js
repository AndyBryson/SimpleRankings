import 'bootstrap/dist/css/bootstrap.min.css';
import React, { useState, useEffect } from 'react';
import SubmitMatch from "./SubmitMatch";
import PlayerTable from "./PlayerTable";
import { addPlayer, getPlayers } from "./rest_api";

function App() {
    const [players, setPlayers] = useState([]);

    function update_players() {
        return getPlayers().then(players => setPlayers(players));
    }

    useEffect(() => {
        if (players.length < 1) {
            update_players();
        }
    });

    return (
        <div className="App">
            <div className="container">
                <PlayerTable players={players}/>
                <div className="row">
                    <div className="col">
                        <SubmitMatch players={players} update_players={update_players} />
                        <button type="button" className="btn btn-primary ms-2" onClick={() => addPlayer({update_players})}>Add Player</button>
                    </div>

                </div>
            </div>
        </div>
    );
}

export default App;
