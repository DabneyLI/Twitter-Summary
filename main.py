import smtplib
from email.mime.text import MIMEText
from email.header import Header

def sendEmail(message:str, receiver:str, subject:str='测试邮件'):
    try:
        sender = os.environ['MAIL']
        smtpserver = os.environ['SMTP']
        username = os.environ['MAIL']
        password = os.environ['MAILPWD']

        msg = MIMEText(message, 'html', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['from'] = sender
        msg['to'] = receiver

        smtp = smtplib.SMTP_SSL(smtpserver, 465)
        smtp.login(username, password)
        smtp.sendmail(sender, [receiver], msg.as_string())
        smtp.quit()
        print('邮件发送成功')
    except smtplib.SMTPException as e:
        print('邮件发送失败', e)

if __name__ == '__main__':
    sendEmail("这是一封测试邮件。", os.environ['MAILTO'])
