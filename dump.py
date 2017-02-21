import subprocess
import ConfigParser
from time import strftime
from os.path import getsize
from dropbox import client, rest, session
 
 
# populating variables
ACCESS_TYPE = 'app_folder'
config = ConfigParser.RawConfigParser()
config.read('const.cfg')
APP_KEY = config.get('Section1', 'KEY')
APP_SECRET = config.get('Section1', 'SECRET')
oauth_token = config.get('Section1', 'token')
oauth_token_secret = config.get('Section1', 'token_secret')
sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)

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
  
# dropbox part
client = client.DropboxClient(sess)
USER = config.get('Section1', 'USER')
PASS = config.get('Section1', 'PASS')
HOST = config.get('Section1', 'HOST')
BACKUP_DIR = config.get('Section1', 'backup')
dumper = """ pg_dump -U %s -Z 9 -f %s  -F c %s -h %s  """
database_name = config.get('Section1', 'dbname')
 
# creating backup 
print "dump started for %s" % database_name
thetime = str(strftime("%Y-%m-%d-%H-%M"))
file_name = database_name + '_' + thetime + ".sql.pgdump"
command = dumper % (USER, BACKUP_DIR + file_name, database_name, HOST)
subprocess.call(command, shell=True)
print "%s dump finished" % database_name
print "Backup job complete."
 
 
with open(file_name, 'rb') as f:
    fsize = getsize(file_name)
    uploader = client.get_chunked_uploader(f, fsize)
    print "Uploading file", fsize, "bytes..."
    while uploader.offset < fsize:
        try:
            upload = uploader.upload_chunked()
            print "."
        except rest.ErrorResponse, e:
            print "error uploading file!"
    uploader.finish("/" + file_name)
    f.close()
    print "File uploaded successfully."
