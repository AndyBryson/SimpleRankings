import React from "react";
import { useNavigate } from "react-router-dom";

function PlayerRow({ player, index }) {
    const navigate = useNavigate();

    function handleRowClick() {
        navigate(`/player/${player.id}`);
    }

    return (
        <tr onClick={handleRowClick} style={{ cursor: 'pointer' }}>
            <td>{index}</td>
            <td>{player.name}</td>
            <td>{player.wins}</td>
            <td>{player.losses}</td>
            <td>{Math.round(player.rating)}</td>
        </tr>
    );
}

function PlayerTable({ players }) {
    const one_day = 60 * 24 * 60 * 60 * 1000;
    const inactiveCutoff = Date.now() - one_day * 60;
    const matchCutoff = 2;

    const activePlayers = players.filter(player => player.wins + player.losses >= matchCutoff && Date.parse(player.last_match_date) > inactiveCutoff).sort((a, b) => (a.rating < b.rating) ? 1 : -1);
    const inactivePlayers = players.filter(player => player.wins + player.losses >= matchCutoff && Date.parse(player.last_match_date) <= inactiveCutoff).sort((a, b) => (a.rating < b.rating) ? 1 : -1);
    const newPlayers = players.filter(player => player.wins + player.losses < matchCutoff).sort((a, b) => (a.rating < b.rating) ? 1 : -1);

    return (
        <table className="table table-hover">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Name</th>
                    <th>Wins</th>
                    <th>Losses</th>
                    <th>Rating</th>
                </tr>
            </thead>
            <tbody>
                {/*Show active players first*/}
                {activePlayers.map((player, index) => (
                    <PlayerRow key={player.id} player={player} index={index + 1} />
                ))}
                {/*Show inactive players next*/}
                {inactivePlayers.map((player, index) => (
                    <PlayerRow key={player.id} player={player} index={index + 1} />
                ))}
                {/*Fill in the rest of the table with players who haven't played enough*/}
                {newPlayers.map((player, index) => (
                    <PlayerRow key={player.id} player={player} index={'-'} />
                ))}
            </tbody>
        </table>
    );
}

export default PlayerTable;