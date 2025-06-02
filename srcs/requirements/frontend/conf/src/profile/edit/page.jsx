import React, { useState } from "react"
import { useLocation } from "react-router-dom"
import Header from "../../global/header.jsx"
import Background from '../../background/background.jsx'
import ProfileEdit from "./edit.jsx"

function ProfileEditPage({ user }) {

	const url = useLocation()
	const username = url.pathname.split('/')[2]

	return (
		<>
			<Header user={ user }/>
			<main>
				<Background type={"private"} />
				{user.name == username ?
					<div className="position-absolute top-50 start-50 translate-middle mt-3">
						<div className="rounded border border-black border-2 px-3 px-lg-5 pt-2 pt-lg-4 pb-3 pb-lg-4"
							style={{background: "rgba(0, 0, 0, 0.7)"}}>
							<ProfileEdit user={ user }/>
						</div>
					</div> :
					<></>}
			</main>
		</>
	)
}

export default ProfileEditPage