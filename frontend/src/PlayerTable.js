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
            {/*Split players into 2 arrays. One for player who have played, one for those who haven't*/}
            {players.filter(player => player.wins + player.losses > 0).sort((a, b) => (a.rating < b.rating) ? 1 : -1).map((player, index) => (
                <tr key={player.id}>
                    <td>{index + 1}</td>
                    <td>{player.name}</td>
                    <td>{player.wins}</td>
                    <td>{player.losses}</td>
                    <td>{Math.round(player.rating)}</td>
                </tr>
            ))}
            {/*Fill in the rest of the table with players who haven't played*/}
            {players.filter(player => player.wins + player.losses === 0).sort((a, b) => (a.name > b.name) ? 1 : -1).map(player => (
                <tr key={player.id}>
                    <td>-</td>
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