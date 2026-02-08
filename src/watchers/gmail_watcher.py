# gmail_watcher.py
import sys
from pathlib import Path
import time
import logging
from datetime import datetime
import base64
import re
from html import unescape

# Add the parent directory to the path to import base_watcher
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_watcher import BaseWatcher

# Import Google API libraries with error handling
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google.auth.exceptions import RefreshError
except ImportError as e:
    print(f"Google API libraries not installed. Please install: pip install google-api-python-client google-auth")
    raise e

class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path: str, credentials_path: str, check_interval: int = 10):
        super().__init__(vault_path, check_interval)
        # Create the Inbox directory if it doesn't exist
        self.inbox.mkdir(exist_ok=True)

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Load credentials and build service
        try:
            credentials_path_obj = Path(credentials_path)
            self.creds = Credentials.from_authorized_user_file(str(credentials_path_obj))
            self.service = build('gmail', 'v1', credentials=self.creds)
        except FileNotFoundError:
            self.logger.error(f"Credentials file not found: {credentials_path}")
            raise
        except RefreshError:
            self.logger.error("Credentials have expired or are invalid. Please re-authenticate.")
            raise

        # Track processed email IDs to prevent duplicates
        self.processed_ids_file = Path(__file__).parent / '.gmail_processed_ids'
        self.processed_ids = self._load_processed_ids()

    def check_for_updates(self) -> list:
        """Check for all new unread emails"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread'
                # No maxResults limit to fetch all unread emails
            ).execute()

            messages = results.get('messages', [])
            new_messages = []

            for message in messages:
                if message['id'] not in self.processed_ids:
                    # Get full message details to check if it's really new
                    msg_details = self.service.users().messages().get(
                        userId='me',
                        id=message['id'],
                        format='full'  # Use full format to get headers
                    ).execute()

                    # Add to new messages if it passes all checks
                    new_messages.append({
                        'id': message['id'],
                        'details': msg_details
                    })

            self.logger.info(f"Found {len(new_messages)} new unread emails")
            return new_messages

        except Exception as e:
            self.logger.error(f"Error checking for email updates: {e}")
            return []

    def create_action_file(self, message_data) -> Path:
        """Create markdown file in Inbox with YAML frontmatter"""
        try:
            message_id = message_data['id']
            msg = message_data['details']

            # Extract headers
            headers = {}
            if 'payload' in msg and 'headers' in msg['payload']:
                headers = {h['name']: h['value'] for h in msg['payload']['headers']}

            # Extract full email body
            full_body = self._extract_full_email_body(msg)

            # Determine priority based on full content
            priority = self._determine_priority(headers, full_body)

            # Create markdown content with YAML frontmatter
            content = f"""---
type: email
from: {headers.get('From', 'Unknown').replace(':', ';').strip()}
subject: {headers.get('Subject', 'No Subject').replace(':', ';').strip()}
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
---

## Email Content
{full_body}

## Suggested Actions
- [ ] Review content and determine appropriate response
- [ ] Take necessary action based on email content
- [ ] Archive or mark as read after processing
"""

            # Create filename with email ID to ensure uniqueness
            filename = f"EMAIL_{message_id}.md"
            filepath = self.inbox / filename

            # Write content to file
            filepath.write_text(content, encoding='utf-8')

            # Add to processed IDs to prevent duplicate processing
            self.processed_ids.add(message_id)
            self._save_processed_ids()

            self.logger.info(f"Created action file: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"Error creating action file for message {message_data.get('id', 'unknown')}: {e}")
            raise

    def _determine_priority(self, headers: dict, snippet: str) -> str:
        """Determine email priority based on content"""
        subject = headers.get('Subject', '').lower()
        sender = headers.get('From', '').lower()
        snippet_lower = snippet.lower()

        # Check for high priority indicators
        high_priority_keywords = [
            'urgent', 'asap', 'important', 'deadline', 'invoice',
            'payment', 'money', 'billing', 'due', 'critical'
        ]

        # Combine all text for keyword checking
        all_text = f"{subject} {sender} {snippet_lower}"

        for keyword in high_priority_keywords:
            if keyword in all_text:
                return 'high'

        return 'normal'

    def _extract_full_email_body(self, msg):
        """Extract full email body from the message, ensuring only plain text is returned without HTML"""
        try:
            # Check if the message has a payload
            if 'payload' not in msg:
                cleaned_content = self._ensure_plain_text(msg.get('snippet', 'No content available'))
                # Return empty string if content is only HTML with no meaningful text
                if self._is_html_only(cleaned_content):
                    return ""
                return cleaned_content

            payload = msg['payload']

            # Check if the payload has parts (multipart email)
            if 'parts' in payload:
                # Handle multipart emails
                parts = payload['parts']

                # First, try to find plain text parts (excluding images and attachments)
                for part in parts:
                    mime_type = part.get('mimeType', '')

                    # Skip image parts and other attachment types
                    if mime_type.startswith('image/'):
                        continue

                    # Process plain text parts
                    if mime_type == 'text/plain':
                        body_data = part.get('body', {}).get('data')
                        if body_data:
                            decoded_bytes = base64.urlsafe_b64decode(body_data)
                            text_content = decoded_bytes.decode('utf-8')
                            cleaned_content = self._ensure_plain_text(text_content)
                            # Return empty string if content is only HTML with no meaningful text
                            if self._is_html_only(cleaned_content):
                                return ""
                            return cleaned_content

                # If no plain text found, try HTML parts (convert to plain text)
                for part in parts:
                    mime_type = part.get('mimeType', '')

                    # Skip image parts and other attachment types
                    if mime_type.startswith('image/'):
                        continue

                    if mime_type == 'text/html':
                        body_data = part.get('body', {}).get('data')
                        if body_data:
                            decoded_bytes = base64.urlsafe_b64decode(body_data)
                            html_content = decoded_bytes.decode('utf-8')

                            # Ensure HTML is converted to plain text
                            plain_text = self._html_to_plain_text(html_content)
                            cleaned_content = self._ensure_plain_text(plain_text)
                            # Return empty string if content is only HTML with no meaningful text
                            if self._is_html_only(cleaned_content):
                                return ""
                            return cleaned_content

            # If no parts, try to get the body directly from the payload
            elif 'body' in payload and 'data' in payload['body']:
                body_data = payload['body']['data']
                decoded_bytes = base64.urlsafe_b64decode(body_data)
                text_content = decoded_bytes.decode('utf-8')
                cleaned_content = self._ensure_plain_text(text_content)
                # Return empty string if content is only HTML with no meaningful text
                if self._is_html_only(cleaned_content):
                    return ""
                return cleaned_content

            # Fallback to snippet if no body found
            cleaned_content = self._ensure_plain_text(msg.get('snippet', 'No content available'))
            # Return empty string if content is only HTML with no meaningful text
            if self._is_html_only(cleaned_content):
                return ""
            return cleaned_content

        except Exception as e:
            self.logger.error(f"Error extracting email body: {e}")
            # Fallback to cleaned snippet if extraction fails
            cleaned_content = self._ensure_plain_text(msg.get('snippet', 'Content extraction failed, no content available'))
            # Return empty string if content is only HTML with no meaningful text
            if self._is_html_only(cleaned_content):
                return ""
            return cleaned_content

    def _html_to_plain_text(self, html_content: str) -> str:
        """Convert HTML content to plain text using multiple methods to ensure no HTML remains"""
        if not html_content:
            return ""

        # First, unescape HTML entities
        text = unescape(html_content)

        # Use multiple regex patterns to remove various HTML elements
        # Remove script and style elements and their content
        text = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', text, flags=re.DOTALL | re.IGNORECASE)

        # Remove HTML comments
        text = re.sub(r'<!--.*?-->', ' ', text, flags=re.DOTALL)

        # Remove HTML tags (more comprehensive pattern)
        text = re.sub(r'<[^>]*>', ' ', text)

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        return text

    def _ensure_plain_text(self, text: str) -> str:
        """Ensure the text is plain text by removing any remaining HTML-like content"""
        if not text:
            return ""

        # Apply the same cleaning as before
        cleaned = self._clean_text(text)

        # Additional check to ensure no HTML-like content remains
        # Remove any remaining HTML-like patterns (e.g., &nbsp;, &amp;, etc.)
        # But ensure we don't remove legitimate content

        # Remove common HTML entities while preserving their meaning
        entity_map = {
            '&nbsp;': ' ',
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
        }

        for entity, replacement in entity_map.items():
            cleaned = cleaned.replace(entity, replacement)

        # Final cleanup to ensure it's plain text
        return self._clean_text(cleaned)

    def _is_html_only(self, text: str) -> bool:
        """Check if the text is essentially just HTML with no meaningful content"""
        if not text or text.isspace():
            return True

        # Strip out common HTML remnants and check if there's meaningful content
        stripped = re.sub(r'\s+', ' ', text).strip()

        # If text is too short after cleaning, it might be just HTML artifacts
        if len(stripped) < 5:
            return True

        # Check if the remaining text is mostly just HTML formatting remnants
        words = stripped.split()
        if len(words) == 0:
            return True

        # If it's just HTML tags and spaces, return True
        if re.match(r'^[<>\s\/=\-"\'\[\]]*$', stripped):
            return True

        return False

    def _clean_text(self, text: str) -> str:
        """Clean up text by removing links, extra whitespace and normalizing spaces"""
        if not text:
            return ""

        # Remove HTML entities and convert them to proper characters
        text = unescape(text)

        # Remove URLs/links from the text
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

        # Replace multiple whitespace characters (spaces, tabs, newlines) with single spaces
        text = re.sub(r'\s+', ' ', text)

        # Remove leading/trailing whitespace
        text = text.strip()

        # Normalize line breaks to single newlines for readability
        text = re.sub(r'[ \t]*\n[ \t]*', '\n', text)

        return text

    def _load_processed_ids(self):
        """Load processed email IDs from file to prevent duplicate processing across runs"""
        if self.processed_ids_file.exists():
            try:
                content = self.processed_ids_file.read_text(encoding='utf-8').strip()
                if content:
                    return set(content.splitlines())
                else:
                    return set()
            except Exception as e:
                self.logger.error(f"Error loading processed IDs: {e}")
                return set()
        return set()

    def _save_processed_ids(self):
        """Save processed email IDs to file"""
        try:
            self.processed_ids_file.write_text('\n'.join(sorted(self.processed_ids)), encoding='utf-8')
        except Exception as e:
            self.logger.error(f"Error saving processed IDs: {e}")

    def run(self):
        """Override run method with better error handling"""
        self.logger.info(f'Starting {self.__class__.__name__}')
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    self.create_action_file(item)
            except KeyboardInterrupt:
                self.logger.info("Gmail Watcher stopped by user")
                break
            except Exception as e:
                self.logger.error(f'Unexpected error in {self.__class__.__name__}: {e}')
                # Wait before retrying to avoid rapid error loops
                time.sleep(self.check_interval)

            # Sleep for the check interval before next check
            time.sleep(self.check_interval)


if __name__ == "__main__":
    # Example usage - adjust paths as needed
    # When running from project root: python -m src.watchers.gmail_watcher
    VAULT_PATH = "./AI_Employee_Vault"  # Use the dedicated vault directory
    CREDENTIALS_PATH = "token.json"  # Path to Gmail API authorized user credentials

    try:
        watcher = GmailWatcher(VAULT_PATH, CREDENTIALS_PATH)
        watcher.run()
    except Exception as e:
        print(f"Failed to start Gmail Watcher: {e}")
        print("Make sure you have valid Gmail API credentials in token.json")