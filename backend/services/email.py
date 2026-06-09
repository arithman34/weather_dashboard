import resend

from backend.config import settings

resend.api_key = settings.resend_api_key


def send_email(username: str, email: str) -> None:
    """Send a welcome email to a new user."""
    resend.Emails.send(
        {
            "from": settings.from_email,
            "to": email,
            "subject": "Welcome to Weather Dashboard!",
            "html": f"""
                    <html>
                        <body>
                            <h1>Welcome, {username}!</h1>
                            <p>Thank you for signing up for Weather Dashboard. We're excited to have you on board!</p>
                            <p>With Weather Dashboard, you can easily track the weather in your favorite locations and stay informed about the latest conditions.</p>
                            <p>If you have any questions or need assistance, feel free to reach out to our support team.</p>
                            <p>Best regards,<br/>The Weather Dashboard Team</p>
                        </body>
                    </html>
                    """,
        }
    )
