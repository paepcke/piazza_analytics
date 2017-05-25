'''
Takes paths containing users.json and class_content.json for class exports, and generates corresponding MySQL databases containing forum post data.
Note that not all post metadata is created in the databases. However, the essential requirements for analytics are taken care of.
For each class, a database with four tables is created:
1- 'users' table: This table contains all the information about the participants (students/ instructors) in the course.
2- 'class_content' table: This table contains the entire dataset dump of interactions on Piazza (questions, notes, follow-ups, student responses, instructor responses, feedbacks; literally everything).
3- 'questions' table: This table contains all the questions and their associated responses, feedbacks/ followups and other relevant statistics.
4- 'notes' table: This table contains all the notes and their feedbacks/ followups and other relevant statistics.

To run the code,

python new_schema_piazza.py --p /path_to_data_folder/ -d database_name
E.g. $ python new_schema_piazza.py -p /Users/xyz/Documents/piazza_downloads/data_folder -d music101_db

The first argument --p stands for path name and is compulsary and it must be a valid path to a folder containing class_content.json and users.json
The second argument --d stands for database name and is optional. In case you do not provide the database name, the default database name is piazza_dataset

'''

import json, time
import os
import argparse
import sys
import logging
from datetime import datetime
import MySQLdb as mdb
from constants import *
from utils import *

logger_output_file = 'output_logs.log'
logger = logging.getLogger('piazza_application')
logging.basicConfig(filename =logger_output_file, filemode= 'w', level=logging.INFO)

class Config(object):

    """Holds configurable parameters.
       These can be configured by the instructors of the course.
    """
    credit = {}
    credit['questions_asked'] = 1.0
    credit['questions_answered'] = 2.0
    credit['total_posts'] = 3.0
    credit['total_views'] = 1.0
    credit['days_online'] = 0.75
    credit['no_endorsed_answers'] = 5.0
    credit['total_no_endorsements'] = 7.0


class DataParser(object):

    """This is the main class that does all the functionality of parsing the information in the dataset and putting them into the database
    """
    def __init__(self):
        self.config_inst = Config()
        #self.logger = Logger()

    def fetch(self, task):
        # Connect to the database using the specified parameters
        con = mdb.connect(DB_PARAMS['host'], DB_PARAMS['user'], DB_PARAMS['password'])
        cur = con.cursor(mdb.cursors.DictCursor)

        # Create the database. Overwrites any existing instance.
        q = "DROP DATABASE IF EXISTS {0};".format(task['db_name'])
        try:
            cur.execute(q)
        except:
            pass

        q = "CREATE DATABASE {0};".format(task['db_name'])
        cur.execute(q)

        q = "USE {0};".format(task['db_name'])
        cur.execute(q)

        logger.info("Created the database")

        ## Create the class content table
        ##################################
        logger.info("Creating the class_content table")

        q = "CREATE TABLE class_content (id varchar(255) PRIMARY KEY, type varchar(255), created DATETIME, user_id varchar(255), subject LONGTEXT, content LONGTEXT, status varchar(255), nr int, no_answer_followup int, tags LONGTEXT, is_root int, changelog_user_ids LONGTEXT, unique_views int, no_upvotes_defunct int, no_endorsements int, endorsers text, no_upvoters int, upvoters text, folders varchar(255), user_id_role varchar(255), root_id varchar(255));"

        cur.execute(q)

        #Reading the class_content file from the dataset and loading the json as a dictionary.
        f = open(task['input'] + 'class_content.json', 'rb')
        data = json.loads(f.read())
        f.close()

        def parse_posts(x):
                    if 'created' in x.keys():
                        tc = x['created']
                    else:
                        tc = '2000-01-10T00:00:00Z'
                    dt = datetime(int(tc[0:4]), int(tc[5:7]), int(tc[8:10]), int(tc[11:13]), int(tc[14:16]), int(tc[17:19]))
                    nodes = []

                    if 'history' in x.keys():
                        nodes .append({
                            'id': x['id'],
                            'type': x['type'],
                            'created': dt,
                            'user_id': x['history'][0]['uid'] if 'uid' in x['history'][0].keys() else 'None',
                            'subject': x['history'][0]['subject'],
                            'content': x['history'][0]['content'],
                            'status': x['status'] if 'status' in x.keys() else ' ',
                            'nr': x['nr'],
                            'no_answer_followup': x['no_answer_followup'],
                            'tags': json.dumps(x['tags']),
                            'is_root': 1,
                            'changelog_user_ids': json.dumps([c['uid'] if 'uid' in c.keys() else 'None' for c in x['change_log']]),
                            'unique_views': x['unique_views'],
                            'no_upvotes_defunct': x['no_upvotes'] if 'no_upvotes' in x else 0,
                            'no_endorsements':len(x['tag_endorse_arr']) if 'tag_endorse_arr' in x else 0,
                            'endorsers':json.dupms(x['tag_endorse_arr']) if 'tag_endorse_arr' in x else ' ',
                            'upvoters':json.dumps(x['tag_good_arr']) if 'tag_good_arr' in x else ' ',
                            'folders':json.dumps(x['folders']) if 'folders' in x else ' ',
                            'no_upvoters':len(x['tag_good_arr']) if 'tag_good_arr' in x else 0,
                            'user_id_role': "not available",
                            'root_id': x['id']
                        })
                    else:
                        logger.info("Not expecting any posts without 'history' in keys")

                    if 'folders' in x.keys():
                        folders = json.dumps(x['folders'])
                    else:
                        folders = 'None'
                    tags = json.dumps(x['tags'])

                    if 'children' in x.keys():
                        for c in x['children']:
                            ch = self.ChildTreeToList(c,x['nr'], x['unique_views'], x['id'], folders, tags)
                            if ch:
                                nodes.extend(ch)
                    return nodes

        for x in data:
            nodes = parse_posts(x)

            for node in nodes:
                q = "INSERT INTO class_content VALUES ('{0}','{1}', '{2}', '{3}', '{4}', '{5}', '{6}', {7},{8},'{9}', {10}, '{11}', {12}, {13}, {14}, '{15}', {16}, '{17}', '{18}', '{19}', '{20}');".format(
                    node['id'],
                    node['type'],
                    node['created'],
                    'null' if not node['user_id'] else node['user_id'],
                    cleanhtml(self, node['subject'].replace("\\", "%").replace("'", "\\'").encode('utf-8')),
                    cleanhtml(self, node['content'].replace("\\", "%").replace("'", "\\'").encode('utf-8')),
                    node['status'],
                    node['nr'],
                    node['no_answer_followup'],
                    node['tags'],
                    node['is_root'],
                    node['changelog_user_ids'],
                    node['unique_views'],
                    node['no_upvotes_defunct'],
                    node['no_endorsements'],
                    node['endorsers'],
                    node['no_upvoters'],
                    node['upvoters'],
                    node['folders'],
                    node['user_id_role'],
                    node['root_id']
                )
                cur.execute(q)

        logger.info("Created the class_content table")

        ## Create the questions table
        ##########################
        logger.info("Creating the questions table")

        list_question_ids = []

        q = "SELECT id from class_content where type = 'question';"
        cur.execute(q)

        data = cur.fetchall()

        for row in data:
            list_question_ids.append(row['id'])

        q = "CREATE TABLE questions (id varchar(255) PRIMARY KEY, question_text LONGTEXT, user_id_role varchar(255), no_upvotes_on_question int, i_answer LONGTEXT, s_answer LONGTEXT, no_upvotes_on_i_answer int, no_upvotes_on_s_answer int, no_unique_collaborations int, follow_up_thread LONGTEXT, length_of_follow_up_thread int, folders LONGTEXT, tags LONGTEXT, created DATETIME);"

        cur.execute(q)

        #Building the questions table from the class_content table

        nodes = []
        for i in range(len(list_question_ids)):
            question_id  = list_question_ids[i]
            cur.execute("""SELECT content, no_upvoters, changelog_user_ids, folders, tags, created from class_content where id = '%s'""" %(question_id))
            data = cur.fetchall()
            question_content = cleanhtml(self, data[0]['content'])
            no_upvotes_on_que = data[0]['no_upvoters']
            no_unique_collab = len(set(data[0]['changelog_user_ids'].split(',')))-1
            folders = data[0]['folders']
            tags = data[0]['tags']
            created_timestamp = data[0]['created']

            cur.execute("""SELECT content, no_endorsements from class_content where type = 'i_answer' and root_id = '%s'""" %(question_id))
            if cur.rowcount != 0:
                data = cur.fetchall()
                instructor_answer = cleanhtml(self, data[0]['content'])
                no_upvotes_on_i_answer = data[0]['no_endorsements']

            else:
                instructor_answer = 'None'
                no_upvotes_on_i_answer = 0

            cur.execute("""SELECT content, no_endorsements from class_content where type = 's_answer' and root_id = '%s'""" %(question_id))
            if cur.rowcount != 0:
                data = cur.fetchall()
                student_answer = cleanhtml(self, data[0]['content'])
                no_upvotes_on_s_answer = data[0]['no_endorsements']
            else:
                student_answer = 'None'
                no_upvotes_on_s_answer = 0


            # The string "******************" is used as a delimiter between follow_ups.
            follow_ups = ' '
            cur.execute("""SELECT content from class_content where type IN ('followup', 'feedback') and root_id = '%s'""" %(question_id))
            follow_up_thread_len = 0
            if cur.rowcount != 0:
                data = cur.fetchall()
                for i in range(len(data)):
                    follow_ups += data[i]['content']
                    follow_ups += "******************"
                    follow_up_thread_len += 1
            else:
                follow_ups = ''

            follow_ups = cleanhtml(self, follow_ups)

            nodes.append({
                'id':question_id,
                'question_text': question_content,
                'user_id_role':'not available',
                'no_upvotes_on_question': no_upvotes_on_que,
                'i_answer': instructor_answer,
                's_answer': student_answer,
                'no_upvotes_on_i_answer': no_upvotes_on_i_answer,
                'no_upvotes_on_s_answer': no_upvotes_on_s_answer,
                'no_unique_collaborations': no_unique_collab,
                'follow_up_thread':follow_ups,
                'length_of_follow_up_thread':follow_up_thread_len,
                'folders':folders,
                'tags':tags,
                'created':created_timestamp
                })


        for node in nodes:
            q = "INSERT INTO questions VALUES ('{0}','{1}', '{2}',{3}, '{4}', '{5}', {6}, {7}, {8}, '{9}', {10}, '{11}', '{12}', '{13}');".format(
                node['id'],
                node['question_text'],
                node['user_id_role'],
                node['no_upvotes_on_question'],
                node['i_answer'],
                node['s_answer'],
                node['no_upvotes_on_i_answer'],
                node['no_upvotes_on_s_answer'],
                node['no_unique_collaborations'],
                node['follow_up_thread'],
                node['length_of_follow_up_thread'],
                node['folders'],
                node['tags'],
                node['created']
            )
            cur.execute(q)

        logger.info("Created the questions table")

        ## Create the notes table
        ##########################

        logger.info("Creating the notes table")
        list_notes_ids = []

        q = "SELECT id from class_content where type = 'note';"
        cur.execute(q)

        data = cur.fetchall()

        for row in data:
            list_notes_ids.append(row['id'])

        q = "CREATE TABLE notes (id varchar(255) PRIMARY KEY, notes_text LONGTEXT, user_id_role varchar(255), no_upvotes_on_note int, no_unique_collaborations int, follow_up_thread LONGTEXT, length_of_follow_up_thread int, folders LONGTEXT, tags LONGTEXT, created DATETIME);"
        cur.execute(q)

        #Building the notes table from the class_content table

        nodes = []
        for i in range(1, len(list_notes_ids)):
            notes_id  = list_notes_ids[i]
            cur.execute("""SELECT content, no_upvoters, changelog_user_ids, folders, tags, created from class_content where id = '%s'""" %(notes_id))
            data = cur.fetchall()
            notes_content = cleanhtml(self, data[0]['content'])
            no_upvotes_on_note = data[0]['no_upvoters']
            no_unique_collab = len(set(data[0]['changelog_user_ids'].split(',')))-1
            folders = data[0]['folders']
            tags = data[0]['tags']
            created_timestamp = data[0]['created']

            # The string "******************" is used as a delimiter between follow_ups.
            follow_ups = ' '
            cur.execute("""SELECT content from class_content where type IN ('followup', 'feedback') and root_id = '%s'""" %(notes_id))
            follow_up_thread_len = 0
            if cur.rowcount != 0:
                data = cur.fetchall()
                for i in range(len(data)):
                    follow_ups += data[i]['content']
                    follow_ups += "******************"
                    follow_up_thread_len +=1
            else:
                follow_ups = ''

            follow_ups = cleanhtml(self, follow_ups)

            nodes.append({
                'id':notes_id,
                'notes_text': notes_content,
                'user_id_role':'not available',
                'no_upvotes_on_note': no_upvotes_on_note,
                'no_unique_collaborations': no_unique_collab,
                'follow_up_thread':follow_ups,
                'length_of_follow_up_thread':follow_up_thread_len,
                'folders':folders,
                'tags':tags,
                'created':created_timestamp
                })

        for node in nodes:
            q = "INSERT INTO notes VALUES ('{0}','{1}', '{2}',{3}, {4}, '{5}', {6}, '{7}','{8}', '{9}');".format(
                node['id'],
                mdb.escape_string(node['notes_text']),
                node['user_id_role'],
                node['no_upvotes_on_note'],
                node['no_unique_collaborations'],
                node['follow_up_thread'],
                node['length_of_follow_up_thread'],
                node['folders'],
                node['tags'],
                node['created']
            )
            cur.execute(q)

        logger.info("Created the notes table")

         ## Create the users table
        ##########################

        logger.info("Creating the users table")

        q = "CREATE TABLE users (id varchar(255) PRIMARY KEY, answers int, asks int, posts int, views int, days_online int, no_endorsed_answers int, total_no_endorsements int, role varchar(255), contribution int);"
        cur.execute(q)

        f = open(task['input'] + 'users.json', 'rb')
        data = json.loads(f.read())
        f.close()

        for x in data:
            q = "INSERT INTO users (id, answers, asks, posts, views, days_online, no_endorsed_answers, total_no_endorsements,role, contribution) VALUES ('{0}',{1},{2},{3},{4},{5},{6},{7}, '{8}', {9});".format(x['user_id'], x['answers'], x['asks'], x['posts'], x['views'], x['days'], 0, 0, 'not available', 0)
            cur.execute(q)

        list_user_ids = []

        q = "SELECT id from users;"
        cur.execute(q)
        data = cur.fetchall()

        for row in data:
            list_user_ids.append(row['id'])

        for i in range(len(list_user_ids)):
            user_id  = list_user_ids[i]
            total_endorsements_count = 0
            cur.execute("""SELECT no_endorsements from class_content where user_id = '%s' AND type IN ('s_answer', 'i_answer') AND no_endorsements != 0 """ %(user_id))
            data = cur.fetchall()
            for i in range(len(data)):
                total_endorsements_count += data[i]['no_endorsements']
            endorsed_answers_count = len(data)
            cur.execute("""UPDATE users set no_endorsed_answers = %d, total_no_endorsements = %d WHERE id = '%s'""" %(endorsed_answers_count,total_endorsements_count,user_id))
            cur.execute("""SELECT answers, asks, posts, views, days_online,no_endorsed_answers, total_no_endorsements from users where id = '%s'""" %(user_id))
            data = cur.fetchall()

            '''Fetching the weightage of each of the factors from the distionary in the Config class that can be configured by the instructors of the course
            '''
            asks = data[0]['asks']
            answers = data[0]['answers']
            posts = data[0]['posts']
            views = data[0]['views']
            days_online = data[0]['days_online']
            no_endorsed_answers = data[0]['no_endorsed_answers']
            total_no_endorsements = data[0]['total_no_endorsements']

            '''Adding up the contributions by each of the factor to get the total credit for the user.
            '''
            total_credit = self.config_inst.credit['questions_asked'] * asks + \
                           self.config_inst.credit['questions_answered'] * answers + \
                           self.config_inst.credit['total_posts'] * posts + \
                           self.config_inst.credit['total_views'] * views + \
                           self.config_inst.credit['days_online'] * days_online + \
                           self.config_inst.credit['no_endorsed_answers'] * no_endorsed_answers + \
                           self.config_inst.credit['total_no_endorsements'] * total_no_endorsements

            cur.execute("""UPDATE users set contribution = %d WHERE id = '%s'""" %(total_credit,user_id))

            # ''' Extracting the endorsers of a user '''

            # endorsers = ''
            # cur.execute("""SELECT endorsers from class_content where user_id = '%s' and no_endorsements != 0 """ %(user_id))
            # data = cur.fetchall()
            # if cur.rowcount > 1:
            #     for i in range(len(data)-1):
            #         endorsers += data[i]['endorsers']
            #         print data[i]
            #         endorsers += ','
            #     endorsers += data[i]['endorsers']

            # elif cur.rowcount == 1:
            #     endorsers = data[0]['endorsers']

            # else:
            #     endorsers = "None"

            # cur.execute("""UPDATE users set endorsers = '%s' WHERE id = '%s'""" %(endorsers, user_id))

            # ''' Extracting the upvoters of a user '''
            # upvoters = ''
            # cur.execute("""SELECT upvoters from class_content where user_id = '%s' and no_upvoters != 0 """ %(user_id))
            # data = cur.fetchall()
            # if cur.rowcount != 0:
            #     for i in range(len(data)):
            #         upvoters += data[i]['upvoters']
            #         upvoters += ','

            # else:
            #     upvoters = "None"

            # cur.execute("""UPDATE users set upvoters = '%s' WHERE id = '%s'""" %(upvoters, user_id))

            '''Extracting the role of a user based on whether the user_id comes up in a student answer, instructor answer and/ or instructor note
            '''
            student_answer_exists = False
            instructor_answer_exists = False
            instructor_note_exists = False

            cur.execute("""SELECT distinct count(*) AS s_answer_count from class_content where type ='s_answer' and user_id = '%s' """ %(user_id))
            data = cur.fetchall()
            if data[0]['s_answer_count'] != 0:
                student_answer_exists = True

            else:
                cur.execute("""SELECT distinct count(*) AS i_answer_count from class_content where type ='i_answer' and user_id = '%s' """ %(user_id))
                data = cur.fetchall()
                if data[0]['i_answer_count'] != 0:
                    instructor_answer_exists = True

                if not instructor_answer_exists:
                    cur.execute("""SELECT distinct count(*) AS i_notes_count from class_content where tags LIKE
                        "%%instructor-note%%" and user_id = '%s' """ %(user_id))
                    data = cur.fetchall()
                    if data[0]['i_notes_count'] != 0:
                        instructor_note_exists = True

            if student_answer_exists:
                cur.execute("""UPDATE users set role = 'student' where id = '%s' """ %(user_id))
            elif instructor_answer_exists or instructor_note_exists:
                cur.execute("""UPDATE users set role = 'instructor' where id = '%s' """ %(user_id))

        set_of_instructors_from_parsed_class_content, set_of_students_from_parsed_class_content, = identify_role(self, task)
        for i in range(len(set_of_instructors_from_parsed_class_content)):
            cur.execute("""UPDATE users set role = 'instructor' where id = '%s' """ %(user_id))
        for i in range(len(set_of_students_from_parsed_class_content)):
            cur.execute("""UPDATE users set role = 'student' where id = '%s' """ %(user_id))

        ''' Since the users table has the role populated now, we can propagate the same to the class_content table, questions table and notes tables.
        '''
        list_posts = []
        q = "SELECT id from class_content;"
        cur.execute(q)
        data = cur.fetchall()

        for row in data:
            list_posts.append(row['id'])

        for i in range(len(list_posts)):
            cur.execute("""SELECT user_id from class_content where id = '%s' """ %(list_posts[i]))
            data = cur.fetchall()
            user_id_to_fetch = data[0]['user_id']
            cur.execute("""SELECT role from users where id = '%s' """ %(user_id_to_fetch))
            data = cur.fetchall()
            if cur.rowcount != 0:
                role = data[0]['role']
                cur.execute("""UPDATE class_content set user_id_role = '%s' where id = '%s' """ %(role, list_posts[i]))
                cur.execute("""SELECT id from questions where id = '%s' """ %(list_posts[i]))
                data = cur.fetchall()
                if cur.rowcount != 0:
                    question_id = data[0]['id']
                    cur.execute("""UPDATE questions set user_id_role = '%s' where id = '%s' """ %(role, question_id))

                cur.execute("""SELECT id from notes where id = '%s' """ %(list_posts[i]))
                data = cur.fetchall()
                if cur.rowcount != 0:
                    note_id = data[0]['id']
                    cur.execute("""UPDATE notes set user_id_role = '%s' where id = '%s' """ %(role, note_id))



        con.commit()
        con.close()
        logger.info("Created the users table")


    def ChildTreeToList(self, x,nr,unique_views, root_id, folders, tags):
        if 'created' in x.keys():
            tc = x['created']
        else:
            tc = '2000-01-10T00:00:00Z'
        dt = datetime(int(tc[0:4]), int(tc[5:7]), int(tc[8:10]), int(tc[11:13]), int(tc[14:16]), int(tc[17:19]))

        if 'history' not in x.keys():
            x['uid'] = 'None'

        child_list = []
        if 'history' in x.keys():
            child_list.append({
                'id': x['id'],
                'type': x['type'],
                'created': dt,
                'user_id': x['history'][0]['uid'] if 'uid' in x['history'][0].keys() else 'None',
                'subject': '',
                'content': cleanhtml(self, x['history'][0]['content']) if 'content' in x['history'][0].keys() else ' ',
                'status': '',
                'nr': nr,
                'no_answer_followup': 0,
                'tags': tags,
                'is_root': 0,
                'changelog_user_ids':'None',
                'unique_views':unique_views,
                'no_upvotes_defunct': x['no_upvotes_defunct'] if 'no_upvotes_defunct' in x else 0,
                'no_endorsements':len(x['tag_endorse_arr']) if 'tag_endorse_arr' in x else 0,
                'endorsers':json.dumps(x['tag_endorse_arr']) if 'tag_endorse_arr' in x else ' ',
                'upvoters':json.dumps(x['tag_good_arr']) if 'tag_good_arr' in x else ' ',
                'folders':folders,
                'no_upvoters':len(x['tag_good_arr']) if 'tag_good_arr' in x else 0,
                'user_id_role': "not available",
                'root_id':root_id
            })
        if 'history' not in x.keys():
            child_list.append({
                'id': x['id'],
                'type': x['type'],
                'created': dt,
                'user_id':'None',
                'subject': '',
                'content': cleanhtml(self, x['subject']) if 'subject' in x else ' ',
                'status': '',
                'nr': nr,
                'no_answer_followup': 0,
                'tags': tags,
                'is_root': 0,
                'changelog_user_ids':'None',
                'unique_views':unique_views,
                'no_upvotes_defunct': x['no_upvotes_defunct'] if 'no_upvotes_defunct' in x else 0,
                'no_endorsements':len(x['tag_endorse_arr']) if 'tag_endorse_arr' in x else 0,
                'endorsers':json.dumps(x['tag_endorse_arr']) if 'tag_endorse_arr' in x else ' ',
                'upvoters':json.dumps(x['tag_good_arr']) if 'tag_good_arr' in x else ' ',
                'folders':folders,
                'no_upvoters':len(x['tag_good_arr']) if 'tag_good_arr' in x else 0,
                'user_id_role': "not available",
                'root_id':root_id
            })

        if 'children' in x:
            for c in x['children']:
                child_list.extend(self.ChildTreeToList(c,nr,unique_views, root_id, folders, tags))
        return child_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]), formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-p', '--path-dataset', required=True,
                        help='Path of the folder containing the dataset eg. /Users/abc/Desktop/piazza_downloads/data_folder',
                        dest='path_dataset',
                        default=None)

    parser.add_argument('-d', '--dbname',
                        help='Database name',
                        dest='db_name',
                        default='piazza_dataset');


    args = parser.parse_args()

    if not os.path.isfile(args.path_dataset+"class_content.json") or not os.path.isfile(args.path_dataset+"users.json"):
        #if the last character in the path is not a forward slash, then we add one to avoid error
        if args.path_dataset[-1]!= '/':
            args.path_dataset+= '/'
        # If there isn't a valid file in the path, we throw an error
        if not os.path.isfile(args.path_dataset+"class_content.json") or not os.path.isfile(args.path_dataset+"users.json"):
            print "Unable to find valid class_content.json and/or users.json in this location"
            exit(1)


#task = { "input" : "/Users/ankita/Desktop/RA/piazza_downloads/data_folder/", "db_name": "cs246_winter2017"}
task = { "input": args.path_dataset, "db_name": args.db_name}
parser = DataParser()
parser.fetch(task)
