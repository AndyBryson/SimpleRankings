const API_URL = process.env.REACT_APP_API_URL || 'http://192.168.63.30:8091';
const PLAYERS_ENDPOINT = `${API_URL}/players`;
const MATCHES_ENDPOINT = `${API_URL}/matches`;
const MATCHES_RESOLVED_ENDPOINT = `${API_URL}/matches/resolved`;

function addMatch(winner_id, loser_id, draw=false) {
    return fetch(MATCHES_ENDPOINT + "/resolved", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            result: [winner_id, loser_id],
            draw: draw,
        }),
    })
        .then((response) => response.json())
        .catch((error) => console.log(error));
}

function getMatches() {
    return fetch(MATCHES_RESOLVED_ENDPOINT)
        .then(response => response.json())
        .catch(error => { console.log(error); });
}

function getPlayers() {
    return fetch(PLAYERS_ENDPOINT)
        .then(response => response.json())
        .then(data => {
            data.sort((a, b) => (a.rating < b.rating) ? 1 : -1);
            return data;
        })
        .catch(error => { console.log(error); });
}

function getPlayer(playerId) {
    return fetch(`${API_URL}/players/${playerId}`)
        .then(response => response.json())
        .catch(error => { console.log(error); });
}

function getPlayersMatches(playerId) {
    return fetch(`${API_URL}/players/${playerId}/matches`)
        .then(response => response.json())
        .catch(error => { console.log(error); });
}

function addPlayer({update_players}) {
    const name = prompt("Enter player name");
    return fetch(PLAYERS_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: name
        })
    }).then(response => response.json())
        .then(data => {
            update_players();
        })
        .catch(error => console.log(error));
}

export { getPlayers, addPlayer, addMatch, getMatches, getPlayersMatches, getPlayer };