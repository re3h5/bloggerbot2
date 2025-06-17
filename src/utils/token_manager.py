"""
Token management utilities for OAuth authentication with Google APIs.
"""
import os
import json
import logging
import time
import socket
import psutil
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.utils.config import CREDENTIALS_PATH, TOKEN_PATH, BLOGGER_ID

def get_blogger_token():
    """
    Get or refresh the OAuth token for Blogger API.
    Returns the credentials object.
    """
    creds = None
    scopes = ['https://www.googleapis.com/auth/blogger']
    
    # Check if token file exists
    if os.path.exists(TOKEN_PATH):
        try:
            with open(TOKEN_PATH, 'r') as token_file:
                token_data = json.load(token_file)
                creds = Credentials.from_authorized_user_info(token_data, scopes)
        except Exception as e:
            logging.error(f"Error loading token: {str(e)}")
    
    # If no valid credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logging.info("Token refreshed successfully")
            except Exception as e:
                logging.error(f"Error refreshing token: {str(e)}")
                creds = None
        
        # If still no valid credentials, need to get new ones
        if not creds:
            if not os.path.exists(CREDENTIALS_PATH):
                logging.error(f"Credentials file not found at {CREDENTIALS_PATH}")
                return None
            
            # Find an available port for the local server
            port = find_available_port()
            if not port:
                logging.error("Could not find an available port")
                return None
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH, 
                    scopes,
                    redirect_uri=f'http://localhost:{port}'
                )
                creds = flow.run_local_server(port=port)
                logging.info("New token obtained successfully")
            except Exception as e:
                logging.error(f"Error in authentication flow: {str(e)}")
                return None
    
    # Save the credentials for the next run
    try:
        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())
        logging.info(f"Token saved to {TOKEN_PATH}")
    except Exception as e:
        logging.error(f"Error saving token: {str(e)}")
    
    # Verify token works by making a test API call
    try:
        service = build('blogger', 'v3', credentials=creds)
        blog = service.blogs().get(blogId=BLOGGER_ID).execute()
        logging.info(f"Successfully authenticated to blog: {blog.get('name', 'Unknown')}")
    except HttpError as e:
        if e.status_code == 401:
            logging.error("Authentication failed: Invalid credentials")
            # Remove invalid token
            if os.path.exists(TOKEN_PATH):
                os.remove(TOKEN_PATH)
            return None
        elif e.status_code == 403:
            logging.error("Permission denied: Check your OAuth scopes and Blogger ID")
            return None
        else:
            logging.error(f"API error: {str(e)}")
            return None
    except Exception as e:
        logging.error(f"Error verifying token: {str(e)}")
        return None
    
    return creds

def find_available_port(start=8080, end=8180):
    """Find an available port in the given range."""
    for port in range(start, end):
        if is_port_available(port):
            return port
    return None

def is_port_available(port):
    """Check if a port is available."""
    # Check if port is in use by any process
    for conn in psutil.net_connections():
        if conn.laddr.port == port:
            return False
    
    # Double-check with a socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except socket.error:
            return False
