import { updateScore, updateName } from './shapes'

const createAnimate = (stateRef, objects, MessageRef, rendererRef, scene, camera, setGroupScore, setGroupName, groupScoreRef, groupNameRef) => {
    
	let animationFrameId

    const animate = () => {
        if (stateRef.current === "play" && objects && objects.paddle?.paddleL && objects.paddle?.paddleR && objects.ball) {
            const lastPongMessage = MessageRef.current
            if (lastPongMessage && lastPongMessage.type == "data_pong") {
                objects.paddle.paddleL.position.set(0.5, lastPongMessage.paddleL + 2.5, 1)
                objects.paddle.paddleR.position.set(70.5, lastPongMessage.paddleR + 2.5, 1)
                objects.ball.position.set(lastPongMessage.x + 0.5, lastPongMessage.y + 0.5, 1)

				const currentScore = groupScoreRef.current

                if ((lastPongMessage.scorePlayer1 !== currentScore.score1) || (lastPongMessage.scorePlayer2 !== currentScore.score2)) {
                    const newScore = { score1: lastPongMessage.scorePlayer1, score2: lastPongMessage.scorePlayer2 }
                    updateScore(newScore, scene, objects)
                    setGroupScore(newScore)
                }

				const currentName = groupNameRef.current

                if ((lastPongMessage.Player1_name !== currentName.name1) || (lastPongMessage.Player2_name !== currentName.name2)) {
                    const newName = { name1: lastPongMessage.Player1_name, name2: lastPongMessage.Player2_name }
                    updateName(newName, scene, objects)
                    setGroupName(newName)
                }
            }
        }
		rendererRef.current.render(scene, camera)
        animationFrameId = requestAnimationFrame(animate)
    }

    animate()

    return { animationFrameId }
}

export default createAnimate
