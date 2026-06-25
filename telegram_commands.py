from pause import (
    pause,
    resume,
    status
)

def handle_command(text):

    if text == "/pause":

        pause()

        return (
            "⏸ Notifications paused"
        )

    if text == "/resume":

        resume()

        return (
            "▶ Notifications resumed"
        )

    if text == "/status":

        return (
            f"Current status: {status()}"
        )

    return None 