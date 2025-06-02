import React, { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { Button, Form } from "react-bootstrap"
import { useAuth } from "../auth/context"
import ErrorModal from "../global/error-modal"
import axiosInstance from "../auth/instance"
import DFAModal from "./dfa-modal"

function Login() {

	const { refreshUser } = useAuth()

	const navigate = useNavigate()

	const [username, setUsername] = useState('')
	const [password, setPassword] = useState('')
	const [DFAcode, setDFAcode] = useState('')

	const [passShow, setPassShow] = useState(false)
	const showPass = () => setPassShow(true)
	const hidePass = () => setPassShow(false)

	const [show, setShow] = useState(false)
	const hideModal = () => setShow(false)
	const [info, setInfo] = useState("")

	const [dfaShow, setdfaShow] = useState(false)
	const hideDFA = () => setdfaShow(false)

	const sendAuth = async (e) => {
		e.preventDefault()
		try {
			const response = await axiosInstance.post('/users/api/login/', {
				username: username,
				password: password,
				otp_code: DFAcode})
			if (response.data.code == 1000) {
				localStorage.setItem('Atoken', response.data.tokens.access)
				localStorage.setItem('Rtoken', response.data.tokens.refresh)
				localStorage.setItem('data', JSON.stringify({name: username, id: response.data.player}))
				await refreshUser()
				navigate("/home")
			}
		}
		catch (error) {
			if (error.response.data.code == "1037") {
				if (username && password)
					setdfaShow(true)
			}
			else {
				setUsername("")
				setPassword("")
				if (error && error.response && error.response.data && error.response.data.message) {
					setInfo(error.response.data.message)
					setShow(true)
				}
			}
		}
	}

	useEffect(() => {
		if (!dfaShow) {
			setUsername("")
			setPassword("")
		}
	}, [dfaShow])

	return (
        <Form>
            <Form.Group className="fs-5 fs-lg-4 mb-2 mb-lg-4">
                <Form.Label className="mb-2 text-light" htmlFor="username">Username</Form.Label>
                <Form.Control
                    type="text"
                    value={username}
                    placeholder="Insert username"
                    onChange={(e) => setUsername(e.target.value)}
					name="username"
					id="username"
					autoComplete="username"
                />
            </Form.Group>
            <Form.Group className="fs-5 fs-lg-4 mb-2 mb-lg-4">
                <Form.Label className="mb-2 text-light" htmlFor="password">Password</Form.Label>
                <div className="d-flex">
                    <Form.Control
                        type={passShow ? "text" : "password"}
                        value={password}
                        placeholder="Insert password"
                        onChange={(e) => setPassword(e.target.value)}
                        className="rounded-0 rounded-start"
						name="password"
						id="password"
						autoComplete="current-password"
                    />
                    <Button
                        type="button"
                        className="rounded-0 rounded-end btn btn-light"
						aria-label="show"
                        onClick={passShow ? hidePass : showPass}
                    >
                        {passShow ? <i className="eye bi-eye-fill"></i>
                                  : <i className="eye bi-eye-slash-fill"></i>}
                    </Button>
                </div>
            </Form.Group>
			<div className="d-flex justify-content-center pt-3 mb-3 mb-lg-5">
				<Button
					type="button"
					className="btn btn-secondary rounded fw-bolder"
					onClick={sendAuth}
				>
					LOGIN
				</Button>
			</div>
			<div className="d-flex justify-content-end pt-3">
				<Button
					type="button"
					className="btn btn-secondary rounded fw-bolder"
					onClick={() => navigate("/register")}
				>
					REGISTER
				</Button>
			</div>
			<ErrorModal show={ show } hideModal={ hideModal } contextId={ 1 } info={ info } />
			<DFAModal show={ dfaShow } hide={ hideDFA } username={ username } password={ password }/>
        </Form>
    )
}

export default Login