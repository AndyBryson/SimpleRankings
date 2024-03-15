import 'bootstrap/dist/css/bootstrap.min.css';
import React, { useEffect } from 'react';
import SubmitMatch from "../components/SubmitMatch";
import MatchTable from "../components/MatchTable";

function Matches({ players, update_players, matches, update_matches, delete: canDelete, onDelete }) {

    useEffect(() => {
        update_matches();
    }, []);

    if (canDelete) {
        console.log("delete mode");
    }


    return (
        <div className="App">
            {/*<div className="container">*/}
            <MatchTable matches={matches} delete={canDelete} onDelete={onDelete} />
            <div className="row">
                <div className="col">
                    <SubmitMatch players={players} update_players={update_players} />
                </div>
            </div>
            {/*</div>*/}
        </div>
    );
}

export default Matches;
