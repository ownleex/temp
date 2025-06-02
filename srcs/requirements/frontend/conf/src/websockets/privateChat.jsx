import React, { createContext, useContext, useEffect, useRef, useState } from 'react'
import { useNavigate } from "react-router-dom"
import { useAuth } from '../auth/context'
import axiosInstance from '../auth/instance'
import axios from 'axios'

const PrivateChatContext = createContext(null)

export const usePrivateChat = () => useContext(PrivateChatContext)

export const PrivateChat = ({ children }) => {
	const navigate = useNavigate()
	const socketRef = useRef(null)
	const [privMessages, setMessages] = useState([])
	const { user } = useAuth()

	useEffect(() => {
		if (!user) return
		const Rtoken = localStorage.getItem("Rtoken")
		if (!Rtoken) return

		let isMounted = true
		let wsInstance = null

		const createPrivateSocket = async (Rtoken, onMessage, onError, onClose) => {
			const tokens = await axiosInstance.post('/users/api/token/refresh/', { refresh: Rtoken })
			const ws = new WebSocket(`wss://${location.host}/live_chat/ws/chat/private/${user.id}/?token=${tokens.data.access}`)
		
			ws.onopen = () => {}
			ws.onmessage = (event) => {
				const data = JSON.parse(event.data)
				onMessage?.(data)
			}
			ws.onerror = (error) => {onError?.(error)}
			ws.onclose = () => {onClose?.()}
			return ws
		}

		const initPrivateSocket = async () => {
			try {
				const containerStatus = await axios.get(`https://${location.host}/live_chat/api/status/`)
				if (containerStatus.data.code != 1000) return
				const ws = await createPrivateSocket(Rtoken, (data) => {
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

		initPrivateSocket()

		return () => {
			isMounted = false
			if (wsInstance?.readyState === WebSocket.OPEN || wsInstance?.readyState === WebSocket.CONNECTING)
				wsInstance.close()
		}
	
	}, [user])

	return (
		<PrivateChatContext.Provider value={{ getSocket: () => socketRef.current, privMessages }}>
			{children}
		</PrivateChatContext.Provider>
	)
}
