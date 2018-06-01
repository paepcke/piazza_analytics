import getpass
import os

#COURSES =  ['cs221','cs229','cs231a','mse252','biomedin214']
#COURSES =  ['cultural_heritage','econ50','humbio3a','urbanst145','womhealth']
#COURSES = ['cs221','cs229','cs231a','mse252','music320','polsci350','biomedin214','womhealth','cultural_heritage','econ50','humbio3a','urbanst145']
# COURSES = ['cs231a', 'cs246', 'cs224s']
# COURSES = ['cs246', 'cs221', 'cs224s', 'cs231a']
COURSES = ['cs221']

# COURSES = ['cs221']

# Leave user and password blank to use
# script-invoking user as the MySQL user,
# and the password in ~/.ssh/mysql as
# the pwd:

DATA_DIRECTORY = os.path.join(os.path.dirname(__file__), '../data')

DB_PARAMS = {
    'host': 'localhost',
    'user': '',
    'password': ''
}

def getMySQLPasswd(root=False):
    '''
    Checks if ~/.ssh contains the MySQL pwd
    in a file. If so, returns that pwd. else
    returns empty string.

    For root the pwd file name in ~/.ssh is
    expected to be 'mysql_root'. For the current
    user the pwd should be in 'mysql'
    '''
    
    homeDir=os.path.expanduser('~'+getpass.getuser())

    if root:
        f_name = homeDir + '/.ssh/mysql_root'
    else:
        f_name = homeDir + '/.ssh/mysql'
    try:
        with open(f_name, 'r') as f:
            password = f.readline().strip()
    except IOError:
        return ''
    return password

# If no user given, set user to the one
# who invoked this script:

if len(DB_PARAMS['user']) == 0:
    DB_PARAMS['user'] = getpass.getuser()

# If no pwd given, try to find the pwd in
# ~/.ssh:

if len(DB_PARAMS['password']) == 0:
    if DB_PARAMS['user'] == 'root':
         DB_PARAMS['password'] = getMySQLPasswd(root=True)
    else:
         DB_PARAMS['password'] = getMySQLPasswd(root=False)
         

