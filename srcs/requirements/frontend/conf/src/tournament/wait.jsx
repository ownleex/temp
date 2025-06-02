import React, { useEffect, useState } from "react"
import { Button, Spinner } from "react-bootstrap"
import { useNotification } from "../websockets/notification"
import { useGame } from "../websockets/game"
import axiosInstance from "../auth/instance"
import { useAuth } from "../auth/context"

function WaitMatch({ setState, setType, setShow, setInfo }) {

	const { NotifMessages, setNotifMessages } = useNotification()
	const { setUrl } = useGame()
	const [ready, setReady] = useState(false)
	const [data, setData] = useState({})
	const { user } = useAuth()

	const fonction = async () => {
		try {
			const playerData = await axiosInstance.get('/users/api/player/')
			const tournamentData = await axiosInstance.get("/pong/tournament/list/")
			const getName = (id) => {
				if (!id || id == null) return "..."
				const Name = playerData.data.find(player => player.id === id)
				return Name.name
			}
			const getAvatar = (id) => {
				if (!id || id == null) return "null"
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
				.find(tourn => tourn.status == "Ouvert" &&
					(tourn.player_1 == user.id || tourn.player_2 == user.id ||
					tourn.player_3 == user.id || tourn.player_4 == user.id))
			if (a == undefined || a.length == 0) return
			setData({
				name: a.name,
				id: a.id,
				p1: {name: getName(a.player_1), avatar: getAvatar(a.player_1)},
				p2: {name: getName(a.player_2), avatar: getAvatar(a.player_2)},
				p3: {name: getName(a.player_3), avatar: getAvatar(a.player_3)},
				p4: {name: getName(a.player_4), avatar: getAvatar(a.player_4)},
				players: getPlayers(a.player_1, a.player_2, a.player_3, a.player_4)})
		}
		catch(error) {
			if (error && error.response && error.response.data && error.response.data.message) {
				setShow(true)
				setInfo(error.response.data.message)
			}
		}
	}

	const startGame = async (message) => {
		try {
			if (data.p1.name == user.name) {
				const idData = await axiosInstance.get("/pong/tournament/get-id/")
				let a
				if (idData.data.tournament_id) {
					a = await axiosInstance.get(`/pong/tournaments/${idData.data.tournament_id}/struct/`)
					await axiosInstance.post("/live_chat/general/send/", {content: `#A tournament has started ! Semi-final-1 : ${a.data.matches[0].player_1} vs ${a.data.matches[0].player_2}, Semi-final-2: ${a.data.matches[1].player_1} vs ${a.data.matches[1].player_2}`})
				}
			}
		}
		catch(error) {
			if (error && error.response && error.response.data && error.response.data.message) {
				setShow(true)
				setInfo(error.response.data.message)
			}
		} 
		finally {
			if (message.player_1 == user.name) setType("paddle_l")
			else if (message.player_2 == user.name) setType("paddle_r")
			setUrl(message.ws_url)
			setNotifMessages([])
			setState("play")
		}
	}

	const play = async (id) => {
		if (ready == false) return
		try {const response = await axiosInstance.put(`/pong/tournament/${id}/start/`)}
		catch(error) {
			if (error && error.response && error.response.data && error.response.data.message) {
				setShow(true)
				setInfo(error.response.data.message)
			}
		}
	}


	const cancel = async (id) => {
		try {await axiosInstance.delete(`/pong/tournament/${id}/cancel/`)}
		catch(error) {
			if (error && error.response && error.response.data && error.response.data.message) {
				setShow(true)
				setInfo(error.response.data.message)
			}
		}
	}

	const leave = async (id) => {
		try {
			await axiosInstance.put(`/pong/tournament/${id}/leave/`)
			setType("")
			setState("")
		}
		catch(error) {
			if (error && error.response && error.response.data && error.response.data.message) {
				setShow(true)
				setInfo(error.response.data.message)
			}
		}
	}

	useEffect(() => {
		if (NotifMessages.type == "tournament_created" || NotifMessages.type == "player_joined" || NotifMessages.type == "player_leave")
			fonction()
		if (NotifMessages.type == "tournament_cancelled") {
			setState("")
			setType("")
		}
		if (NotifMessages.type == "match_created" && NotifMessages.type != "tournament_semi_final")
			startGame(NotifMessages)
	}, [NotifMessages])

	useEffect(() => {
		if (data && data.players == 4 && data.p1.name == user.name)
			setReady(true)
		else
			setReady(false)
	}, [data])

	return (
		<div className="position-absolute top-0 d-flex justify-content-center align-items-center vh-100 w-100">
			<div className="rounded border border-black border-2 px-3 px-lg-5 pt-2 pt-lg-4 pb-3 pb-lg-4"
				style={{background: "rgba(0, 0, 0, 0.7)"}}>
				<div className="d-flex flex-column align-items-center">
				{data && data.p1 && data.p2 && data.p3 && data.p4 ?
				<>
					<span className="text-white mb-3">{data.name}</span>
					{data.p1.avatar != "null" ?
					<img src={data.p1.avatar} className="mb-1" style={{ width: '80px', height: '80px', borderRadius: '50%' }}/> :
					<Spinner animation="border" style={{ width: '3rem', height: '3rem' }} className="mb-2"/>}
					<div className="text-white mb-3">{data.p1.name}</div>
					{data.p2.avatar != "null" ?
					<img src={data.p2.avatar} className="mb-1" style={{ width: '80px', height: '80px', borderRadius: '50%' }}/> :
					<Spinner animation="border" style={{ width: '3rem', height: '3rem' }} className="mb-2"/>}
					<div className="text-white mb-3">{data.p2.name}</div>
					{data.p3.avatar != "null" ?
					<img src={data.p3.avatar} className="mb-1" style={{ width: '80px', height: '80px', borderRadius: '50%' }}/> :
					<Spinner animation="border" style={{ width: '3rem', height: '3rem' }} className="mb-2"/>}
					<div className="text-white mb-3">{data.p3.name}</div>
					{data.p4.avatar != "null" ?
					<img src={data.p4.avatar} className="mb-1" style={{ width: '80px', height: '80px', borderRadius: '50%' }}/> :
					<Spinner animation="border" style={{ width: '3rem', height: '3rem' }} className="mb-2"/>}
					<div className="text-white mb-3">{data.p4.name}</div>
					<Button type="button" variant={ready ? "success" : "danger" } className="btn btn-secondary rounded fw-bolder mt-3" onClick={() => play(data.id)}>Play</Button>
					{data.p1.name == user.name ?
					<Button type="button" className="btn btn-secondary rounded fw-bolder mt-3" onClick={() => cancel(data.id)}>Cancel</Button> :
					<Button type="button" className="btn btn-secondary rounded fw-bolder mt-3" onClick={() => leave(data.id)}>Leave</Button>}
				</>	
				: <></>}
				</div>
			</div>
		</div>
	)
}

export default WaitMatch