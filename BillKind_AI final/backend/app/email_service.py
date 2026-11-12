import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email.utils
import os
import re
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from backend or backend/app directory
backend_dir = Path(__file__).resolve().parent.parent
env_paths = [
    Path(__file__).resolve().parent / ".env",
    backend_dir / ".env",
    backend_dir.parent / ".env"
]
for p in env_paths:
    if p.exists():
        load_dotenv(p)
        break

def get_smtp_config():
    """Retrieve SMTP configuration from environment or settings file."""
    for p in env_paths:
        if p.exists():
            load_dotenv(p, override=True)
            break
    raw_pwd = os.getenv("SMTP_PASSWORD", "").strip()
    clean_pwd = re.sub(r"\s+", "", raw_pwd)
    return {
        "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.getenv("SMTP_PORT", "587")),
        "user": os.getenv("SMTP_USER", "").strip(),
        "password": clean_pwd,
        "from_name": os.getenv("SMTP_FROM_NAME", "BillKind AI Platform"),
    }

def update_smtp_config(user: str, password: str, host: str = "smtp.gmail.com", port: int = 587):
    """Save or update SMTP configuration in backend/.env file."""
    env_file = backend_dir / ".env"
    clean_user = user.strip()
    clean_pwd = re.sub(r"\s+", "", password.strip())
    content = f"""# BillKind AI SMTP Email Configuration
SMTP_HOST={host}
SMTP_PORT={port}
SMTP_USER={clean_user}
SMTP_PASSWORD={clean_pwd}
SMTP_FROM_NAME=BillKind AI Platform
"""
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(content)

    # Reload into current process environment
    os.environ["SMTP_HOST"] = host
    os.environ["SMTP_PORT"] = str(port)
    os.environ["SMTP_USER"] = clean_user
    os.environ["SMTP_PASSWORD"] = clean_pwd
    os.environ["SMTP_FROM_NAME"] = "BillKind AI Platform"

def is_smtp_configured() -> bool:
    cfg = get_smtp_config()
    return bool(cfg["user"] and cfg["password"])

def send_otp_email(recipient_email: str, recipient_name: str, otp_code: str) -> tuple[bool, str]:
    """
    Dispatches a real verification email via SMTP to recipient_email.
    Returns (True, message) on success, or (False, error_detail) on failure.
    """
    cfg = get_smtp_config()

    if not cfg["user"] or not cfg["password"]:
        return (
            False,
            "SMTP sender credentials are not configured. Please set SMTP_USER and SMTP_PASSWORD in backend/.env or configure via the BillKind AI email settings."
        )

    sender_email = cfg["user"]
    sender_name = cfg["from_name"]
    subject = f"{otp_code} is your BillKind AI Verification Code"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = recipient_email
    msg["Date"] = email.utils.formatdate(localtime=True)
    msg["Message-ID"] = email.utils.make_msgid(domain="billkind.ai")
    msg["X-Priority"] = "1 (Highest)"
    msg["Priority"] = "urgent"
    msg["Importance"] = "high"
    msg["Precedence"] = "immediate"
    msg["Auto-Submitted"] = "auto-generated"

    # Plain-text version
    text_content = f"""Hello {recipient_name},

Thank you for joining BillKind AI (AI-Powered Essential Bills Crowdfunding).

Your 6-digit email verification code is:

{otp_code}

This code will expire in 10 minutes.
If you did not request this verification code, please ignore this email.

Warm regards,
BillKind AI Verification Team
https://billkind.ai
"""

    # HTML formatted version
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>BillKind AI Verification Code</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 24px;">
  <div style="max-width: 560px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
    
    <!-- Header -->
    <div style="background: linear-gradient(135deg, #065f46, #0f766e); padding: 32px 28px; text-align: center; color: #ffffff;">
      <h1 style="margin: 0; font-size: 26px; font-weight: 800; letter-spacing: -0.5px;">BillKind AI</h1>
      <p style="margin: 6px 0 0; font-size: 13px; color: #a7f3d0; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Essential Bills Crowdfunding</p>
    </div>

    <!-- Body -->
    <div style="padding: 32px 28px; color: #1e293b;">
      <h2 style="margin: 0 0 12px; font-size: 18px; font-weight: 700; color: #0f172a;">Verify Your Email Address</h2>
      <p style="margin: 0 0 20px; font-size: 14px; line-height: 1.6; color: #475569;">
        Hello <strong>{recipient_name}</strong>,<br>
        Thank you for registering on BillKind AI. To complete your registration and secure your account, please enter the one-time verification code below:
      </p>

      <!-- OTP Box -->
      <div style="background-color: #ecfdf5; border: 2px dashed #059669; border-radius: 12px; padding: 20px; text-align: center; margin: 24px 0;">
        <span style="font-family: 'Courier New', Courier, monospace; font-size: 36px; font-weight: 800; letter-spacing: 8px; color: #065f46; display: inline-block;">
          {otp_code}
        </span>
        <p style="margin: 8px 0 0; font-size: 12px; color: #047857; font-weight: 500;">
          Valid for 10 minutes &bull; Do not share with anyone
        </p>
      </div>

      <p style="margin: 20px 0 0; font-size: 13px; color: #64748b; line-height: 1.5;">
        If you did not initiate this registration on BillKind AI, you can safely disregard this email.
      </p>
    </div>

    <!-- Footer -->
    <div style="background-color: #f1f5f9; padding: 18px 28px; text-align: center; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0;">
      &copy; 2026 BillKind AI Social Impact Platform. All rights reserved.<br>
      Automated system message &bull; Please do not reply directly to this email.
    </div>

  </div>
</body>
</html>
"""

    msg.attach(MIMEText(text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    clean_user = cfg["user"].strip()
    clean_pwd = cfg["password"].replace(" ", "").strip()

    try:
        # Connect to SMTP server (587 STARTTLS)
        server = smtplib.SMTP(cfg["host"], cfg["port"], timeout=15)
        server.ehlo()
        server.starttls()
        server.ehlo()
        
        # Try clean password, then lowercase if distinct
        try:
            server.login(clean_user, clean_pwd)
        except smtplib.SMTPAuthenticationError:
            if clean_pwd.lower() != clean_pwd:
                server.login(clean_user, clean_pwd.lower())
            else:
                raise
                
        server.send_message(msg)
        server.quit()
        print(f"[SMTP SUCCESS] Real verification email with OTP {otp_code} successfully delivered to {recipient_email}")
        return (True, f"Verification OTP email delivered to {recipient_email}")
    except smtplib.SMTPAuthenticationError as auth_err:
        err_msg = (
            f"Gmail Authentication Error: Google rejected credentials for '{clean_user}'. "
            "Please ensure 2-Step Verification is ON and a fresh 16-character App Password is generated at: https://myaccount.google.com/apppasswords"
        )
        print(f"[SMTP AUTH ERROR] {auth_err}")
        return (False, err_msg)
    except Exception as e:
        err_msg = f"Failed to send email via SMTP ({cfg['host']}:{cfg['port']}): {str(e)}"
        print(f"[SMTP ERROR] {err_msg}")
        return (False, err_msg)
