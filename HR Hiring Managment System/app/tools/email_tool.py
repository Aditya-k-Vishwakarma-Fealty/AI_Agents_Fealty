"""
Email tool for LangChain agents.
Provides Gmail API integration for sending and reading emails.
"""
from langchain.tools import Tool
from typing import List, Dict, Any, Optional
import json
import logging
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

from app.config.settings import settings

logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send', 
          'https://www.googleapis.com/auth/gmail.readonly']


class EmailTool:
    """Email operations wrapper for Gmail API."""
    
    def __init__(self):
        """Initialize Gmail API client."""
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API."""
        try:
            creds = None
            
            # Load existing token
            if os.path.exists(settings.gmail_token_file):
                creds = Credentials.from_authorized_user_file(settings.gmail_token_file, SCOPES)
            
            # Refresh or create new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        settings.gmail_credentials_file, SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save credentials
                with open(settings.gmail_token_file, 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail API authenticated successfully")
        except Exception as e:
            logger.error(f"Error authenticating Gmail API: {e}")
            raise
    
    def send_email(self, to: str, subject: str, body: str, is_html: bool = False) -> Dict[str, Any]:
        """
        Send email via Gmail API.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            is_html: Whether body is HTML
        
        Returns:
            Dict with status and message_id
        """
        try:
            message = MIMEMultipart()
            message['to'] = to
            message['from'] = settings.sender_email
            message['subject'] = subject
            
            if is_html:
                message.attach(MIMEText(body, 'html'))
            else:
                message.attach(MIMEText(body, 'plain'))
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f"Email sent to {to}, message_id: {sent_message['id']}")
            return {"status": "success", "message_id": sent_message['id']}
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {"status": "error", "message": str(e)}
    
    def send_shortlist_email(self, candidate_name: str, candidate_email: str, role_title: str) -> Dict[str, Any]:
        """
        Send shortlist notification email.
        
        Args:
            candidate_name: Candidate's name
            candidate_email: Candidate's email
            role_title: Role title
        
        Returns:
            Dict with status
        """
        subject = settings.email_shortlist_subject
        body = f"""Dear {candidate_name},

Congratulations! We are pleased to inform you that you have been shortlisted for the position of {role_title}.

We were impressed by your qualifications and experience, and we would like to proceed to the next stage of our hiring process.

Our team will reach out to you shortly to schedule a telephonic interview. Please confirm your availability by replying to this email with your preferred time slots for the coming week.

We look forward to speaking with you soon.

Best regards,
HR Team
"""
        
        return self.send_email(candidate_email, subject, body)
    
    def send_rejection_email(self, candidate_name: str, candidate_email: str, role_title: str) -> Dict[str, Any]:
        """
        Send rejection notification email.
        
        Args:
            candidate_name: Candidate's name
            candidate_email: Candidate's email
            role_title: Role title
        
        Returns:
            Dict with status
        """
        subject = settings.email_rejection_subject
        body = f"""Dear {candidate_name},

Thank you for your interest in the {role_title} position and for taking the time to apply.

After careful consideration of all applications, we regret to inform you that we will not be moving forward with your application at this time.

We were impressed by your background and encourage you to apply for future opportunities that match your skills and experience.

We wish you all the best in your job search.

Best regards,
HR Team
"""
        
        return self.send_email(candidate_email, subject, body)
    
    def send_interview_invite(self, candidate_name: str, candidate_email: str, 
                            role_title: str, interview_datetime: str) -> Dict[str, Any]:
        """
        Send interview invitation email.
        
        Args:
            candidate_name: Candidate's name
            candidate_email: Candidate's email
            role_title: Role title
            interview_datetime: Interview date and time
        
        Returns:
            Dict with status
        """
        subject = settings.email_interview_subject
        body = f"""Dear {candidate_name},

We are pleased to invite you for a telephonic interview for the position of {role_title}.

Interview Details:
Date & Time: {interview_datetime}

Please confirm your availability by replying to this email. If the proposed time doesn't work for you, please suggest alternative time slots.

We look forward to speaking with you.

Best regards,
HR Team
"""
        
        return self.send_email(candidate_email, subject, body)
    
    def read_replies(self, candidate_email: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Read email replies from a candidate.
        
        Args:
            candidate_email: Candidate's email to filter by
            max_results: Maximum number of emails to retrieve
        
        Returns:
            Dict with list of email messages
        """
        try:
            query = f"from:{candidate_email}"
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            email_list = []
            for msg in messages:
                msg_data = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                # Extract email body
                payload = msg_data.get('payload', {})
                body = ""
                
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/plain':
                            body = base64.urlsafe_b64decode(part['body']['data']).decode()
                            break
                elif 'body' in payload and 'data' in payload['body']:
                    body = base64.urlsafe_b64decode(payload['body']['data']).decode()
                
                email_list.append({
                    "message_id": msg['id'],
                    "body": body,
                    "snippet": msg_data.get('snippet', '')
                })
            
            logger.info(f"Retrieved {len(email_list)} emails from {candidate_email}")
            return {"status": "success", "emails": email_list}
        except Exception as e:
            logger.error(f"Error reading emails: {e}")
            return {"status": "error", "message": str(e)}


def create_email_tools() -> List[Tool]:
    """
    Create LangChain tools for email operations.
    
    Returns:
        List of LangChain Tool objects
    """
    email_tool = EmailTool()
    
    tools = [
        Tool(
            name="send_shortlist_email",
            func=lambda data: email_tool.send_shortlist_email(**json.loads(data) if isinstance(data, str) else data),
            description="Send shortlist notification email. Input should be JSON with: candidate_name, candidate_email, role_title"
        ),
        Tool(
            name="send_rejection_email",
            func=lambda data: email_tool.send_rejection_email(**json.loads(data) if isinstance(data, str) else data),
            description="Send rejection notification email. Input should be JSON with: candidate_name, candidate_email, role_title"
        ),
        Tool(
            name="send_interview_invite",
            func=lambda data: email_tool.send_interview_invite(**json.loads(data) if isinstance(data, str) else data),
            description="Send interview invitation email. Input should be JSON with: candidate_name, candidate_email, role_title, interview_datetime"
        ),
        Tool(
            name="read_candidate_replies",
            func=lambda data: email_tool.read_replies(**json.loads(data) if isinstance(data, str) else data),
            description="Read email replies from candidate. Input should be JSON with: candidate_email, max_results (optional)"
        )
    ]
    
    return tools
