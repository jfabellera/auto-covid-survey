import imaplib
import smtplib
import os
import email
import quopri
import pickle
import time


def get_url(payload):
    # get rid of 3D in the url which is introduced for some reason
    # payload = str(quopri.decodestring(payload))

    url = payload[payload.rfind('<') + 1:payload.rfind('>')]
    if "redcap" in url:
        return url
    return None


def send_email(subject, msg, recipient, user, password):
    try:
        server = smtplib.SMTP("smtp.gmail.com:587")
        server.ehlo()
        server.starttls()
        server.login(user, password)
        message = f"Subject: {subject}\n\n{msg}"
        server.sendmail(user, recipient, message)
        server.quit()
        print("Email successfully sent.")
    except:
        print("Email failed to send.")


# retrieve login credentials for emails
yes_user = os.environ["YES_USER"]
yes_pass = os.environ["YES_PASS"]
no_user = os.environ["NO_USER"]
no_pass = os.environ["NO_PASS"]

# authenticate accounts
# yes_mail = imaplib.IMAP4_SSL("imap.gmail.com")
# yes_mail.login(yes_user, yes_pass)
# no_mail = imaplib.IMAP4_SSL("imap.gmail.com")
# no_mail.login(no_user, no_pass)

labels = ["YES", "NO"]
usernames = [yes_user, no_user]
passwords = [yes_pass, no_pass]
read_emails_files = ["read_emails_yes.dat", "read_emails_no.dat"]
mailbox_selector = 0

while True:
    mailbox = imaplib.IMAP4_SSL("imap.gmail.com")
    mailbox.login(usernames[mailbox_selector], passwords[mailbox_selector])
    print(f"syncing {labels[mailbox_selector]} mailbox...")

    mailbox.select("INBOX")

    # get uid's of already read emails
    with open(read_emails_files[mailbox_selector], "rb") as fp:
        read_emails = pickle.load(fp)

    result, data = mailbox.uid("search", None, "ALL")
    inbox_item_list = data[0].split()

    # determine uid's of unread emails by doing set difference
    unread_emails = list(set(inbox_item_list) - set(read_emails))
    if len(unread_emails) > 0:
        print(f"{len(unread_emails)} new email(s)")

    # go through the new emails
    for uid in unread_emails:
        result2, email_data = mailbox.uid("fetch", uid, "(RFC822)")
        raw_email = email_data[0][1].decode('utf-8')
        email_message = email.message_from_string(raw_email)
        sender = email_message["From"]
        sender_email = sender[sender.rfind('<') + 1: sender.rfind('>')]
        survey_url = None

        print(f"Reading email from {sender} in {labels[mailbox_selector]} mailbox...")

        if "utdallas.edu" in sender.lower():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if "plain" in content_type:
                    survey_url = get_url(part.get_payload(decode=True).decode('utf-8'))

        # fill out survey if valid
        script_result = 1
        if survey_url is not None:
            command = f"python fill-survey.py -u {survey_url}"
            if mailbox_selector == 1:
                command += " -n"
            script_result = os.system(command)

        # status stuff
        msg = f"Survey submitted successfully with {labels[mailbox_selector]} to being on campus." \
              f"\n\nSurvey: {survey_url}"
        if script_result < 0:
            msg = f"There was a problem submitting the following survey:\n\n{survey_url}"
        elif script_result > 0:
            msg = "There was no survey to submit."
        print(msg)
        send_email("Survey Status", msg, sender_email, usernames[mailbox_selector], passwords[mailbox_selector])

        # update read emails
        read_emails.append(uid)

    with open(read_emails_files[mailbox_selector], "wb") as fp:
        pickle.dump(read_emails, fp)

    mailbox.logout()
    mailbox_selector = (mailbox_selector + 1) % 2
    time.sleep(5)
