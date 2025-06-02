import React from 'react'
import { useLocation, Navigate } from 'react-router-dom'
import { useAuth } from './context'

const publicRoutes = ['/', '/register', '/register/42', '/register/42/complete']

const AuthRedirect = ({ children }) => {

	const { isAuth, loading } = useAuth()
	const location = useLocation()

	if (loading)
		return null

	const isPublic = publicRoutes.includes(location.pathname)

	if (isAuth && isPublic)
		return <Navigate to="/home" replace />
	if (!isAuth && !isPublic)
		return <Navigate to="/" replace />

	return children
}

export default AuthRedirect