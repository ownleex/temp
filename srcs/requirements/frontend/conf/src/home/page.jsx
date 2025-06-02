import React from "react"
import Header from "../global/header"
import Background from "../background/background.jsx"
import Home from "./home"

function HomePage({ user }) {

	return (
		<>
			<Header user={ user }/>
			<main>
				<Background type={"private"}/>
				<div className="d-flex vh-100 w-100 justify-content-center align-items-lg-center pt-5 pt-lg-0 px-xl-5">
					<div className="pt-5 pt-lg-0 px-xl-5">
						<Home/>
					</div>
				</div>
			</main>
		</>
	)
}  

export default HomePage
