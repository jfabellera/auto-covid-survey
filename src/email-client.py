import imaplib
import os
import email
import quopri
import pickle


def get_url(payload):
    # get rid of 3D in the url which is introduced for some reason
    payload = str(quopri.decodestring(payload))

    url = payload[payload.rfind('<') + 1:payload.rfind('>')]
    if "redcap" in url:
        return url
    return None


# get uid's of already read emails
with open("read_emails.dat", "rb") as fp:
    read_emails = pickle.load(fp)

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

sender = email_message["From"]
survey_url = ""

for part in email_message.walk():
    content_type = part.get_content_type()
    if "plain" in content_type:
        survey_url = get_url(part.get_payload())

if survey_url is not None:
    os.system(f"python fill-survey.py -u {survey_url}")
else:
    # email sender that it is not a valid email
    pass

