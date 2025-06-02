import React, { useEffect, useState } from "react"
import { Button, Spinner } from "react-bootstrap"
import { useAuth } from "../auth/context"
import { useNotification } from "../websockets/notification"
import { useGame } from "../websockets/game"
import axiosInstance from "../auth/instance"

function WaitMatch({ setState, setShow, setInfo }) {

	const { user } = useAuth()
	const { NotifMessages, setNotifMessages } = useNotification()
	const { setUrl } = useGame()

	const cancel = async () => {
		try {
			const invitations = await axiosInstance.get("/pong/invitations/")
			const a = invitations.data.find(invite => invite.from_player.name == user.name)
			await axiosInstance.put(`/pong/invitations/${a.id}/cancel/`)
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
		if (NotifMessages.type == "invitation_declined") {
			setState("")
			setNotifMessages([])
		}
	}, [NotifMessages])

	return (
		<div className="position-absolute top-0 d-flex justify-content-center align-items-center vh-100 w-100">
			<div className="rounded border border-black border-2 px-3 px-lg-5 pt-2 pt-lg-4 pb-3 pb-lg-4"
				style={{background: "rgba(0, 0, 0, 0.7)"}}>
				<div className="d-flex flex-column align-items-center">
					<img src={user.avatar} className="mb-1" style={{ width: '80px', height: '80px', borderRadius: '50%' }}/>
					<div className="text-white mb-3">{user.name}</div>
					<Spinner animation="border" style={{ width: '3rem', height: '3rem' }} className="mb-2"/>
					<div className="text-white mb-3">...</div>
					<Button type="button" className="btn btn-secondary rounded fw-bolder mt-3" onClick={() => cancel()}>Cancel</Button>				
				</div>
			</div>
		</div>
	)
}

export default WaitMatch