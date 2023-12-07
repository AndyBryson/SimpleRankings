import 'bootstrap/dist/css/bootstrap.min.css';
import React from 'react';
import SubmitMatch from "../components/SubmitMatch";
import PlayerTable from "../components/PlayerTable";
import { addPlayer } from "../rest_api";
import SnowFall from 'react-snowfall';
function Home({players, update_players}){
    return (
        <div className="App">
            <SnowFall />
            {/*<div className="container">*/}
                <PlayerTable players={players}/>
                <div className="row">
                    <div className="col">
                        <SubmitMatch players={players} update_players={update_players} />
                        <button type="button" className="btn btn-primary ms-2" onClick={() => addPlayer({update_players})}>Add Player</button>
                    </div>
                </div>
            {/*</div>*/}
        </div>
    );
}

export default Home;
