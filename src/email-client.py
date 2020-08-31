import imaplib
import os
import email
import time

# retrieve login credentials for emails
yes_user = os.environ["YES_USER"]
yes_pass = os.environ["YES_PASS"]
no_user = os.environ["NO_USER"]
no_pass = os.environ["NO_PASS"]

# authenticate accounts
yes_mail = imaplib.IMAP4_SSL("imap.gmail.com")
yes_mail.login(yes_user, yes_pass)
no_mail = imaplib.IMAP4_SSL("imap.gmail.com")
no_mail.login(no_user, no_pass)

yes_mail.select("INBOX")

result, data = yes_mail.uid("search", None, "ALL")
inbox_item_list = data[0].split()

latest = inbox_item_list[-1]
result2, email_data = yes_mail.uid("fetch", latest, "(RFC822)")
raw_email = email_data[0][1].decode("utf-8")
email_message = email.message_from_string(raw_email)

print(email_message["From"])