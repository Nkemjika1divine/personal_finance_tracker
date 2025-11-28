#!/usr/bin/python3
"""Module for functions for emails"""
import asyncio
import aiosmtplib
from os import environ
from dotenv import load_dotenv
from email.message import EmailMessage
import smtplib

load_dotenv()


async def send_welcome_email_to_user(recipient_email: str, display_name: str):
    message = EmailMessage()
    message["From"] = environ.get("MAIL_USERNAME")
    message["To"] = recipient_email
    message["Subject"] = "Welcome to Orbituwa"
    message.set_content(f"Hi {display_name}...\n\nWelcome to Orbituwa")

    try:
        await aiosmtplib.send(
            message,
            hostname=environ.get("MAIL_HOST"),
            port=environ.get("MAIL_PORT"),
            username=environ.get("MAIL_USERNAME"),
            password=environ.get("MAIL_PASSWORD"),
            start_tls=True,
        )
    except aiosmtplib.errors.SMTPConnectError as e:
        print(f"Connection Error: {e}")
    except aiosmtplib.errors.SMTPAuthenticationError as e:
        print(f"Authentication Error: {e}")
    except aiosmtplib.errors.SMTPRecipientRefused as e:
        print(f"Recipient's address was refused: {e.recipient}")
    except aiosmtplib.errors.SMTPException as e:
        print(f"General SMTP Error: {e}")
    except asyncio.TimeoutError:
        print("Timeout error while trying to send email")
    except Exception as e:
        print(f"Unexpected Error: {e}")


async def send_welcome_email_to_individual_beneficiary(
    recipient_email: str, display_name: str
):
    message = EmailMessage()
    message["From"] = environ.get("MAIL_USERNAME")
    message["To"] = recipient_email
    message["Subject"] = "Welcome to Anizoba Divine Foundation"
    message.set_content(
        f"Hi {display_name}...\n\nThis is to officially announce to you that you are now a beneficiary of the Anizoba Divine Foundation"
    )

    await aiosmtplib.send(
        message,
        hostname=environ.get("MAIL_HOST"),
        port=environ.get("MAIL_PORT"),
        username=environ.get("MAIL_USERNAME"),
        password=environ.get("MAIL_PASSWORD"),
        start_tls=True,
    )
