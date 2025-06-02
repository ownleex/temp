import React, { useEffect, useState } from "react"
import { Form, Modal, Button } from "react-bootstrap"
import axiosInstance from "../auth/instance"
import { useAuth } from "../auth/context"
import ErrorModal from "./error-modal"

function DFAModal({ show, hide, handleClose }) {

	const { refreshUser } = useAuth()
	const [qrCode, setQrCode] = useState("")
	const [code, setCode] = useState("")

	const [showErr, setShowErr] = useState(false)
	const hideModal = () => setShow(false)
	const [info, setInfo] = useState("")

	const fonction = async () => {
		try {
			const response = await axiosInstance.put("/users/api/2fa-enable/")
			if (response.data.code == "1000")
				setQrCode(response.data.qr_code_image)
		}
		catch(error) {
			if (error && error.response && error.response.data && error.response.data.message) {
				setInfo(error.response.data.message)
				setShowErr(true)
			}
		}
	}

	const fonction2 = async (code) => {
		try {
			const response = await axiosInstance.put("/users/api/2fa-enable/", {otp_code: code})
			if (response.data.code == "1000") {
				refreshUser()
				hide()
				handleClose()
			}
		}
		catch(error) {
			if (error && error.response && error.response.data && error.response.data.message) {
				setInfo(error.response.data.message)
				setShow(true)
			}
		}
	}

	useEffect(() => {
		if (show)
			fonction()
	}, [show])

	return (
		<Modal show={show} onHide={hide}>
			<Modal.Header closeButton>
				<Modal.Title>Enable 2FA</Modal.Title>
			</Modal.Header>
			<Modal.Body>
				<Form.Group className="mb-3">
				{qrCode && (
					<div className="text-center mb-3">
						<img src={qrCode} alt="QR Code" style={{ maxWidth: "100%" }} />
					</div>)}
					<Form.Control type="text" placeholder="Insert 2FA code" value={code}
						onChange={(e) => setCode(e.target.value)}/>
				</Form.Group>
				<div className="d-grid mb-4">
					<Button type="button" className="btn btn-secondary rounded fw-bolder"
						onClick={() => fonction2(code)}>Confirm</Button>
				</div>
			</Modal.Body>
			<ErrorModal show={ showErr } hideModal={ hideModal } contextId={ 4 } info={ info } />
		</Modal>
	)
}

export default DFAModal