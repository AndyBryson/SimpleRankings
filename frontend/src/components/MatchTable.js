import React from "react";

function MatchRow({match}) {

    return (
        <tr>
            <td>{match.winner_name} <span className={'text-muted'}>({Math.round(match.winner_rating)})</span></td>
            <td>{match.loser_name} <span className={'text-muted'}>({Math.round(match.loser_rating)})</span></td>
            <td>{Math.round(match.probability * 100)}%</td>
            <td>{new Date(match.date).toLocaleString("en-GB")}</td>
        </tr>
    );
}

function MatchTable({matches}) {
    matches.sort((a, b) => (a.date < b.date) ? 1 : -1);
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