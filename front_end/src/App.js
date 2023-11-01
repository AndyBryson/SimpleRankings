import 'bootstrap/dist/css/bootstrap.min.css';
import React, { useState, useEffect } from 'react';

const API_URL = process.env.API_URL || 'http://localhost:8080';
const PLAYERS_ENDPOINT = `${API_URL}/players`;


function getPlayers() {
    return fetch(PLAYERS_ENDPOINT)
        .then(response => response.json())
        .then(data => {
          data.sort((a, b) => (a.rating < b.rating) ? 1 : -1);
          return data;
        })
        .catch(error => { console.log(error); });
}

function PlayerTable({players}) {
  return (
        <table className="table table-hover">
            <thead>
            <tr>
                <th>Name</th>
                <th>Wins</th>
                <th>Losses</th>
                <th>Rating</th>
            </tr>
            </thead>
            <tbody>
            {players.map(player => (
                <tr key={player.id}>
                    <td>{player.name}</td>
                    <td>{player.wins}</td>
                    <td>{player.losses}</td>
                    <td>{Math.round(player.rating)}</td>
                </tr>
            ))}
            </tbody>
        </table>
  );
}

function SumbitMatch({players, update_players}) {
    // a form that lets you submit a match

    function handleSubmit(event) {
        event.preventDefault();
        const winner_id = event.target.winner.value;
        const loser_id = event.target.loser.value;
        if (winner_id === loser_id || winner_id === '---' || loser_id === '---') {
            return;
        }
        fetch(`${API_URL}/matches`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                result: [winner_id, loser_id],
                draw: false
            })
        }).then(response => response.json())
          .then(data => {
              update_players();

          })
          .catch(error => console.log(error));
    }

    return (
        <div className="submit_match">
            <h5>Submit Match</h5>
            <form onSubmit={handleSubmit}>
            <fieldset>
                <div className="form-group row">
                <div className="col-3">
                    <select className="form-control" id="winner" defaultValue="---">
                        <option value="---" disabled>Winner...</option>
                        {players.map(player => (
                            <option key={player.id} value={player.id}>{player.name}</option>
                        ))}
                    </select>
                </div>
                <div className="col-3">
                    <select className="form-control" id="loser" defaultValue="---">
                        <option value="---" disabled>Loser...</option>
                        {players.map(player => (
                            <option key={player.id} value={player.id}>{player.name}</option>
                        ))}
                    </select>
                </div>

                <div className="col-3">
                    <button type="submit" className="btn btn-primary mb-2">Submit</button>
                </div>
                </div>
            </fieldset>
            </form>
        </div>
    );

}

function App() {
    const [players, setPlayers] = useState([]);

    function update_players() {
        getPlayers().then(players => setPlayers(players));
    }

    useEffect(() => {
        if (!players.length) {
            update_players();
        }
    });

    return (
        <div className="App">
            <div className="container">
                <PlayerTable players={players}/>
                <div className="mt-6">
                <SumbitMatch players={players} update_players={update_players}/>
                </div>
            </div>
        </div>
    );
}

export default App;
