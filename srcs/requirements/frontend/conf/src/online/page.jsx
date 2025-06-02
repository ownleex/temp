import React, { useState, useEffect } from "react"
import { Button } from "react-bootstrap"
import Header from "../global/header"
import BGprivate from "../test/private/page.jsx"
import InviteMatch from "./invite.jsx"
import JoinMatch from "./join.jsx"
import WaitMatch from "./wait.jsx"
import PlayMatch from "./play.jsx"
import axiosInstance from "../auth/instance.jsx"
import { useGame } from "../websockets/game.jsx"
import ErrorModal from "../global/error-modal.jsx"

function Online({ user }) {

	const [state, setState] = useState("")
	const [type, setType] = useState("")
	const { setUrl } = useGame()

	const [show, setShow] = useState(false)
	const hideModal = () => setShow(false)
	const [info, setInfo] = useState("")

	const fonction = async () => {
		try {
			const matchData = await axiosInstance.get(`/pong/matches/?player_id=${user.id}`)
			const inviteData = await axiosInstance.get("/pong/invitations/")
			const a = matchData.data.find(match => (match.player_1.name == user.name || match.player_2.name == user.name) &&
				match.status == "En cours" && match.tournament == null)
			if (a) {
				if (a.player_1 != undefined && a.player_2 != undefined &&
					a.player_1.name != undefined && a.player_2.name != undefined) {		
					if (a.player_1.name == user.name) setType("paddle_l")
					else if (a.player_2.name == user.name) setType("paddle_r")
					setUrl(a.url.ws_url)
					setState("play")
				}
			}
			const b = inviteData.data.find(invite => invite.status == "En attente" && invite.from_player.name == user.name)
			if (b) {
				setType("paddle_l")
				setState("wait")
			}
		}
		catch(error) {
			if (error && error.response && error.response.data && error.response.data.message) {
				setInfo(error.response.data.message)
				setShow(true)
			}
		}
	}

	useEffect(() => {
		if (state != "play")
			fonction()
	}, [state])

	return (
		<>
			<Header user={ user } state={ state } setState={ setState }/>
			<main>
				<BGprivate state={ state } type={ type }/>
				{state == "" || state == "invite" || state == "join" ?
				<div className="position-absolute top-0 d-flex justify-content-center align-items-center vh-100 w-100">
					<div className="rounded border border-black border-2 px-3 px-lg-5 pt-2 pt-lg-4 pb-3 pb-lg-4"
						style={{background: "rgba(0, 0, 0, 0.7)"}}>
						<h1 className="text-white text-center mb-4">Online</h1>
						<div className="d-flex flex-column gap-3">
							<Button type="button" className="btn btn-secondary rounded fw-bolder" onClick={() => setState("invite")}>Invite</Button>
							<Button type="button" className="btn btn-secondary rounded fw-bolder" onClick={() => setState("join")}>Join</Button>
						</div>
					</div>
				</div> : <></>}
				<InviteMatch state={ state } setState={ setState } setShow={ setShow } setInfo={ setInfo }/>
				<JoinMatch state={ state } setState={ setState } setShow={ setShow } setInfo={ setInfo }/>
				{state == "wait" ?
				<WaitMatch setState={ setState } setShow={ setShow } setInfo={ setInfo }/> : <></>}
				{state == "play" ?
				<PlayMatch setState={ setState }/> : <></>}
				<ErrorModal show={ show } hideModal={ hideModal } contextId={ 5 } info={ info } />
			</main>
		</>
	)
}

export default Online