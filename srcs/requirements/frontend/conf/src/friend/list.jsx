import React, { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../auth/context"
import axiosInstance from '../auth/instance'

function ListModal({ tab, setShow, setInfo }) {

	const navigate = useNavigate()

	const { user } = useAuth()
	const [data, setData] = useState()
	const [search, setSearch] = useState('')
	const [filteredFriends, setFilteredFriends] = useState()

	const list = async () => {
		try {
			const playerData = await axiosInstance.get('/users/api/player/')
			const friendData = await axiosInstance.get('/users/api/friend/list/')
			let temp

			const getID = (name) => {
				const player = friendData.data.find(friend => friend.player_1 === name && friend.player_2 == user.name)
				return player.id
			}

			temp = playerData.data
				.filter(player => friendData.data.some(friend => friend.status == "accepted" && friend.player_1 == user.name && friend.player_2 == player.name))
				.map(player => ({name: player.name, id: getID(player.name), avatar: player.avatar}))

			setData(temp)
			setFilteredFriends(temp)
		}
		catch(error) {
			if (error && error.response && error.response.data && error.response.data.message) {
				setInfo(error.response.data.message)
				setShow(true)
			}
		}
	}

	const viewProfile = async (name) => {
		navigate(`/profile/${name}`)
	}

	const removeFriend = async (playerID) => {
		const json = {data: {"id": playerID}}
		try {await axiosInstance.delete(`/users/api/friend/remove/`, json)}
		catch(error) {
			if (error && error.response && error.response.data && error.response.data.message) {
				setInfo(error.response.data.message)
				setShow(true)
			}
		}
		finally {list()}
	}

	const filterList = (e) => {
		const query = e.target.value
		setSearch(query)
		if (!data) return
		const filtered = data.filter(player =>player.name.toLowerCase().includes(query.toLowerCase()))
		setFilteredFriends(filtered)
	}
	
	useEffect(() => {
		if (tab == "friendlist")
			list()
	}, [tab])

	return (
		<>
			<div className="d-flex justify-content-center mb-3">
				<input type="text" className="form-control w-50" placeholder="Search for a friend..." value={search} onChange={filterList} id="searchfriendList"/>
			</div>
			<div className="d-flex flex-column align-items-center">
				<ul className="list-unstyled w-100 d-flex flex-column align-items-center gap-3">
				{filteredFriends && filteredFriends.length > 0 
					? (filteredFriends.map((player, index) => (
					<li key={index} className="d-flex align-items-center justify-content-between bg-light rounded p-2 w-50 border-bottom">
						<div className="d-flex align-items-center gap-2">
							<img src={player.avatar} alt="Avatar" style={{ width: '40px', height: '40px', borderRadius: '50%' }}/>
							<span className="fw-bold">{player.name}</span>
						</div>
						<div className="d-flex gap-3">
							<i className="bi bi-person-square fs-4" onClick={() => viewProfile(player.name)} />
							<i className="bi bi-x fs-4" onClick={() => removeFriend(player.id)} />
						</div>
					</li>)))
					: <li>No friends found</li> }
				</ul>
			</div>
		</>
	)
}

export default ListModal