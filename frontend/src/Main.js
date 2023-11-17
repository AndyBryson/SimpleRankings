import React, {useEffect, useState} from 'react';
import { Routes, Route } from 'react-router-dom';

import Home from './pages/Home';
import Matches from './pages/Matches';
import {getPlayers} from "./rest_api";


const Main = () => {
    const [players, setPlayers] = useState([]);

    function update_players() {
        return getPlayers().then(players => setPlayers(players));
    }

    useEffect(() => {
        if (players.length < 1) {
            update_players();
        }
    });


    return (
        <Routes>
            <Route exact path='/' element={<Home players={players} update_players={update_players} />} />
            <Route exact path='/matches' element={<Matches players={players} />} />
        </Routes>
    );
};

export default Main;