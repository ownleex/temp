import React, { useState, useEffect } from "react"
import { useAuth } from "../auth/context"
import axiosInstance from '../auth/instance'

function SearchModal({ tab, setShow, setInfo }) {

	const { user } = useAuth()
	const [data, setData] = useState()
	const [search, setSearch] = useState('')
	const [filteredFriends, setFilteredFriends] = useState()

	const list = async () => {
		try {
			const playerData = await axiosInstance.get('/users/api/player/')
			const friendData = await axiosInstance.get('/users/api/friend/list/')
			const blockData = await axiosInstance.get('/users/api/block/list/')
			let temp

			temp = playerData.data
				.filter(player => user.name != player.name &&
					!friendData.data.some(friend => friend.player_1 == player.name || friend.player_2 == player.name) &&
					!blockData.data.some(block => block.blocker == player.name || block.blocked == player.name))
				.map(player => ({name: player.name, id: player.id, avatar: player.avatar}))

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

	const addFriend = async (playerID) => {
		try {await axiosInstance.post('/users/api/friend-request/send/', { player_2: playerID })}
		catch(error) {
			if (error && error.response && error.response.data && error.response.data.message) {
				setInfo(error.response.data.message)
				setShow(true)
			}
		}
		finally {list()}
	}

	const addBlock = async (playerID) => {
		try {await axiosInstance.post('/users/api/block/add', { blocked_id: playerID })} //manque un /
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
		if (tab == "addfriend")
			list()
	}, [tab])

	return (
		<>
			<div className="d-flex justify-content-center mb-3">
				<input type="text" className="form-control w-50" placeholder="Search for a friend..." value={search} onChange={filterList} id="searchfriendSearch"/>
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
							<i className="bi bi-person-plus-fill fs-4" onClick={() => addFriend(player.id)} />
							<i className="bi bi-slash-circle fs-4" onClick={() => addBlock(player.id)} />
						</div>
					</li>)))
					: <li>No friends found</li> }
				</ul>
			</div>
		</>
	)
}

export default SearchModal