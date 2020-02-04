"""
Fetch mails from mailbox, extract first xliff target and
push to CMS via push content API.
"""
import requests
from lxml import etree
from imapclient import IMAPClient  # pylint: disable=E0401

XLIFFNS = 'urn:oasis:names:tc:xliff:document:1.2'
TOKEN = ''
IMAP_HOST = ''
IMAP_USER = ''
IMAP_PASS = ''


def parse_xliff(file_name):
    """
    Parse xliff file provided as paramter, extract first target and target
    language
    """
    tree = etree.parse(file_name)
    target_text = tree.xpath('.//xliffns:target',
                             namespaces={'xliffns': XLIFFNS})[1].text
    language = ""
    return (target_text, language)


def push_to_cms(content, language):
    """
    Upload content to CMS via push content API
    """
    payload = {'page_id': 1903,
               'content': content,
               "token": TOKEN}
    url = ("https://cms.integreat-app.de/testumgebung/" +
           "{}/wp-json/extensions/v3/pushpage").format(language)

    requests.post(url, data=payload)


def fetch_latest_mail():
    """
    Fetch unread mail from IMAP.
    """
    server = IMAPClient(IMAP_HOST, use_uid=True)
    server.login(IMAP_USER, IMAP_PASS)
    select_info = server.select_folder('INBOX')
    print('%d messages in INBOX' % select_info[b'EXISTS'])
    messages = server.search(['FROM', 'best-friend@domain.com'])
    print("%d messages from our best friend" % len(messages))
    for msgid, data in server.fetch(messages, ['ENVELOPE']).items():
        envelope = data[b'ENVELOPE']
        print('ID #%d: "%s" received %s' % (msgid, envelope.subject.decode(),
                                            envelope.date))
    server.logout()
