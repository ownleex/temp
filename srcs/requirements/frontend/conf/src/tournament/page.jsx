import React, { useState, useEffect } from "react"
import { Button } from "react-bootstrap"
import Header from "../global/header"
import BGprivate from "../test/private/page.jsx"
import JoinMatch from "./join.jsx"
import WaitMatch from "./wait.jsx"
import PlayMatch from "./play.jsx"
import { useNotification } from "../websockets/notification.jsx"
import axiosInstance from "../auth/instance.jsx"
import ErrorModal from "../global/error-modal.jsx"
import { useGame } from "../websockets/game.jsx"

function Tournament({ user }) {

	const [state, setState] = useState("")
	const [type, setType] = useState("")
	const { setNotifMessages, NotifMessages } = useNotification()
	const { setUrl } = useGame()

	const [show, setShow] = useState(false)
	const hideModal = () => setShow(false)
	const [info, setInfo] = useState("")

	const fonction = async () => {
		try {
			const tournamentData = await axiosInstance.get("/pong/tournament/list/")
			const matchData = await axiosInstance.get(`/pong/matches/?player_id=${user.id}`)
			const idData = await axiosInstance.get("/pong/tournament/get-id/")
			const a = tournamentData.data
				.find(match => match.status == "Ouvert" &&
				(match.player_1 == user.id || match.player_2 == user.id ||
				match.player_3 == user.id || match.player_4 == user.id))
			if (a) {
				setState("wait")
				setNotifMessages({type: "tournament_created"})
			}
			const b = matchData.data
				.find(match => match.status == "En cours" && match.type == "Tournois")
			if (b) {
				if (b.player_1.name == user.name) setType("paddle_l")
				else if (b.player_2.name == user.name) setType("paddle_r")
				setUrl(b.url.ws_url)
				setState("play")
			}
			if (idData && idData.data.finalist1 != null && idData.data.finalist2 != null &&
				(idData.data.finalist1 == user.name || idData.data.finalist2 == user.name && !b)) {
				await axiosInstance.put(`/pong/tournament/${idData.data.tournament_id}/start-final/`)
				await axiosInstance.post("/live_chat/general/send/", {content: `#Time for final : ${idData.data.finalist1} vs ${idData.data.finalist2}`})
			}
		}
		catch {}
	}

	const create = async () => {
		try {
			await axiosInstance.post("pong/tournament/create/", {
				name: `Tournament of ${user.name}`,
				max_score_per_round: 3,
				number_of_rounds: 1,
			})
			setNotifMessages({type: "tournament_created"})
			setState("wait")
		}
		catch(error) {
			if (error && error.response && error.response.data && error.response.data.message) {
				setInfo(error.response.data.message)
				setShow(true)
			}
		}
	}

	useEffect(() => {
		if (NotifMessages.type == "match_created" && state == "") {
			if (NotifMessages.player_1 == user.name) setType("paddle_l")
			else if (NotifMessages.player_2 == user.name) setType("paddle_r")
			setUrl(NotifMessages.ws_url)
			setNotifMessages([])
			setState("play")
		}
	}, [NotifMessages])

	useEffect(() => {
		if (state == "")
			fonction()
	}, [state])

	return (
		<>
			<Header user={ user } state={ state } setState={ setState }/>
			<main>
				<BGprivate state={ state } type={ type }/>
				{state == "" || state == "join" ?
				<div className="position-absolute top-0 d-flex justify-content-center align-items-center vh-100 w-100">
					<div className="rounded border border-black border-2 px-3 px-lg-5 pt-2 pt-lg-4 pb-3 pb-lg-4"
						style={{background: "rgba(0, 0, 0, 0.7)"}}>
						<h1 className="text-white text-center mb-4">Tournament</h1>
						<div className="d-flex flex-column gap-3">
							<Button type="button" className="btn btn-secondary rounded fw-bolder" onClick={() => create()}>Create</Button>
							<Button type="button" className="btn btn-secondary rounded fw-bolder" onClick={() => setState("join")}>Join</Button>
						</div>
					</div>
				</div> : <></>}
				<JoinMatch state={ state } setState={ setState } setShow={ setShow } setInfo={ setInfo }/>
				{state == "wait" ?
				<WaitMatch setState={ setState } setType={ setType }/> : <></>}
				{state == "play" ?
				<PlayMatch setState={ setState } setType={ setType }/> : <></>}
				<ErrorModal show={ show } hideModal={ hideModal } contextId={ 5 } info={ info } />
			</main>
		</>
	)
}

export default Tournament