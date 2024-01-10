import os
import re
import json
from datetime import datetime, timedelta
import pandas as pd
import requests
from bs4 import BeautifulSoup
from litellm import completion
from feedparser import parse
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from markdown import markdown
from dotenv import load_dotenv, find_dotenv
from github import Github

# 加载环境变量
load_dotenv(find_dotenv())

def sendEmail(message:str, receiver:str=os.environ['MAILTO'], subject:str=''):
    '''
    发送邮件的方法
    :param message:
    :param receiver:
    :param subject:
    :return:
    '''
    if len(message) == 0:
        return
    message=message.replace('<td','<td style="border:1px solid grey;"').replace('<table','<table style="border-collapse:collapse;"')
    subject=datetime.now().strftime('%Y年%m月%d日')+subject
    sender = os.environ['MAIL'] #发送的邮箱
    receiver = receiver.split(';')  #要接受的邮箱（注:测试中发送其他邮箱会提示错误）
    smtpserver = os.environ['SMTP']
    username = os.environ['MAIL'] #你的邮箱账号
    password = os.environ['MAILPWD'] #你的邮箱密码
    msg = MIMEText(message,'html','utf-8') #中文需参数‘utf-8'，单字节字符不需要
    msg['Subject'] = Header(subject, 'utf-8') #邮件主题
    msg['from'] = sender    #自己的邮件地址
    # smtp = smtplib.SMTP()
    smtp = smtplib.SMTP_SSL(smtpserver, 465) # 使用 SSL
    # smtp.starttls() # 如果使用 TLS，取消注释这行
    try :
        smtp.connect(smtpserver) # 链接
        print('链接成功')
        smtp.login(username, password) # 登陆
        print('登陆成功')
        smtp.sendmail(sender, receiver, msg.as_string()) #发送
        print('邮件发送成功')
    except smtplib.SMTPException:
        print('邮件发送失败')
    smtp.quit() # 结束

def sumTweets(lang='中文', length:int=10000, model='openai/gpt-3.5-turbo-1106', mail=True, render=True):
    '''
    抓取目标推特AI总结并发邮件
    :param lang:
    :param length:
    :param model:
    :param mail:
    :param render:
    :param info: 要筛选的信息关键词
    :return:
    '''
    users = os.environ['TARGET']
    info: str = os.environ['INFO']
    nitter = os.environ['NITTER']
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    all_tweets = []  # 用于存储所有用户的推文
    result = ''

    for user in users.split(';'):
        rss_url = f'https://{nitter}/{user}/rss'
        feed = parse(rss_url)
        df = pd.json_normalize(feed.entries)
        df['timestamp'] = df.apply(lambda x: pd.Timestamp(x.get('published', '1970-01-01')).timestamp(), axis=1)
        if not 'i/lists' in user:
            df = df.reindex(index=df.index[::-1])
        df = df[df['timestamp'] > pd.Timestamp(one_week_ago).timestamp()]

        # ...原有的推文处理逻辑...

        # 从每个用户的DataFrame中筛选info相关的推文
        df_info_related = df[df['summary'].str.contains(info)]

        # 将筛选后的推文添加到汇总列表中
        all_tweets.extend(df_info_related.to_dict(orient='records'))

    # 汇总所有用户推文后保存为JSON文件
    filename = "all_info_related_tweets.json"
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(all_tweets, file, ensure_ascii=False)

    # 检查内容是否有更新并上传到GitHub
    if is_content_updated(filename, "your_repository_name", os.environ['GH_TOKEN']):
        upload_to_github(filename, "your_repository_name", os.environ['GH_TOKEN'])

    # 如果邮件内容不为空，则发送邮件
    if mail and len(result) > 0:
        if render:
            result = markdown(result, extensions=['markdown.extensions.tables'])
        sendEmail(result)

    return result

def upload_to_github(filename, repository_name, github_token):
    g = Github(github_token)
    repo = g.get_user().get_repo(repository_name)
    with open(filename, 'r') as file:
        content = file.read()
    try:
        contents = repo.get_contents(filename)
        repo.update_file(contents.path, "Update tweets", content, contents.sha)
        print(f"文件 {filename} 已更新到GitHub")
    except:
        repo.create_file(filename, "Create tweets", content)
        print(f"文件 {filename} 已创建并上传到GitHub")

def is_content_updated(filename, repository_name, github_token):
    g = Github(github_token)
    repo = g.get_user().get_repo(repository_name)
    try:
        contents = repo.get_contents(filename)
        existing_content = contents.decoded_content.decode('utf-8')
        with open(filename, 'r') as file:
            new_content = file.read()
        return existing_content != new_content
    except:
        return True  # 如果文件不存在，那么内容一定是“更新”的

if __name__ == '__main__':
    sumTweets(mail=True, render=True, info=os.environ['INFO'])
