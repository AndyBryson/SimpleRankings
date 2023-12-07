import 'bootstrap/dist/css/bootstrap.min.css';
import React, {useEffect, useState} from 'react';
import MatchTable from "../components/MatchTable";
import {getPlayersMatches, getPlayer} from "../rest_api";
import {json, useParams} from "react-router-dom";

function Profile() {
    const { id } = useParams();
    const [playersMatches, setPlayersMatches] = useState([]);
    const [player, setPlayer] = useState({});

    useEffect(() =>
    {
        getPlayersMatches(id).then(matches => {
            console.log(matches);
            setPlayersMatches(matches);
        });
        getPlayer(id).then(player => {
            console.log(player);
            setPlayer(player);
        });
    }, []);

    return (
        <div className="App">
            <div style={{
                paddingTop: '20px',
            }}>
                <h1>{player.name}</h1>
                <p>Current Rating: {Math.round(player.rating)}</p>
                <p>Games played: {player.wins + player.losses + player.draws}</p>
                <p>Wins: {player.wins}</p>
                <p>Losses: {player.losses}</p>
            </div>
            <MatchTable matches={playersMatches}/>
        </div>
    )
}

export default Profile;