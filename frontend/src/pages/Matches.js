import 'bootstrap/dist/css/bootstrap.min.css';
import React, {useEffect} from 'react';
import SubmitMatch from "../components/SubmitMatch";
import MatchTable from "../components/MatchTable";

function Matches({players, update_players, matches, update_matches}) {

    useEffect(() => {
        update_matches();
    }, []);

    return (
        <div className="App">
            {/*<div className="container">*/}
                <MatchTable matches={matches}/>
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
