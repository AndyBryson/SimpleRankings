import React from "react";

function MatchRow({ match, delete: canDelete, onDelete }) {

    return (
        <tr>
            <td>{match.winner_name} <span className={'text-muted'}>({Math.round(match.winner_rating)})</span></td>
            <td>{match.loser_name} <span className={'text-muted'}>({Math.round(match.loser_rating)})</span></td>
            <td>{Math.round(match.probability * 100)}%</td>
            <td>{new Date(match.date).toLocaleString("en-GB")}</td>
            {canDelete && <td><button onClick={() => onDelete(match.id)}>Delete</button></td>}
        </tr>
    );
}

function MatchTable({ matches, delete: canDelete, onDelete }) {
    const matches_copy = [...matches];
    matches_copy.sort((a, b) => { return new Date(b.date) - new Date(a.date) });
    return (
        <table className="table table-hover">
            <thead>
                <tr>
                    <th>Winner</th>
                    <th>Loser</th>
                    <th>Probability</th>
                    <th>Date</th>
                    {canDelete && <th>Delete</th>}
                </tr>
            </thead>
            <tbody>
                {matches_copy.map(match => (
                    <MatchRow key={match.id} match={match} delete={canDelete} onDelete={onDelete} />
                ))}
            </tbody>
        </table>
    );
}

export default MatchTable;