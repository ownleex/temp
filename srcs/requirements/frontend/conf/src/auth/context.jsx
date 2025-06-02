import React, { createContext, useContext, useState, useEffect } from 'react'
import { refreshData, getData, removeData } from './data.js'
import axiosInstance, { refreshAtoken } from './instance'
import { useLocation } from "react-router-dom"

export const AuthContext = createContext()

export const AuthProvider = ({ children }) => {

	const [user, setUser] = useState(null)
	const [loading, setLoading] = useState(true)
	const [isAuth, setIsAuth] = useState(false)
	const location = useLocation()

	const isTokenExpired = (Atoken) => {
		if (!Atoken || !Atoken.includes('.')) return true
		try {
			const payload = JSON.parse(atob(Atoken.split('.')[1]))
			const expiryTime = payload.exp * 1000
			return Date.now() >= expiryTime
		}
		catch(error) {return true}
	}

	const isTokenInvalid = async (Atoken, Rtoken) => {
		if (!Atoken || !Rtoken) return true
		try {
			const tokens = await axiosInstance.post('/users/api/token/refresh/', { refresh: Rtoken })
			if (Atoken == tokens.data.access) return false
			return true
		}
		catch {return true}
	}

	const checkAuth = async () => {
		const Atoken = localStorage.getItem('Atoken')
		const Rtoken = localStorage.getItem('Rtoken')
		if (!Atoken || !Rtoken) return false
		if (isTokenExpired(Atoken)) return await refreshAtoken(Rtoken, "")
		//if (isTokenInvalid(Atoken, Rtoken)) return false
		return true
	}

	const refreshUser = async () => {
		try {
			const auth = await checkAuth()
			if (!auth) {
				logout()
				return
			}
			if 	(location.pathname.includes("/users/api/login/", "/users/api/register/",
				"/users/api/auth-42/register/", "/users/api/auth-42/callback/?code=",
				"/users/api/auth-42/status/", "/users/api/auth-42/complete/"))
				return
			setIsAuth(auth)
			await refreshData()
			const updatedUser = await getData()
			setUser(updatedUser)
		}
		catch (error) {logout()}
	}

	const logout = () => {
		removeData()
		setUser(null)
		setIsAuth(false)
		if (!(location.pathname.includes("/") || location.pathname.includes("/register")))
			window.location.reload()
	}

	useEffect(() => {
		const init = async () => {
			try {
				await refreshUser()
			}
			catch {}
			finally {
				setLoading(false)
			}
		}
		init()
	}, [])

	return (
		<AuthContext.Provider value={ { user, isAuth, loading, refreshUser, logout } }>
			{children}
		</AuthContext.Provider>
	)
}

export const useAuth = () => useContext(AuthContext)
