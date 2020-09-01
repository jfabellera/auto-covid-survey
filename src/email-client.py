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

mailboxes = [yes_mail, no_mail]
labels = ["YES", "NO"]
read_emails_files = ["read_emails_yes.dat", "read_emails_no.dat"]
mailbox_selector = 0

while True:
    print(f"syncing {labels[mailbox_selector]} mailbox...")

    mailboxes[mailbox_selector].select("INBOX")

    # get uid's of already read emails
    with open(read_emails_files[mailbox_selector], "rb") as fp:
        read_emails = pickle.load(fp)

    result, data = mailboxes[mailbox_selector].uid("search", None, "ALL")
    inbox_item_list = data[0].split()

    # determine uid's of unread emails by doing set difference
    unread_emails = list(set(inbox_item_list) - set(read_emails))
    if len(unread_emails) > 0:
        print(f"{len(unread_emails)} new email(s)")

    # go through the new emails
    for uid in unread_emails:
        result2, email_data = mailboxes[mailbox_selector].uid("fetch", uid, "(RFC822)")
        raw_email = email_data[0][1].decode("utf-8")
        email_message = email.message_from_string(raw_email)
        sender = email_message["From"]
        survey_url = None

        print(f"Reading email from {sender} in {labels[mailbox_selector]} mailbox...")

        if "utdallas.edu" in sender.lower():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if "plain" in content_type:
                    survey_url = get_url(part.get_payload())

        # fill out survey if valid
        script_result = 1
        if survey_url is not None:
            command = f"python fill-survey.py -u {survey_url}"
            if mailbox_selector == 1:
                command += " -n"
            script_result = os.system(command)
        else:
            # TODO email sender that it is not a valid email or something like that
            pass

        # status stuff
        if script_result < 0:
            print("There was a problem submitting the survey.")
        elif script_result > 0:
            print("There was no survey to submit.")
        else:
            print(f"Survey submitted successfully with {labels[mailbox_selector]} to being on campus.")

        # update read emails
        read_emails.append(uid)

    with open(read_emails_files[mailbox_selector], "wb") as fp:
        pickle.dump(read_emails, fp)

    mailbox_selector = (mailbox_selector + 1) % 2
    time.sleep(30)
