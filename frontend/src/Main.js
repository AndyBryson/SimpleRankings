import React, {useEffect, useState} from 'react';
import { Routes, Route } from 'react-router-dom';

import Home from './pages/Home';
import Matches from './pages/Matches';
import Profile from "./pages/Profile";
import {getPlayers, getMatches} from "./rest_api";


const Main = () => {
    const [players, setPlayers] = useState([]);
    const [matches, setMatches] = useState([]);

    function update_players() {
        return getPlayers().then(players => setPlayers(players));
    }

    function update_matches() {
        return getMatches().then(matches => setMatches(matches));
    }

    useEffect(() => {
        update_players();
    }, []);


    return (
        <Routes>
            <Route exact path='/' element={<Home players={players} update_players={update_players} />} />
            <Route path='/matches' element={<Matches players={players} update_players={update_players} matches={matches} update_matches={update_matches}/>} />
            <Route path={'/player/:id'} element={<Profile playerId={1} />} />
        </Routes>
    );
};

export default Main;