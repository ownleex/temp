import React, { createContext, useContext, useEffect, useRef, useState } from 'react'
import { useNavigate } from "react-router-dom"
import { useAuth } from "../auth/context.jsx"
import axiosInstance from '../auth/instance'
import axios from 'axios'

const NotificationContext = createContext(null)

export const useNotification = () => useContext(NotificationContext)

export const Notification = ({ children }) => {
	const navigate = useNavigate()
	const socketRef = useRef(null)
	const [NotifMessages, setNotifMessages] = useState([])
	const { isAuth } = useAuth()

	useEffect(() => {
		if (!isAuth) return
		const Rtoken = localStorage.getItem("Rtoken")
		if (!Rtoken) return

		let isMounted = true
		let wsInstance = null

		const createNotifSocket = async (Rokten, onMessage, onError, onClose) => {
			const tokens = await axiosInstance.post('/users/api/token/refresh/', { refresh: Rtoken })
			const ws = new WebSocket(`wss://${location.host}/pong/ws/notifications/?token=${tokens.data.access}`)
			
			ws.onopen = () => {}
			ws.onmessage = (event) => {
				const data = JSON.parse(event.data)
				onMessage?.(data)
			}
			ws.onerror = (error) => {onError?.(error)}
			ws.onclose = () => {onClose?.()}
			return ws
		}

		const initNotifSocket = async () => {
			try {
				const containerStatus = await axios.get(`https://${location.host}/users/api/status/`)
				if (containerStatus.data.code != 1000) return
				const ws = await createNotifSocket(Rtoken, (data) => {
					if (data.type) setNotifMessages(data)
				}, (error) => {navigate("/home")}, () => {setNotifMessages([])})
				if (isMounted) {
					socketRef.current = ws
					wsInstance = ws
				}
			}
			catch {}
		}

		initNotifSocket()

		return () => {
			isMounted = false
			if (wsInstance?.readyState === WebSocket.OPEN || wsInstance?.readyState === WebSocket.CONNECTING)
				wsInstance.close()
		}

	}, [isAuth])

	return (
		<NotificationContext.Provider value={{ socket: socketRef.current, NotifMessages, setNotifMessages }}>
			{children}
		</NotificationContext.Provider>
	)
}
