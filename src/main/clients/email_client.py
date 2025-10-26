import os
import aiohttp
from exceptions import EmailSendError, EmailConfigurationError


class EmailClient:
    def __init__(self):
        self.api_token = os.getenv("MAILTRAP_API_TOKEN")
        self.from_email = os.getenv("EMAIL_FROM_ADDRESS", "hello@basedagent.io")
        self.from_name = os.getenv("EMAIL_FROM_NAME", "ChatPlatform")
        self.api_url = "https://send.api.mailtrap.io/api/send"

    def _validate_config(self):
        if not self.api_token:
            raise EmailConfigurationError("MAILTRAP_API_TOKEN is required")
        if not self.from_email:
            raise EmailConfigurationError("EMAIL_FROM_ADDRESS is required")

    async def send_email(self,
                         to_email: str,
                         subject: str,
                         html: str,
                         category: str) -> bool:
        try:
            self._validate_config()

            payload = {
                "from": {
                    "email": self.from_email,
                    "name": self.from_name
                },
                "to": [
                    {
                        "email": to_email
                    }
                ],
                "subject": subject,
                "category": category,
                "html": html
            }

            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json"
                }

                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:

                    if response.status == 200:
                        result = await response.json()
                        return result.get("success", True)
                    else:
                        error_text = await response.text()
                        raise EmailSendError(f"Mailtrap API error {response.status}: {error_text}")

        except aiohttp.ClientError as e:
            raise EmailSendError(f"Network error sending email to {to_email}: {str(e)}")
        except Exception as e:
            raise EmailSendError(f"Failed to send email to {to_email}: {str(e)}")

    async def send_verification_code(self, to_email: str, code: str) -> bool:
        subject = "BasedAgent Verification Code"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Verification Code</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px; text-align: center;">
                <h2 style="color: #333; margin-bottom: 20px;">Verification Code</h2>
                <div style="background-color: #007bff; color: white; font-size: 24px; font-weight: bold; 
                           padding: 15px; border-radius: 5px; margin: 20px 0; letter-spacing: 3px;">
                    {code}
                </div>
                <p style="color: #666; margin-bottom: 20px;">
                    This code is valid for <strong>5 minutes</strong>.
                </p>
                <p style="color: #999; font-size: 14px;">
                    If you didn't request this code, please ignore this message.
                </p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #999; font-size: 12px;">
                    Best regards,<br>
                    BasedAgent Team
                </p>
            </div>
        </body>
        </html>
        """

        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html=html_content,
            category="Verification Code"
        )



