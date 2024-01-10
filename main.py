import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def sendEmail(message:str, receiver:str=os.environ['MAILTO'], subject:str='测试邮件'):
    '''
    发送邮件的方法
    :param message: 邮件内容
    :param receiver: 接收者邮箱
    :param subject: 邮件主题
    :return:
    '''
    sender = os.environ['MAIL']  # 发送的邮箱
    receiver = receiver.split(';')  # 要接受的邮箱
    smtpserver = os.environ['SMTP']
    username = os.environ['MAIL']  # 邮箱账号
    password = os.environ['MAILPWD']  # 邮箱密码
    msg = MIMEText(message, 'html', 'utf-8')  # 中文需参数‘utf-8'，单字节字符不需要
    msg['Subject'] = Header(subject, 'utf-8')  # 邮件主题
    msg['from'] = sender  # 发送者邮件地址

    smtp = smtplib.SMTP_SSL(smtpserver, 465)  # 使用 SSL
    try:
        smtp.connect(smtpserver)  # 链接
        smtp.login(username, password)  # 登陆
        smtp.sendmail(sender, receiver, msg.as_string())  # 发送
        print('邮件发送成功')
    except smtplib.SMTPException:
        print('邮件发送失败')
    smtp.quit()  # 结束

if __name__=='__main__':
    fixed_message = "这是一封测试邮件。"  # 设定固定内容
    sendEmail(fixed_message)  # 发送邮件
