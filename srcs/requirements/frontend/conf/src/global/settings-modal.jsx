import React, { useState } from "react"
import { Modal, Form, Button } from "react-bootstrap"
import { useAuth } from "../auth/context"
import axiosInstance from '../auth/instance'
import DFAModal from "./dfa-modal"
import ErrorModal from "./error-modal"

function SettingsModal({ settings, setSettings }) {

	const [nUsername, setNUsername] = useState('')
	const [password1, setPassword1] = useState('')
	const [passShow1, setPassShow1] = useState(false)

	const [password2, setPassword2] = useState('')
	const [passShow2, setPassShow2] = useState(false)
	const [nPassword1, setNPassword1] = useState('')
	const [nPassShow1, setNPassShow1] = useState(false)
	const [nPassword2, setNPassword2] = useState('')
	const [nPassShow2, setNPassShow2] = useState(false)
	const [password2FA, setPassword2FA] = useState('')
	const [passShow2FA, setPassShow2FA] = useState(false)
	const [passDelete, setPassDelete] = useState('')
	const [showPassDelete, setShowPassDelete] = useState(false)

	const [dfaShow, setdfaShow] = useState(false)
	const hideDFA = () => setdfaShow(false)

	const [show, setShow] = useState(false)
	const hideModal = () => setShow(false)
	const [info, setInfo] = useState("")

	const { user, refreshUser, logout } = useAuth()

	const handleClose = () => {
		setNUsername("")
		setPassword1("")
		setPassword2("")
		setNPassword1("")
		setNPassword2()
		setPassword2FA("")
		setPassDelete("")
		setSettings(false)
	}

	const changeUsername = async () => {
		try {
			const response = await axiosInstance.put(`/users/api/player/update-name/`,
				{name: nUsername, current_password: password1})
			if (response.data.code == 1000) {
				handleClose()
				refreshUser()
			}
		}
		catch(error) {
			if (error && error.response && error.response.data && error.response.data.message) {
				setInfo(error.response.data.message)
				setShow(true)
			}
		}
	}
	
	const changePassword = async () => {
		try {
			const response = await axiosInstance.put(`/users/api/player/update-PWD/`,
				{current_password: password2, new_pwd1: nPassword1, new_pwd2: nPassword2})
			if (response.data.code == 1000)
				handleClose()
		}
		catch(error) {
			if (error && error.response && error.response.data && error.response.data.message) {
				setInfo(error.response.data.message)
				setShow(true)
			}
		}
	}
	
	const removeProfile = async (password) => {
		try {
			const response = await axiosInstance.put(`/users/api/player/delete/`, {password: password})
			if (response.data.code == 1000)
				logout()
		}
		catch(error) {
			if (error && error.response && error.response.data && error.response.data.message) {
				setInfo(error.response.data.message)
				setShow(true)
			}
		}	
	}

	const remove2FA = async (password2FA) => {
		try {
			const json = {data: {"password": password2FA}}
			const response = await axiosInstance.delete("/users/api/2fa-disable/", json)
			if (response.data.code == 1000) {
				refreshUser()
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

	return (
		<Modal show={settings} onHide={() => handleClose()} centered>
			<Modal.Header closeButton>
				<Modal.Title>Settings</Modal.Title>
			</Modal.Header>
			<Modal.Body>	
				<h5 className="mb-3">Change Username</h5>
				<Form.Group className="mb-3">
					<Form.Control type="text" placeholder="New username" value={nUsername}
						onChange={(e) => setNUsername(e.target.value)}/>
				</Form.Group>
				<Form.Group className="mb-3">
					<div className="d-flex">
						<Form.Control type={passShow1 ? "text" : "password"} placeholder="Current password" value={password1}
							onChange={(e) => setPassword1(e.target.value)} className="rounded-0 rounded-start"/>
						<Button type="button" className="rounded-0 rounded-end btn btn-light"
							aria-label="show" onClick={() => setPassShow1(!passShow1)}>
							{passShow1
								? <i className="eye bi-eye-fill"></i>
								: <i className="eye bi-eye-slash-fill"></i>}
						</Button>
					</div>
				</Form.Group>
				<div className="d-grid mb-4">
					<Button variant="secondary" onClick={changeUsername}>Update Username</Button>
				</div>
				<h5 className="mb-3">Change Password</h5>
				<Form.Group className="mb-2">
					<div className="d-flex">
						<Form.Control type={passShow2 ? "text" : "password"} placeholder="Current password" value={password2}
							onChange={(e) => setPassword2(e.target.value)} className="rounded-0 rounded-start"/>
						<Button type="button" className="rounded-0 rounded-end btn btn-light"
							aria-label="show" onClick={() => setPassShow2(!passShow2)}>
							{passShow2
								? <i className="eye bi-eye-fill"></i>
								: <i className="eye bi-eye-slash-fill"></i>}
						</Button>
					</div>
				</Form.Group>
				<Form.Group className="mb-2">
					<div className="d-flex">
						<Form.Control type={nPassShow1 ? "text" : "password"} placeholder="New password" value={nPassword1}
							onChange={(e) => setNPassword1(e.target.value)} className="rounded-0 rounded-start"/>
						<Button type="button" className="rounded-0 rounded-end btn btn-light"
							aria-label="show" onClick={() => setNPassShow1(!nPassShow1)}>
							{nPassShow1
								? <i className="eye bi-eye-fill"></i>
								: <i className="eye bi-eye-slash-fill"></i>}
						</Button>
					</div>
				</Form.Group>
				<Form.Group className="mb-3">
					<div className="d-flex">
						<Form.Control type={nPassShow2 ? "text" : "password"} placeholder="Confirm new password" value={nPassword2}
							onChange={(e) => setNPassword2(e.target.value)} className="rounded-0 rounded-start"/>
						<Button type="button" className="rounded-0 rounded-end btn btn-light"
							aria-label="show" onClick={() => setNPassShow2(!nPassShow2)}>
							{nPassShow2
								? <i className="eye bi-eye-fill"></i>
								: <i className="eye bi-eye-slash-fill"></i>}
						</Button>
					</div>
				</Form.Group>
				<div className="d-grid mb-4">
					<Button variant="secondary" onClick={changePassword}>Update Password</Button>
				</div>
				<h5 className="mb-3">{user.two_factor_enabled ? "Remove 2FA" : "Enable 2FA"}</h5>
				<Form.Group className="mb-3">
					{user.two_factor_enabled
						? <div className="d-flex">
							<Form.Control type={passShow2FA ? "text" : "password"} placeholder="Insert password"
								value={password2FA} onChange={(e) => setPassword2FA(e.target.value)}
								className="rounded-0 rounded-start"/>
							<Button type="button" className="rounded-0 rounded-end btn btn-light"
								aria-label="show" onClick={() => setPassShow2FA(!passShow2FA)}>
								{passShow2FA
									? <i className="eye bi-eye-fill"></i>
									: <i className="eye bi-eye-slash-fill"></i>}
							</Button>
						</div>
						: <></>}
				</Form.Group>
				<div className="d-grid mb-4">
					{user.two_factor_enabled
						? <Button variant="secondary" onClick={() => remove2FA(password2FA)}>Remove</Button>
						: <Button variant="secondary" onClick={() => setdfaShow(true)}>Enable</Button>}
					
				</div>
				<h5 className="mb-3">Delete Account</h5>
				<Form.Group className="mb-3">
					<div className="d-flex">
						<Form.Control type={showPassDelete ? "text" : "password"} placeholder="Insert password"
							value={passDelete} onChange={(e) => setPassDelete(e.target.value)}
							className="rounded-0 rounded-start"/>
						<Button type="button" className="rounded-0 rounded-end btn btn-light"
							aria-label="show" onClick={() => setShowPassDelete(!showPassDelete)}>
							{showPassDelete
								? <i className="eye bi-eye-fill"></i>
								: <i className="eye bi-eye-slash-fill"></i>}
							</Button>
						</div>
				</Form.Group>
				<div className="d-grid mb-4">
					<Button variant="danger" onClick={() => removeProfile(passDelete)}>Delete</Button>
				</div>
			</Modal.Body>
			<DFAModal show={ dfaShow } hide={ hideDFA } handleClose={ handleClose }/>
			<ErrorModal show={ show } hideModal={ hideModal } contextId={ 4 } info={ info } />
		</Modal>
	)
}

export default SettingsModal