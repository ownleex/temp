import React, { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Form, Modal, Button } from "react-bootstrap"
//import axiosInstance from "../auth/instance"
import axios from 'axios'
import { useAuth } from "../auth/context"

function DFAModal({ show, hide, username, password }) {

	const navigate = useNavigate()
	const { refreshUser } = useAuth()
	const [code, setCode] = useState("")

	const login = async (code) => {
		try {
			const response = await axios.post(`https://${location.host}/users/api/login/`, {
				username: username,
				password: password,
				otp_code: code})
			if (response.data.code == 1000) {
				hide()
				localStorage.setItem('Atoken', response.data.tokens.access)
				localStorage.setItem('Rtoken', response.data.tokens.refresh)
				localStorage.setItem('data', JSON.stringify({name: username, id: response.data.player}))
				await refreshUser()
				navigate("/home")
			}
		}
		catch {hide()}
	}

	return (
		<Modal show={show} onHide={hide}>
			<Modal.Header closeButton/>
			<Modal.Body>
				<Form.Group className="mb-3">
					<Form.Control type="text" placeholder="Insert 2FA code" value={code}
						onChange={(e) => setCode(e.target.value)}/>
				</Form.Group>
				<div className="d-grid mb-4">
					<Button type="button" className="btn btn-secondary rounded fw-bolder"
						onClick={() => login(code)}>Confirm</Button>
				</div>
			</Modal.Body>
		</Modal>
	)
}

export default DFAModal