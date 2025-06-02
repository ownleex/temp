import React, { useEffect, useState } from "react"
import { Modal, Button } from "react-bootstrap"
import { useAuth } from "../auth/context"
import axiosInstance from "../auth/instance"

function InviteMatch({ state, setState, setShow, setInfo }) {

	const [data, setData] = useState(null)
	const { user } = useAuth()

	const fonction = async () => {
		try {
			const playerData = await axiosInstance.get('users/api/player/')
			const blockData = await axiosInstance.get('/users/api/block/list/')
			
			const a = playerData.data
				.filter(player => !blockData.data.some(block => block.blocked == player.name || block.blocker == player.name) &&
					player.name != user.name)
			setData(a)
		}
		catch(error) {
			setState("")
			if (error && error.response && error.response.data && error.response.data.message) {
				setInfo(error.response.data.message)
				setShow(true)
			}
		}
	}

	const invite = async (id) => {
		try {
			await axiosInstance.post("pong/invitations/create/", {
				player_2_id: id,
				number_of_rounds: 1,
				max_score_per_round: 3,
				match_type: "Normal"
			})
			setState("wait")
		}
		catch(error) {
			setState("")
			if (error && error.response && error.response.data && error.response.data.message) {
				setInfo(error.response.data.message)
				setShow(true)
			}
		}
	}

	useEffect(() => {
		if (state == "invite")
			fonction()
	}, [state])

	return (
		<Modal show={state == "invite"}>
			<Modal.Header closeButton onClick={() => setState("")}>
				<Modal.Title>Who would you want to invite ?</Modal.Title>
			</Modal.Header>
			<Modal.Body className="d-flex flex-column align-items-center">
				<ul className="list-unstyled w-100 d-flex flex-column align-items-center gap-3">
					{data && data.length > 0 
						? (data.map((player, index) => (
						<li key={index} className="d-flex align-items-center justify-content-between bg-light rounded p-2 w-50 border-bottom">
							<div className="d-flex align-items-center gap-2">
								<img src={player.avatar} alt="Avatar" style={{ width: '40px', height: '40px', borderRadius: '50%' }}/>
								<span className="fw-bold">{player.name}</span>
							</div>
							<div className="d-flex gap-3">
								<Button type="button" onClick={() => invite(player.id)}>Invite</Button>
							</div>
						</li>)))
						: <li>No friends found</li>}
				</ul>
			</Modal.Body>
		</Modal>
	)
}

export default InviteMatch