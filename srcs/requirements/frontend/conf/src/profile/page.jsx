import React, { useState, useEffect } from "react"
import { useLocation } from "react-router-dom"
import Header from "../global/header.jsx"
import Background from '../background/background.jsx'
import Profile from "./profile.jsx"
import axiosInstance from '../auth/instance'

function ProfilePage({ user }) {

	const location = useLocation()
	const [profile, setProfile] = useState(null)

	useEffect(() => {
		const checkURL = async () => {
			try {
				const path = location.pathname.split('/')
				if (path.length > 3) return
				const username = path[2]
				const Atoken = localStorage.getItem('Atoken')
				const Rtoken = localStorage.getItem('Rtoken')
				const config = {headers: {Authorization: `Bearer ${Atoken}`}}
				const params = { token: Rtoken }
				const playerData = await axiosInstance.get('/users/api/player/', {headers: config.headers, param: params})
				const data = playerData.data.filter(player => player.name == username)
				if (data.length == 1)
					setProfile(data[0])
			}
			catch {}
		}
		checkURL()
	}, [location.pathname])

	return (
		<>
			<Header user={ user }/>
			<main>
				<Background type={"private"} />
				<div className="position-absolute top-50 start-50 translate-middle mt-3">
					<div className="rounded border border-black border-2 px-3 px-lg-5 pt-2 pt-lg-4 pb-3 pb-lg-4"
						style={{background: "rgba(0, 0, 0, 0.7)"}}>
						{profile ? <Profile user={ user } profile={ profile }/> : <div className="text-white text-center">Profile not found</div>}
					</div>
				</div>
			</main>
		</>
	)
}

export default ProfilePage