import React, { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { Card } from "react-bootstrap"
import { useGame } from "../websockets/game"

function Home() {

	const navigate = useNavigate()

	const { getSocket, closeSocket } = useGame()
	const socket = getSocket()
  
	const cardData = [
		{ src: "Online.svg", title: "Online", path: "/online" },
		{ src: "Crown.svg", title: "Tournament", path: "/tournament" }]

	useEffect(() => {
		if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING))
			closeSocket()
	}, [])
		
	function CardItem({ card }) {
	
		const [hovered, setHovered] = useState(true);
		
		return (
			<div role="button" onClick={() => navigate(card.path)} className="col-12 col-sm-6 col-lg-4 col-xl-3 mb-4 d-flex justify-content-center"
				style={{transition: "transform 0.6s", transformStyle: "preserve-3d", cursor: "pointer" }}
				onMouseEnter={() => setHovered(false)} onMouseLeave={() => setHovered(true)}>
				{hovered ?
					<Card className="p-3 p-sm-4 p-xl-5 pb-0 rounded-0 text-bg-dark">
						<Card.Img variant="top" src={card.src} />
						<Card.Body className="pt-3 pt-sm-4 pt-xl-5 pb-3 pb-sm-0">
							<Card.Title className="row justify-content-center m-0">{card.title}</Card.Title>
						</Card.Body>
					</Card> :
					<Card className="p-3 p-sm-4 p-xl-5 pb-0 rounded-0 text-bg-dark">
						<Card.Img variant="top" src={card.src}/>
						<Card.Body className="pt-3 pt-sm-4 pt-xl-5 pb-3 pb-sm-0">
							<Card.Title className="row justify-content-center m-0">Play !</Card.Title>
						</Card.Body>
					</Card>}
			</div>
		)
	}

	return (
		<div className="container py-5">
			<div className="row justify-content-center g-4">
			{cardData.map((card) => (<CardItem card={ card }/>))}
			</div>
		</div>
	)
}  

export default Home