import React, { useEffect, useState } from "react"
import { Modal, Button, Spinner } from "react-bootstrap"
import axiosInstance from "../auth/instance"

function JoinMatch({ state, setState, setShow, setInfo }) {

	const [data, setData] = useState(null)
	const [full, setFull] = useState(false)

	const fonction = async () => {
		try {
			const playerData = await axiosInstance.get('/users/api/player/')
			const tournamentData = await axiosInstance.get("/pong/tournament/list/")
			const getAvatar = (id) => {
				if (!id || id == null) return null
				const Avatar = playerData.data.find(player => player.id === id)
				return Avatar.avatar
			}
			const getPlayers = (p1, p2, p3, p4) => {
				let players = 0
				if (p1) players++
				if (p2)	players++
				if (p3) players++
				if (p4) players++
				return players
			}
			const a = tournamentData.data
				.map(tourn => ({
					name: tourn.name,
					id: tourn.id,
					p1: getAvatar(tourn.player_1),
					p2: getAvatar(tourn.player_2),
					p3: getAvatar(tourn.player_3),
					p4: getAvatar(tourn.player_4),
					players: getPlayers(tourn.player_1, tourn.player_2, tourn.player_3, tourn.player_4)}))
			setData(a)
		}
		catch(error) {
			fonction()
			if (error && error.response && error.response.data && error.response.data.message) {
				setShow(true)
				setInfo(error.response.data.message)
			}
		}
	}

	const join = async (id) => {
		if (full == true) return
		try {
			await axiosInstance.put(`pong/tournament/${id}/join/`)
			setState("wait")
		}
		catch(error) {
			fonction()
			if (error && error.response && error.response.data && error.response.data.message) {
				setShow(true)
				setInfo(error.response.data.message)
			}
		}
	}

	useEffect(() => {
		if (state == "join")
			fonction()
	}, [state])

	useEffect(() => {
		if (data && data.players == 4)
			setFull(true)
		else
			setFull(false)
	}, [data])

	return (
		<Modal show={state == "join"}>
			<Modal.Header closeButton onClick={() => setState("")}>
				<Modal.Title>Who would you want to join ?</Modal.Title>
			</Modal.Header>
			<Modal.Body className="d-flex flex-column align-items-center">
				<ul className="list-unstyled w-100 d-flex flex-column align-items-center gap-3">
					{data && data.length > 0 
						? (data.map((tourn, index) => (
						<li key={index} className="bg-light rounded p-2 w-75 border-bottom">
							<div className="d-flex justify-content-between align-items-center">
								<div className="d-flex align-items-center gap-3">
									<span className="fw-bold">{tourn.name}</span>
									{tourn.p1 ?
									<img src={tourn.p1} alt="Avatar" style={{ width: '40px', height: '40px', borderRadius: '50%' }} /> :
									<Spinner animation="border" style={{ width: '1rem', height: '1rem' }} className="mb-2"/>}
									{tourn.p2 ?
									<img src={tourn.p2} alt="Avatar" style={{ width: '40px', height: '40px', borderRadius: '50%' }} /> :
									<Spinner animation="border" style={{ width: '1rem', height: '1rem' }} className="mb-2"/>}
									{tourn.p3 ?
									<img src={tourn.p3} alt="Avatar" style={{ width: '40px', height: '40px', borderRadius: '50%' }} /> :
									<Spinner animation="border" style={{ width: '1rem', height: '1rem' }} className="mb-2"/>}
									{tourn.p4 ?
									<img src={tourn.p4} alt="Avatar" style={{ width: '40px', height: '40px', borderRadius: '50%' }} /> :
									<Spinner animation="border" style={{ width: '1rem', height: '1rem' }} className="mb-2"/>}
								</div>
								<div className="ms-3">
									<Button variant={!full ? "success" : "danger"} onClick={() => join(tourn.id)}>Join</Button>
								</div>
							</div>
						</li>)))
						: <li>No tournament found</li>}
				</ul>
			</Modal.Body>
		</Modal>
	)
}

export default JoinMatch