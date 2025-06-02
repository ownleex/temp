import React, { createContext, useContext, useEffect, useRef, useState } from 'react'
import { useNavigate } from "react-router-dom"
import { useAuth } from '../auth/context'
import axiosInstance from '../auth/instance'
import axios from 'axios'

const ChatContext = createContext(null)

export const useChat = () => useContext(ChatContext)

export const Chat = ({ children }) => {
	const navigate = useNavigate()
	const socketRef = useRef(null)
	const [messages, setMessages] = useState([])
	const { isAuth } = useAuth()

	useEffect(() => {
		if (!isAuth) return
		const Rtoken = localStorage.getItem("Rtoken")
		if (!Rtoken) return

		let isMounted = true
		let wsInstance = null

		const createChatSocket = async (Rtoken, onMessage, onError, onClose) => {
			const tokens = await axiosInstance.post('/users/api/token/refresh/', { refresh: Rtoken })
			const ws = new WebSocket(`wss://${location.host}/live_chat/ws/chat/general/?token=${tokens.data.access}`)

			ws.onopen = () => {}
			ws.onmessage = (event) => {
				const data = JSON.parse(event.data)
				onMessage?.(data)
			}
			ws.onerror = (error) => {onError?.(error)}
			ws.onclose = () => {onClose?.()}
			return ws
		}

		const initChatSocket = async () => {
			try {
				const containerStatus = await axios.get(`https://${location.host}/live_chat/api/status/`)
				if (containerStatus.data.code != 1000) return
				const ws = await createChatSocket(Rtoken, (data) => {
					if (data && data.code == 1000) return
					setMessages(data)
				}, (error) => {navigate("/home")}, () => {setMessages([])})
				if (isMounted) {
					socketRef.current = ws
					wsInstance = ws
				}
			}
			catch {}
		}

		initChatSocket()

		return () => {
			isMounted = false
			if (wsInstance?.readyState === WebSocket.OPEN || wsInstance?.readyState === WebSocket.CONNECTING)
				wsInstance.close()
		}

	}, [isAuth])

	return (
		<ChatContext.Provider value={{ getSocket: () => socketRef.current, messages }}>
			{children}
		</ChatContext.Provider>
	)
}
