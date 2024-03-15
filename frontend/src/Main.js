import React, { useEffect, useState } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';

import Home from './pages/Home';
import Matches from './pages/Matches';
import Profile from "./pages/Profile";
import { getPlayers, getMatches, deleteMatch } from "./rest_api";


const Main = () => {
    const [players, setPlayers] = useState([]);
    const [matches, setMatches] = useState([]);

    function update_players() {
        return getPlayers().then(players => setPlayers(players));
    }

    function update_matches() {
        return getMatches().then(matches => {
            setMatches(matches)
        });
    }

    function delete_match(id) {
        // pop up an are you sure?
        if (window.confirm('Are you sure you want to delete this match?') === true) {
            console.log('deleting match', id);
            deleteMatch(id).then(() => {
                update_matches();
            });
        }
    }

    useEffect(() => {
        update_players();
    }, []);

    const location = useLocation();
    const deleteMode = location.search === '?delete';


    return (
        <Routes>
            <Route exact path='/' element={<Home players={players} update_players={update_players} />} />
            <Route path='/matches' element={<Matches players={players} update_players={update_players} matches={matches}
                update_matches={update_matches} delete={deleteMode} onDelete={delete_match} />} />
            <Route path={'/player/:id'} element={<Profile />} />
        </Routes>
    );
};

export default Main;