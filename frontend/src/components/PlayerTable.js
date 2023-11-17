import React from "react";
import {useFetcher, Navigate} from "react-router-dom";
import {useNavigate} from "react-router-dom";

function PlayerRow({player, index}) {
    const navigate = useNavigate();

    function handleRowClick() {
        navigate(`/player/${player.id}`);
    }

    return (
        <tr onClick={handleRowClick} style={{cursor: 'pointer'}}>
            <td>{index}</td>
            <td>{player.name}</td>
            <td>{player.wins}</td>
            <td>{player.losses}</td>
            <td>{Math.round(player.rating)}</td>
        </tr>
    );
}

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
                <PlayerRow key={player.id} player={player} index={index+1} />
            ))}
            {/*Fill in the rest of the table with players who haven't played*/}
            {players.filter(player => player.wins + player.losses === 0).sort((a, b) => (a.name > b.name) ? 1 : -1).map(player => (
                <PlayerRow key={player.id} player={player} index={'-'}/>
            ))}
            </tbody>
        </table>
    );
}

export default PlayerTable;