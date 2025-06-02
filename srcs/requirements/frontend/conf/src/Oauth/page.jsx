// Oauth/page.jsx
import React from "react"
import Background from "../background/background.jsx"
import OauthRegister from "./oauth.jsx"  // Correction de la casse ici

function OauthPage() {
    return (
        <>
            <header>
                <div className="container position-relative">
                    <h1 className="position-relative text-center text-light fw-bolder z-3 p-5 user-select-none" 
                        style={{textShadow: "3px 3px 5px rgba(0, 0, 0, 0.7)", fontSize: '6rem'}}>
                            Pong.
                    </h1>
                </div>
            </header>
            <main>
                <Background type={"public"} />
                <div className="position-absolute top-0 d-flex justify-content-center align-items-center vh-100 w-100">
                    <div className="rounded border border-black border-2 px-3 px-lg-5 pt-2 pt-lg-4 pb-3 pb-lg-4"
                        style={{background: "rgba(0, 0, 0, 0.7)"}}>
                        <OauthRegister />
                    </div>
                </div>
            </main>
        </>
    )
}

export default OauthPage
