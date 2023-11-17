import React, { useState } from 'react';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import { addMatch } from '../rest_api';

function SubmitMatch({ players, update_players }) {
    const [showModal, setShowModal] = useState(false);
    const hiddenSubmitRef = React.createRef();

    const players_by_name = players.sort((a, b) => (a.name > b.name) ? 1 : -1);

    function handleSubmit(event) {
        event.preventDefault();
        const winner_id = event.target.winner.value;
        const loser_id = event.target.loser.value;
        if (winner_id === loser_id || winner_id === '---' || loser_id === '---') {
            return;
        }
        addMatch(winner_id, loser_id)
            .then(() => {
                update_players();
                setShowModal(false); // Close the modal after submitting

            })
    }

    function handleHiddenSubmitClick() {
        hiddenSubmitRef.current.click();
    }

    return (
        <>
            <Button variant="primary" onClick={() => setShowModal(true)}>
                Submit Match
            </Button>

            <Modal show={showModal} onHide={() => setShowModal(false)}>
                <Modal.Header closeButton>
                    <Modal.Title>Submit Match</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <form onSubmit={handleSubmit}>
                        <div className="form-group row">
                            <div className="col">
                                <select className="form-control" id="winner" defaultValue="---">
                                    <option value="---" disabled>
                                        Winner...
                                    </option>
                                    {players_by_name.map((player) => (
                                        <option key={player.id} value={player.id}>
                                            {player.name}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div className="col">
                                <select className="form-control" id="loser" defaultValue="---">
                                    <option value="---" disabled>
                                        Loser...
                                    </option>
                                    {players_by_name.map((player) => (
                                        <option key={player.id} value={player.id}>
                                            {player.name}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>
                        <button type="submit" style={{ display: 'none' }} ref={hiddenSubmitRef} />
                    </form>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={() => setShowModal(false)}>
                        Close
                    </Button>
                    <Button variant="primary" onClick={handleHiddenSubmitClick}>
                        Submit
                    </Button>
                </Modal.Footer>
            </Modal>
        </>
    );
}

export default SubmitMatch;