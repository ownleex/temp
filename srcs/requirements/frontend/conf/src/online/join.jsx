import React, { useEffect, useState } from "react"
import { Modal, Button } from "react-bootstrap"
import { useAuth } from "../auth/context"
import axiosInstance from "../auth/instance"
import { useNotification } from "../websockets/notification"
import { useGame } from "../websockets/game"

function JoinMatch({ state, setState, setShow, setInfo }) {

	const [data, setData] = useState(null)
	const { NotifMessages, setNotifMessages } = useNotification()
	const { setUrl } = useGame()
	const { user } = useAuth()

	const fonction = async () => {
		try {
			const playerData = await axiosInstance.get('/users/api/player/')
			const invitations = await axiosInstance.get("pong/invitations/")
			const getAvatar = (name) => {
				const Avatar = playerData.data.find(player => player.name === name)
				if (Avatar) return Avatar.avatar
				return null
			}
			const a = invitations.data
				.filter(player => player.to_player.id == user.id)
				.map(player => ({name: player.from_player.name, id: player.id, avatar: getAvatar(player.from_player.name)}))
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

	const accept = async (id) => {
		try {
			await axiosInstance.put(`pong/invitations/${id}/accept/`)
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

	const decline = async (id) => {
		try {
			await axiosInstance.put(`pong/invitations/${id}/decline/`)
			setState("")
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
		if (NotifMessages.type == "match_created") {
			if (NotifMessages.player_1.name == user.name) setType("paddle_l")
			else if (NotifMessages.player_2.name == user.name) setType("paddle_r")
			setUrl(NotifMessages.ws_url)
			setNotifMessages([])
			setState("play")
		}
	}, [NotifMessages])

	useEffect(() => {
		fonction()
	}, [state])

	return (
		<Modal show={state == "join"}>
			<Modal.Header closeButton onClick={() => setState("")}>
				<Modal.Title>Who would you want to join ?</Modal.Title>
			</Modal.Header>
			<Modal.Body className="d-flex flex-column align-items-center">
				<ul className="list-unstyled w-100 d-flex flex-column align-items-center gap-3">
					{data && data.length > 0 
						? (data.map((player, index) => (
						<li key={index} className="bg-light rounded p-2 w-75 border-bottom">
							<div className="d-flex justify-content-between align-items-center">
								<div className="d-flex align-items-center gap-3">
									<img src={player.avatar} alt="Avatar" style={{ width: '40px', height: '40px', borderRadius: '50%' }} />
									<span className="fw-bold">{player.name}</span>
								</div>
								<div className="d-flex gap-2">
									<Button variant="success" onClick={() => accept(player.id)}>Accept</Button>
									<Button variant="danger" onClick={() => decline(player.id)}>Decline</Button>
								</div>
							</div>
						</li>)))
						: <li>No friends found</li>}
				</ul>
			</Modal.Body>
		</Modal>
	)
}

export default JoinMatch