import React, { useEffect, useState, useRef } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../auth/context"
import { useGame } from "../websockets/game"
import { Modal, Button } from "react-bootstrap"
import { confetti } from "dom-confetti"
import { useNotification } from "../websockets/notification"

function WinnerModal({ winnerName, show, onClose, setState }) {

	const confettiRef = useRef(null)
	const navigate = useNavigate()

	useEffect(() => {
		if (show && confettiRef.current) {
			confetti(confettiRef.current, {
				elementCount: 100,
				angle: 90,
				spread: 90
			})
		}
	}, [show])

	const backToMenu = () => {
		onClose()
		setState("")
		navigate("/home")
	}

	return (
		<Modal show={show} onHide={backToMenu} centered>
			<Modal.Body className="text-center">
				<div ref={confettiRef} />
				<h2 className="fw-bold">🏆 {winnerName} wins!</h2>
				<p>Congratulations!</p>
				<Button variant="primary" onClick={() => backToMenu()}>Back to Menu</Button>
			</Modal.Body>
		</Modal>
	)
}

function PlayMatch({ setState }) {

	const { getSocket, closeSocket, messages } = useGame()
	const { setNotifMessages } = useNotification()
	const [paused, setPaused] = useState(false)
	const { user } = useAuth()
	const [end, setEnd] = useState(false)
	const closeEnd = () => setEnd(false)
	const [winner, setWinner] = useState("")
	const [timer, setTimer] = useState(60)
	const socket = getSocket()

	const declareWin = async () => {socket.send(JSON.stringify({ action: "declare_win" }))}

	useEffect(() => {
		if (!messages.length) return
		const lastMessage = messages[messages.length - 1]
		if (lastMessage.type == "game_resumed")
			setNotifMessages(lastMessage)
		if (lastMessage.type == "match_ended" || lastMessage.type == "forfeit_success") {
			closeSocket()
			if (lastMessage.type == "match_ended")
				setWinner(lastMessage.winner)
			else
				setWinner(user.name)
			setPaused(false)
			setEnd(true)
		}
		if (lastMessage.type == "game_paused" || (lastMessage.type == "player_count" && lastMessage.player_count == 1))
			setPaused(true)
		if (lastMessage.type == "forfeit_not_available")
			setTimer(lastMessage.remaining_seconds)
		if (lastMessage.type == "player_count" && lastMessage.player_count == 2) {
			setPaused(false)
			setTimer(60)
		}
	}, [messages])

	return (
		<>
		{paused ? 
		<div className="position-absolute top-0 d-flex flex-column justify-content-center align-items-center vh-100 w-100">
  			<i className="bi bi-pause-circle" style={{ fontSize: "20rem", color: "white" }} />
			<div className="fs-1 mb-5">
				<Button className="" onClick={() => declareWin()}>Declare win in {timer}s</Button>
			</div>
		</div> : <></> }
		<WinnerModal winnerName={ winner } show={ end } onClose={ closeEnd } setState={ setState }/>
		</>
	)
}

export default PlayMatch