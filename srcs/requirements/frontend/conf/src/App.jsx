import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { useAuth } from "./auth/context"
import AuthRedirect from './auth/redirect'
import LoginPage from './login/page'
import RegisterPage from './register/page'
import OauthPage from './Oauth/page'
import Complete from './Oauth/complete/page'
import HomePage from './home/page'
import Profile from './profile/page'
import ProfileEdit from './profile/edit/page'
import Online from './online/page'
import Tournament from './tournament/page'

const App = () => {

	const { loading, user } = useAuth()

	if (loading)
		return(<div className="text-center mt-5">Loading...</div>)

	return (
		<AuthRedirect>
			<Routes>
				<Route path="/" element={ <LoginPage/> }/>
				<Route path="/register" element={ <RegisterPage/> }/>
				<Route path="/register/42" element={ <OauthPage/> }/>
				<Route path="/register/42/complete" element={ <Complete/> }/>
				<Route path="/home" element={ <HomePage user={ user }/> }/>
				<Route path="/profile/:userID" element={ <Profile user={ user }/> }/>
				<Route path="/profile/:userID/edit" element={ <ProfileEdit user={ user }/> }/>
				<Route path="/online" element={ <Online user={ user }/>}/>
				<Route path="/tournament" element={ <Tournament user={ user }/>}/>
				<Route path="*" element={ <NotFound/>}/>
			</Routes>
		</AuthRedirect>)
}

export default App

const NotFound = () => {
	return(<div className="text-center mt-5">Error 404</div>)
}