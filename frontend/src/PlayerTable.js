import React from "react";

function PlayerTable({players}) {
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
            {players.map((player, index) => (
                <tr key={player.id}>
                    <td>{index + 1}</td>
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

export default PlayerTable;