from perceval.backends.pipermail import Pipermail
from perceval.backends.mbox import MBox, MBoxArchive
from playhouse.sqlite_ext import SqliteExtDatabase
from dbo import *
from optparse import OptionParser
import sys
import json 
from dateutil import parser as date_parser

try:
    usage = "Usage: %prog [options] -u uri-to-email-archieve -n folder-name -d database-name -b pipermail or mbox"
    option_parser = OptionParser(usage=usage)
    option_parser.add_option("-u", "--uri", metavar="URI", help="URI to archieve"),
    option_parser.add_option("-n", "--name", metavar="NAME", help="Name of the folder"),
    option_parser.add_option("-d", "--database", metavar="DB", help="Name of the database"),
    option_parser.add_option("-b", "--backend", metavar="BACKEND", help="Name of the backend"),

    (options, args) = option_parser.parse_args()

    if not options.uri or not options.name or not options.database or not options.backend:
        print (usage)
        sys.exit()

    database = SqliteExtDatabase('%s.db' % options.database)
    database_proxy.initialize(database)
    database.connect()
    database.create_tables([EmailDBO], safe=True)

    print('Extracting information from %s to %s.db...' % (options.uri, options.database))

    if options.backend == 'pipermail':
        pipermail = Pipermail(options.uri, options.name)
        messages = pipermail.fetch()
    elif options.backend == 'mbox':
        mbox = MBox(uri=options.uri, dirpath=options.name)
        messages = mbox.fetch()

    print('Reading information from %s to insert into %s.db...' % (options.name, options.database))

    try:
        with database.atomic():
            success_messages_count = 0
            error_messages_count = 0
            for message in messages:
                try:

                    success_messages_count += 1
                    data = message['data']

                    email_from = data['From']

                    if 'To' in data:
                        email_to = data['To']
                    else:
                        email_to = 'NA'
                      
                    email_date = date_parser.parse(data['Date']).strftime("%Y-%m-%d")
                    precedence = data['Precedence']
                    if 'Received-SPF' in data:
                        received_spf = data['Received-SPF']
                    else:
                        received_spf = 'NA'
                        
                    return_path = data['Return-Path']
                    delivered_to = data['Delivered-To']
                    subject = data['Subject']
                    unixfrom = data['unixfrom']
                    reply_to = data['Reply-To']
                    list_unsubscribe = data['list-unsubscribe']

                    if 'X-ASF-Spam-Status' in data:
                        x_asf_spam_status = data['X-ASF-Spam-Status']
                    else:
                        x_asf_spam_status = 'NA'
                    
                    if 'In-Reply-To' in data:
                        in_reply_to = data['In-Reply-To']
                    else:
                        in_reply_to = 'NA'

                    received = data['Received']

                    if 'X-Spam-Check-By' in data:
                        x_spam_check_by = data['X-Spam-Check-By']
                    else:
                        x_spam_check_by = 'NA'

                    if 'References' in data:
                        references = data['References']
                    else:
                        references = 'NA'
                    
                    list_help = data['list-help']

                    if 'Content-Transfer-Encoding' in data:
                        content_transfer_encoding = data['Content-Transfer-Encoding']
                    else:
                        content_transfer_encoding = 'NA'
                    
                    x_original_to = data['X-Original-To']

                    if 'User-Agent' in data:
                        user_agent = data['User-Agent']
                    else:
                        user_agent = 'NA'

                    list_post = data['List-Post']
                    message_id = data['Message-ID']
                    mailing_list = data['Mailing-List']

                    if 'MIME-Version' in data:
                        mime_version = data['MIME-Version']
                    else:
                        mime_version = 'NA'

                    if 'Content-Type' in data:
                        content_type = data['Content-Type']
                    else:
                        content_type = 'NA'

                    list_id = data['List-Id']

                    if 'body' in data:
                        if 'plain' in data['body']:                        
                            body_plain = data['body']['plain']
                        elif 'html' in data['body']: 
                            body_plain = data['body']['html']
                    else:
                        body_plain = 'NA'

                    email_dbo = EmailDBO(
                                    email_from = email_from,
                                    email_to = email_to,
                                    email_date = email_date,
                                    precedence = precedence,
                                    received_spf = received_spf,
                                    return_path = return_path,
                                    delivered_to = delivered_to,
                                    subject = subject,
                                    unixfrom = unixfrom,
                                    reply_to = reply_to,
                                    list_unsubscribe = list_unsubscribe,
                                    x_asf_spam_status = x_asf_spam_status,
                                    in_reply_to = in_reply_to,
                                    received = received,
                                    x_spam_check_by = x_spam_check_by,
                                    references = references,
                                    list_help = list_help,
                                    content_transfer_encoding = content_transfer_encoding,
                                    x_original_to = x_original_to,
                                    user_agent = user_agent,
                                    list_post = list_post,
                                    message_id = message_id,
                                    mailing_list = mailing_list,
                                    mime_version = mime_version, 
                                    content_type = content_type,
                                    list_id = list_id,
                                    body_plain = body_plain,
                    )
                    email_dbo.save()
                    print('Saving email from %s to %s on %s...' % (email_from, email_to, email_date))

                except Exception as mex:
                    success_messages_count -= 1
                    error_messages_count += 1
                    print('ERROR READING AN EMAIL')
                    print(mex)
            print('SUCCESS: %s emails saved to db.' % success_messages_count)                
            print('ERROR: Unable to save %s emails.' % error_messages_count)                
    except Exception as tex:
        print('ERROR DATABASE TRANSACTION')        
        print(tex)

except Exception as e:
        print(e)