#-*-coding: utf-8-*-

import os
import string
from os.path import getsize
from time import gmtime, strftime
import subprocess
from dropbox import client, rest, session
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('const.cfg')

APP_KEY = config.get('Section1', 'KEY')
APP_SECRET = config.get('Section1', 'SECRET')

ACCESS_TYPE = 'app_folder'
sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)

oauth_token,oauth_token_secret = '', ''

oauth_token = config.get('Section1', 'token')
oauth_token_secret = config.get('Section1', 'token_secret')
  

if oauth_token == '' or oauth_token_secret == '':
  request_token = sess.obtain_request_token()

  url = sess.build_authorize_url(request_token)
  print "url:", url
  print "Please visit this website and press the 'Allow' button, then hit 'Enter' here."
  raw_input()
  access_token = sess.obtain_access_token(request_token)
  
  config.set('Section1', 'token', access_token.key)
  config.set('Section1', 'token_secret', access_token.secret)
  with open('const.cfg', 'wb') as configfile:
    config.write(configfile)
else:
  sess.set_token(oauth_token, oauth_token_secret)

client = client.DropboxClient(sess)

USER = config.get('Section1', 'USER')
PASS = config.get('Section1', 'PASS')
HOST = config.get('Section1', 'HOST')
 
BACKUP_DIR = config.get('Section1', 'backup')
dumper = """ pg_dump -U %s -Z 9 -f %s  -F c %s -h %s  """                  
 
def log(string):
    print strftime("%Y-%m-%d-%H-%M-%S", gmtime()) + ": " + str(string)

os.putenv('PGPASSWORD', PASS)
database_list = [config.get('Section1', 'dbname')]

for database_name in database_list :
    log("dump started for %s" % database_name)
    thetime = str(strftime("%Y-%m-%d-%H-%M")) 
    file_name = database_name + '_' + thetime + ".sql.pgdump"
    command = dumper % (USER,  BACKUP_DIR + file_name, database_name, HOST)
    #log(command)
    subprocess.call(command,shell = True)
    log("%s dump finished" % database_name)
 
log("Backup job complete.")

with open(file_name,'rb') as f:
  fsize = getsize(file_name)
  uploader = client.get_chunked_uploader(f, fsize)
  print "Uploading file", fsize, "bytes..."
  while uploader.offset < fsize:
    try:
      upload = uploader.upload_chunked()
      print "."
    except rest.ErrorResponse, e:
      print "error uploading file!"
  uploader.finish("/"+file_name)
  f.close()
  print "File uploaded successfully."