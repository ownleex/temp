import React, { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Button, Form } from "react-bootstrap"
import ErrorModal from "../global/error-modal"
import axiosInstance from '../auth/instance'

function OauthRegister() {
    const navigate = useNavigate()
    const [isLoading, setIsLoading] = useState(false)
    const [show, setShow] = useState(false)
    const [info, setInfo] = useState("")
    
    const hideModal = () => setShow(false)

    const redirectTo42 = async () => {
        setIsLoading(true)
        try {
            const response = await axiosInstance.get('/users/api/auth-42/register/')
            
            if (response.data.code === 1000 && response.data.redirect_url)
                window.location.href = response.data.redirect_url
            else
                throw new Error("Réponse invalide du serveur")
        }
		catch (error) {
			if (error && error.response && error.response.data && error.response.data.message) {
				setInfo(error.response.data.message)
				setShow(true)
			}
        }
		finally {setIsLoading(false)}
    }

    return (
		<Form className="text-light">
			<h3 className="text-center mb-4">Registration with 42</h3>
            <p className="text-center mb-4">Sign in with your 42 account to register on our platform.</p>
			<div className="d-flex justify-content-center mb-4">
				<Button type="button" className="btn btn-primary rounded fw-bolder" onClick={redirectTo42}
                    disabled={isLoading} size="lg">
                    {isLoading ? "LOADING..." : "REGISTER WITH 42"}
                </Button>
			</div>
			<div className="d-flex justify-content-center">
				<Button type="button" variant="outline-light" className="rounded me-2" onClick={() => navigate("/register")}>
                    Standard registration
                </Button>
				<Button type="button" variant="outline-light" className="rounded" onClick={() => navigate("/")}>
                    Back to login
                </Button>
			</div>
            <ErrorModal show={ show } hideModal={ hideModal } contextId={ 0 } info={ info } />
        </Form>
    )
}

export default OauthRegister
