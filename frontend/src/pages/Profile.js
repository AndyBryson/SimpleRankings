import 'bootstrap/dist/css/bootstrap.min.css';
import React, {useEffect, useState} from 'react';
import MatchTable from "../components/MatchTable";
import {getPlayersMatches, getPlayer} from "../rest_api";
import {json, useParams} from "react-router-dom";
import Plot from "react-plotly.js";
import SnowFall from "react-snowfall";


function RatingMap(matches) {
    console.log("matches", matches);
    let player = matches.player;
    let players_matches = [...matches.matches].sort((a, b) => { return new Date(a.date) - new Date(b.date) });
    let x = players_matches.map(match => {
        return match.date;
    });
    let y = players_matches.map(match => {
        if (match.winner_name === player.name) {
            return Math.round(match.winner_rating);
        }
        return Math.round(match.loser_rating)
    });
    console.log("player", player);
    console.log("players_matches", players_matches);
    console.log("x", x);
    console.log("y", y);

    const data = [{
        x: x,
        y: y,
        type: 'scatter',
        mode: 'lines+markers',
        marker: {color: 'red'}
    }]
    console.log("data", data);

    return (
        <Plot
            data={data}
            layout={ { title: 'Rating over time' } }
            style={{ width: '100%', height: '100%' }}
        />
    )
}

function Profile() {
    const { id } = useParams();
    const [playersMatches, setPlayersMatches] = useState([]);
    const [player, setPlayer] = useState({});
    const [ratingOverTime, setRatingOverTime] = useState([]);

    useEffect(() =>
    {
        getPlayersMatches(id).then(matches => {
            setPlayersMatches(matches);
        });
        getPlayer(id).then(player => {
            console.log(player);
            setPlayer(player);
        });
    }, []);

    return (
        <div className="App">
            <SnowFall />
            <div style={{
                paddingTop: '20px',
            }}>
                <h1>{player.name}</h1>
                <p>Current Rating: {Math.round(player.rating)}</p>
                <p>Games played: {player.wins + player.losses + player.draws}</p>
                <p>Wins: {player.wins}</p>
                <p>Losses: {player.losses}</p>
            </div>
            <div style={{ display: 'flex', height: '100%', width: '100%' }}>
                <RatingMap matches={playersMatches} player={player}/>
                {/*<Plot*/}
                {/*    data={[*/}
                {/*        {*/}
                {/*            x: ratingOverTime.map(x => x.x),*/}
                {/*            y: ratingOverTime.map(x => x.y),*/}
                {/*            type: 'scatter',*/}
                {/*            mode: 'lines+markers',*/}
                {/*            marker: {color: 'red'},*/}
                {/*        },*/}
                {/*    ]}*/}
                {/*    layout={ { title: 'Rating over time' } }*/}
                {/*    style={{ width: '100%', height: '200%' }}*/}
                {/*/>*/}
            </div>
            <MatchTable matches={playersMatches}/>
        </div>
    )
}

export default Profile;