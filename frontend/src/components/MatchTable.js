import React from "react";


function MatchRow({match}) {
    return (
        <tr>
            <td>{match.winner_name} ({Math.round(match.winner_rating)})</td>
            <td>{match.loser_name} ({Math.round(match.loser_rating)})</td>
            <td>{match.probability.toFixed(2)}</td>
            <td>{match.date}</td>
        </tr>
    );
}

function MatchTable({matches}) {
    return (
        <table className="table table-hover">
            <thead>
            <tr>
                <th>Winner</th>
                <th>Loser</th>
                <th>Probability</th>
                <th>Date</th>
            </tr>
            </thead>
            <tbody>
            {matches.map(match => (
                <MatchRow key={match.id} match={match} />
            ))}
            </tbody>
        </table>
    );
}

export default MatchTable;