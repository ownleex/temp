import React, { useEffect, useState, useRef } from "react"
import { useNavigate } from "react-router-dom"
import { Modal } from "react-bootstrap"
import { useChat } from "../websockets/chat"
import { useAuth } from "../auth/context"
import { usePrivateChat } from "../websockets/privateChat.jsx"
import { updateTime, updateSender, updateContent} from "./string.js"
import axiosInstance from "../auth/instance.jsx"
import ErrorModal from "../global/error-modal.jsx"

function ChatModal({ chat, setChat }) {

	const navigate = useNavigate()
	const handleClose = () => setChat(false)
	const [chats, setChats] = useState([])
	const [message, setMessage] = useState("")
	const { user } = useAuth()
	const { messages } = useChat()
	const { privMessages } = usePrivateChat()
	const bottomRefs = useRef([])

	const [show, setShow] = useState(false)
	const hideModal = () => setShow(false)
	const [info, setInfo] = useState("")

	const fonction = async () => {
		try {
			const a = await axiosInstance.get("/live_chat/general/messages/")
			const b = await axiosInstance.get("/live_chat/private/list/")
			const c = await axiosInstance.get('/users/api/player/')
			const d = await axiosInstance.get('/users/api/block/list/')
			const e = c.data
				.filter(player => !d.data.some(block => block.blocked == player.name || block.blocker == player.name) &&
					player.name != user.name)

			const temp = []

			temp.push({ lower : "general", realName: "", groupNAME: "General", groupID: 0, id: 0, active: true, data: a.data.data })

			for (let i = 0; i < e.length; i++) {
				const realName = e[i].name
				const groupNAME = updateSender(e[i].name)
				const groupID = e[i].id
				const lower = e[i].name.toLowerCase()
				const id = i + 1
				const data = b.data.data
					.filter(b => b.sender_name == e[i].name || b.receiver_name == e[i].name)
				temp.push({lower: lower, realName: realName, groupNAME: groupNAME, groupID: groupID, id: id, active: false, data: data ? data : []})
			}
			setChats(temp)
		}
		catch(error) {
			if (error && error.response && error.response.data && error.response.data.message)
			if (error && error.response && error.response.data && error.response.data.message) {
				setInfo(error.response.data.message)
				setShow(true)
			}
		}
	}

	const invite = async (id, name) => {
		try {
			const matchData = await axiosInstance.get(`/pong/matches/?player_id=${user.id}`)
			if (matchData.data.find(match => match.status == "En cours")) return
			const inviteData = await axiosInstance.get("/pong/invitations/")
			if (inviteData.data.find(invite => invite.status == "En attente" && invite.from_player.name == user.name)) return
			await axiosInstance.post("pong/invitations/create/", {
				player_2_id: id,
				number_of_rounds: 1,
				max_score_per_round: 3,
				match_type: "Normal"
			})
			await axiosInstance.post(`/live_chat/private/send/${id}/`, {content: `#${user.name} invited ${name} in a game.`})
		}
		catch(error) {
			if (error && error.response && error.response.data && error.response.data.message) {
				setInfo(error.response.data.message)
				setShow(true)
			}
		}
	}

	const send = async (id) => {
		if (!message) return
		try {
			if (id)
				await axiosInstance.post(`/live_chat/private/send/${id}/`, {content: message})
			else
				await axiosInstance.post("/live_chat/general/send/", {content: message})}
		catch(error) {
			if (error && error.response && error.response.data && error.response.data.message) {
				setInfo(error.response.data.message)
				setShow(true)
			}
		}
		finally {setMessage("")}
	}

	const navigateTo = (string) => {
		navigate(string)
		handleClose()
	}

	useEffect(() => {
		if (chat == true)
			fonction()
	}, [chat, messages, privMessages])

	useEffect(() => {
		const activeChat = chats.find(c => c.active)
		if (activeChat && bottomRefs.current[activeChat.id]?.current) {
			setTimeout(() => {
				bottomRefs.current[activeChat.id].current.scrollIntoView({ behavior: "smooth" })
			}, 50)
		}
	}, [chats])

	const renderChatTab = (lower, realName, active, groupID, groupNAME, id, data) => {
		
		if (!bottomRefs.current[id])
			bottomRefs.current[id] = React.createRef()
		return (
			<div id={`v-pills-${lower}`} role="tabpanel" style={{ flex: 1 }} aria-labelledby={`v-pills-${lower}-tab`} tabIndex="0"
				className={`tab-pane fade ${active ? "show active" : ""}`}>
				<div style={{ height: '70vh', border: '1px solid #ccc', borderRadius: '8px' }}
					className="d-flex flex-column bg-white p-3 w-100">
					<div style={{ border: '1px solid #ddd', borderRadius: '4px', padding: '10px', backgroundColor: '#f8f9fa' }}
						className="flex-grow-1 overflow-auto mb-3">
   						{[...data].reverse().map((chatItem) => (
							<p style={{ whiteSpace: "pre-wrap", fontFamily: "monospace", margin: 0 }} key={chatItem.timestamp + chatItem.sender_name}>
								{"["}{updateTime(chatItem.timestamp)}{"] | "}
								{chatItem.content.startsWith("#")
									? (<span style={{ fontWeight: "bold", color: "#dc3545" }}>{updateSender("Sytem")}</span>)
									: (<a style={{ cursor: 'pointer' }} onClick={() => navigateTo(`/profile/${chatItem.sender_name}`)}>{updateSender(chatItem.sender_name)}</a>)}{" : "}
								{updateContent(chatItem.content)}
							</p>
						))}
						<div ref={bottomRefs.current[id]} />
					</div>
					<div className="input-group">
						<input type="text" value={ message } className="form-control" placeholder="Write something..."
							onChange={(e) => setMessage(e.target.value)} onKeyDown={(e) => {if (e.key === "Enter") {
								e.preventDefault()
								send(groupID)}}}/>
						{id ? <button className="btn btn-primary" type="button" onClick={() => invite(groupID, realName)}>Play</button> : <></>}
						<button className="btn btn-primary" type="button" onClick={() => send(groupID)}>Send</button>
					</div>
				</div>
			</div>
		)
	}

	return (
		<Modal show={chat} onHide={handleClose} size="xl">
			<Modal.Header closeButton />
			<Modal.Body>
				<div className="d-flex align-items-start w-100">
  					<div className="nav flex-column nav-pills me-3" role="tablist" aria-orientation="vertical">
					{chats.map((chatItem) => (
						<button	key={chatItem.lower}
								className={`nav-link ${chatItem.active ? "active" : ""}`}
								id={`v-pills-${chatItem.lower}-tab`}
								data-bs-toggle="pill"
								data-bs-target={`#v-pills-${chatItem.lower}`}
								type="button"
								role="tab"
								aria-controls={`v-pills-${chatItem.lower}`}
								aria-selected="true"
						>{chatItem.groupNAME}</button>))}
					</div>
					<div className="tab-content flex-grow-1 w-100">
					{chats.map((chatItem) => (
						renderChatTab(chatItem.lower, chatItem.realName, chatItem.active, chatItem.groupID, chatItem.groupNAME, chatItem.id, chatItem.data)))}
					</div>
				</div>
			</Modal.Body>
			<ErrorModal show={ show } hideModal={ hideModal } contextId={ 2 } info={ info } />
		</Modal>
	)
}

export default ChatModal