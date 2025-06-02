import React from "react"
import { useNavigate } from "react-router-dom"
import { Modal, Button } from "react-bootstrap"
import { useAuth } from "../auth/context"
import axiosInstance from '../auth/instance'

function QuitModal({ quit, setQuit }) {

	const { logout } = useAuth()
	const navigate = useNavigate()

	const handleClose = () => setQuit(false)

	const disconnect = async (e) => {
		e.preventDefault()
		try {
			const response = await axiosInstance.post('/users/api/logout/')
			if (response.data.code == 1000) {
				logout()
				handleClose()
				navigate("/")
			}
		}
		catch {handleClose()}
	}

	return (
		<Modal show={quit} onHide={handleClose}>
			<Modal.Header closeButton>
				<Modal.Title>Are you sure you want to log out ?</Modal.Title>
			</Modal.Header>
			<Modal.Body>
				<div className="d-flex justify-content-center gap-2">
					<Button onClick={disconnect} className="global-quit-yes">Yes</Button>
					<Button onClick={handleClose} className="global-quit-no">No</Button>
				</div>
			</Modal.Body>
		</Modal>
	)
}

export default QuitModal