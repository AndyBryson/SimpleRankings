import 'bootstrap/dist/css/bootstrap.min.css';
import React, {useEffect, useState} from 'react';
import MatchTable from "../components/MatchTable";
import {getPlayersMatches, getPlayer} from "../rest_api";
import {json, useParams} from "react-router-dom";
import Plot from "react-plotly.js";

function Profile() {
    const { id } = useParams();
    const [playersMatches, setPlayersMatches] = useState([]);
    const [player, setPlayer] = useState({});
    const [ratingOverTime, setRatingOverTime] = useState([]);

    useEffect(() =>
    {
        getPlayersMatches(id).then(matches => {
            console.log(matches);
            matches.sort((a, b) => (a.date < b.date) ? 1 : -1);

            setRatingOverTime(matches.map(match => {
                if (match.winner_name === player.name) {
                    return {
                        x: match.date,
                        y: Math.round(match.winner_rating)
                    }
                }
                return {
                    x: match.date,
                    y: Math.round(match.loser_rating)
                }
            }));

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
            <div style={{ display: 'flex', height: '100%', width: '100%' }}>
                <Plot
                    data={[
                        {
                            x: ratingOverTime.map(x => x.x),
                            y: ratingOverTime.map(x => x.y),
                            type: 'scatter',
                            mode: 'lines+markers',
                            marker: {color: 'red'},
                        },
                    ]}
                    layout={ { title: 'Rating over time' } }
                    style={{ width: '100%', height: '200%' }}
                />
            </div>
            <MatchTable matches={playersMatches}/>
        </div>
    )
}

export default Profile;