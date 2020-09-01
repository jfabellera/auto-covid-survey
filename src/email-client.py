import imaplib
import os
import email
import quopri
import pickle
import time


def get_url(payload):
    # get rid of 3D in the url which is introduced for some reason
    payload = str(quopri.decodestring(payload))

    url = payload[payload.rfind('<') + 1:payload.rfind('>')]
    if "redcap" in url:
        return url
    return None


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

while True:
    print("syncing...")

    yes_mail.select("INBOX")

    # get uid's of already read emails
    with open("read_emails.dat", "rb") as fp:
        read_emails = pickle.load(fp)

    result, data = yes_mail.uid("search", None, "ALL")
    inbox_item_list = data[0].split()

    # determine uid's of unread emails by doing set difference
    unread_emails = list(set(inbox_item_list) - set(read_emails))
    if len(unread_emails) > 0:
        print(f"{len(unread_emails)} new email(s)")

    # go through the new emails
    for uid in unread_emails:
        result2, email_data = yes_mail.uid("fetch", uid, "(RFC822)")
        raw_email = email_data[0][1].decode("utf-8")
        email_message = email.message_from_string(raw_email)
        sender = email_message["From"]
        survey_url = None
        if "utdallas.edu" in sender.lower():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if "plain" in content_type:
                    survey_url = get_url(part.get_payload())

        # fill out survey if valid
        if survey_url is not None:
            os.system(f"python fill-survey.py -u {survey_url}")
        else:
            # email sender that it is not a valid email or something like that
            pass

        # update read emails
        read_emails.append(uid)

    with open("read_emails.dat", "wb") as fp:
        pickle.dump(read_emails, fp)

    time.sleep(5)
