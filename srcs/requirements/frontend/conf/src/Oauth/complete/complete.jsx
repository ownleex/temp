import React, { useState, useEffect } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import { Button, Form, Alert, Spinner, Card } from "react-bootstrap"
import ErrorModal from "../../global/error-modal"
import axiosInstance from '../../auth/instance'

function Complete() {
    const navigate = useNavigate()
    const location = useLocation()

    const [password1, setPassword1] = useState('')
    const [password2, setPassword2] = useState('')
    const [codeProcessed, setCodeProcessed] = useState(false)
    const [processingCode, setProcessingCode] = useState(false)
    const [showPasswordForm, setShowPasswordForm] = useState(false)
    
    // États pour l'inscription réussie
    const [registrationSuccess, setRegistrationSuccess] = useState(false)
    const [playerName, setPlayerName] = useState('')

    const [passShow1, setPassShow1] = useState(false)
    const showPass1 = () => setPassShow1(true)
    const hidePass1 = () => setPassShow1(false)

    const [passShow2, setPassShow2] = useState(false)
    const showPass2 = () => setPassShow2(true)
    const hidePass2 = () => setPassShow2(false)

    const [show, setShow] = useState(false)
    const hideModal = () => setShow(false)
    const [info, setInfo] = useState("")
    const [isLoading, setIsLoading] = useState(false)

    // Traiter le code d'autorisation lors du chargement du composant
    useEffect(() => {
        const processAuthCode = async () => {
            const searchParams = new URLSearchParams(location.search)
            const authorizationCode = searchParams.get('code')
            
            if (!authorizationCode) return

            setProcessingCode(true)
            
            try {
                // Envoyer le code au backend en utilisant une requête GET avec le code dans l'URL
                const response = await axiosInstance.get(`/users/api/auth-42/callback/?code=${authorizationCode}`)
                
                if (response.data.code === 1000) {
                    setCodeProcessed(true)
                    setShowPasswordForm(true)
                    
                    // Nettoyer l'URL en supprimant le paramètre code
                    navigate('/register/42/complete', { replace: true })
                }
				else
                    throw new Error("Réponse invalide du serveur")
            }
			catch (error) {
                if (error && error.response && error.response.data && error.response.data.message) {
					setInfo(error.response.data.message)
					setShow(true)
				}
            }
			finally {setProcessingCode(false)}
        }
        
        // Vérifier s'il y a un code dans l'URL et s'il n'a pas encore été traité
        const searchParams = new URLSearchParams(location.search)
        if (searchParams.has('code') && !codeProcessed) {
            processAuthCode()
        } else if (!searchParams.has('code') && !codeProcessed) {
            // Si pas de code et pas encore traité, vérifier si la session est valide
            const checkSession = async () => {
                try {
                    const response = await axiosInstance.get('/users/api/auth-42/status/')
                    if (response.data.code === 1000) {
                        setShowPasswordForm(true)
                    } else {
                        navigate('/register/42') // Rediriger vers la page d'inscription
                    }
                } catch (error) {
                    navigate('/register/42') // Rediriger vers la page d'inscription en cas d'erreur
                }
            }
            
            checkSession()
        }
    }, [location, navigate, codeProcessed])

    const completeAuth = async (e) => {
        e.preventDefault()
        setIsLoading(true)
        try {
            // Soumettre les mots de passe au backend
            const response = await axiosInstance.post('/users/api/auth-42/complete/', {
                password: password1,
                password2: password2
            })
            if (response.data.code === 1000) {
                // Récupérer le nom du joueur
                setPlayerName(response.data.name || '')
                
                // Afficher l'écran de succès et masquer le formulaire
                setRegistrationSuccess(true)
                setShowPasswordForm(false)
            }
        }
		catch (error) {
            setPassword1("")
            setPassword2("")
            if (error && error.response && error.response.data && error.response.data.message) {
				setInfo(error.response.data.message)
				setShow(true)
			}
        }
		finally {setIsLoading(false)}
    }

    // Afficher un spinner pendant le traitement du code
    if (processingCode) {
        return (
            <div className="text-center text-light">
                <Spinner animation="border" role="status" variant="light" />
                <p className="mt-3">Processing authentication...</p>
            </div>
        )
    }
    
    // Afficher l'écran de succès si l'inscription est réussie
    if (registrationSuccess) {
        return (
            <Card className="bg-dark text-light p-4">
                <Card.Body className="text-center">
                    <i className="bi bi-check-circle-fill text-success" style={{ fontSize: '3rem' }}></i>
                    <h3 className="mt-3">Registration successful!</h3>
                    
                    <Alert variant="success" className="mt-4">
                        <p className="mb-1">Your account has been successfully created.</p>
                        <p className="mb-0 mt-2">
                            <strong>Username:</strong> {playerName}
                        </p>
                    </Alert>
                    
                    <p className="mt-4">You can now log in with your username and password.</p>
                    
                    <Button 
                        variant="primary" 
                        size="lg" 
                        className="mt-3" 
                        onClick={() => navigate("/")}
                    >
                        Log in
                    </Button>
                </Card.Body>
            </Card>
        )
    }

    // N'afficher le formulaire que si le code a été traité avec succès
    if (!showPasswordForm) {
        return (
            <div className="text-center text-light">
                <h3>Invalid authentication session</h3>
                <p>Please try the registration process again.</p>
                <Button 
                    variant="primary" 
                    onClick={() => navigate('/register/42')}
                    className="mt-3"
                >
                    Back to registration
                </Button>
            </div>
        )
    }

    return (
        <Form className="text-light">
            <h3 className="text-center mb-3">Complete your registration</h3>
            
            <Alert variant="info" className="mb-4">
                You are authenticated with 42. Please choose a password to complete your account.
            </Alert>
            
            <Form.Group className="fs-5 fs-lg-4 mb-2 mb-lg-4">
                <Form.Label className="mb-2 text-light" htmlFor="password">Password</Form.Label>
                <div className="d-flex">
                    <Form.Control
                        type={passShow1 ? "text" : "password"}
                        value={password1}
                        placeholder="Choose a password"
                        onChange={(e) => setPassword1(e.target.value)}
                        className="rounded-0 rounded-start"
                        name="password"
                        id="password"
                        autoComplete="new-password"
                    />
                    <Button
                        type="button"
                        className="rounded-0 rounded-end btn btn-light"
                        aria-label="show"
                        onClick={passShow1 ? hidePass1 : showPass1}
                    >
                        {passShow1 ? <i className="eye bi-eye-fill"></i>
                                  : <i className="eye bi-eye-slash-fill"></i>}
                    </Button>
                </div>
                <div className="d-flex mt-2">
                    <Form.Control
                        type={passShow2 ? "text" : "password"}
                        value={password2}
                        placeholder="Confirm password"
                        onChange={(e) => setPassword2(e.target.value)}
                        className="rounded-0 rounded-start"
                        name="password2"
                        id="password2"
                        autoComplete="new-password"
                    />
                    <Button
                        type="button"
                        className="rounded-0 rounded-end btn btn-light"
                        aria-label="show"
                        onClick={passShow2 ? hidePass2 : showPass2}
                    >
                        {passShow2 ? <i className="eye bi-eye-fill"></i>
                                  : <i className="eye bi-eye-slash-fill"></i>}
                    </Button>
                </div>
            </Form.Group>
            
            <div className="d-flex justify-content-center pt-3 mb-3 mb-lg-5">
                <Button
                    type="submit"
                    className="btn btn-primary rounded fw-bolder"
                    onClick={completeAuth}
                    disabled={isLoading}
                >
                    {isLoading ? "PROCESSING..." : "COMPLETE REGISTRATION"}
                </Button>
            </div>
            
            <div className="d-flex justify-content-center mb-3">
                <Button
                    type="button"
                    variant="outline-light"
                    className="rounded"
                    onClick={() => navigate("/")}
                >
                    Cancel
                </Button>
            </div>
            <ErrorModal show={ show } hideModal={ hideModal } contextId={ 0 } info={ info } />
        </Form>
    )
}

export default Complete
