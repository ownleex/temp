import React, { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Button } from "react-bootstrap"
import SettingsModal from "./settings-modal.jsx"
import FriendModal from "../friend/modal.jsx"
import ChatModal from "../chat/modal.jsx"
import QuitModal from "../global/quit-modal.jsx"
import { useGame } from "../websockets/game.jsx"

function Header({ user, state, setState }) {

	const navigate = useNavigate()
	const [settings, setSettings] = useState(false)
	const [friend, setFriend] = useState(false)
	const [chat, setChat] = useState(false)
	const [quit, setQuit] = useState(false)
	const { closeSocket } = useGame()

	if (!user) return (<></>)

	const goTo = (string) => {
		if (state && state == "play")
			closeSocket()
		navigate(string)
	}

	const setTo = (string) => {
		if (state && state == "play") {
			closeSocket()
			navigate("/home")
		}
		if (string == "settings")
			setSettings(true)
		else if (string == "friend")
			setFriend(true)
		else if (string == "chat")
			setChat(true)
		else if (string == "quit")
			setQuit(true)
	}

	return (
		<>
			<header>
				<nav className="navbar bg-dark opacity-75 fixed-top p-2">
					<div className="container-fluid p-0 m-0">
						<Button className="rounded-0 btn btn-dark fw-bolder" onClick={() => setTo("settings")}>
							<i className="bi bi-gear-fill" style={{fontSize: "40px"}}/>
						</Button>
						<Button className="rounded-0 btn btn-dark fw-bolder" onClick={() => goTo("/home")}>
							<i className="bi bi-house-fill" style={{fontSize: "40px"}}/>
						</Button>
						<Button className="rounded-0 btn btn-dark fw-bolder" onClick={() => goTo(`/profile/${user.name}`)}>
							<i className="bi bi-person-lines-fill" style={{fontSize: "40px"}}/>
						</Button>
						<h1 className="navbar-brand text-bg-dark fw-bolder fs-1 m-0 p-0 user-select-none"
							style={{textShadow: "3px 3px 5px rgba(0, 0, 0, 0.7)"}}>Pong.</h1>
						<Button className="rounded-0 btn btn-dark fw-bolder" onClick={() => setTo("friend")}>
							<i className="bi bi-people-fill" style={{fontSize: "40px"}}/>
						</Button>
						<Button className="rounded-0 btn btn-dark fw-bolder" onClick={() => setTo("chat")}>
							<i className="bi bi-chat-dots-fill" style={{fontSize: "40px"}}/>
						</Button>
						<Button className="rounded-0 btn btn-dark fw-bolder" onClick={() => setTo("quit")}>
							<i className="bi bi-power" style={{fontSize: "40px"}}/>
						</Button>
					</div>
				</nav>
			</header>
			<SettingsModal settings={ settings } setSettings={ setSettings }/>
			<FriendModal friend={ friend } setFriend={ setFriend }/>
			<ChatModal chat={ chat } setChat={ setChat }/>
			<QuitModal quit={ quit } setQuit={ setQuit }/>
		</>
	)
}

export default Header