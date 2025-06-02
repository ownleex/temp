import React from "react"
import { Modal } from "react-bootstrap"

function ErrorModal({ show, hideModal, contextId, info }) {

	const context = ["Registration", "Connection", "Chat", "Friend", "Settings", "Game", "Edition"]

	return (
		<Modal show={show} onHide={hideModal}>
			<Modal.Header closeButton>
				<Modal.Title>{context[contextId]} Error !</Modal.Title>
			</Modal.Header>
			<Modal.Body>{info}</Modal.Body>
		</Modal>
	)
}

export default ErrorModal