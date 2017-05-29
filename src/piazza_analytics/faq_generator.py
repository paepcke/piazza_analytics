import json, time
import os
import sys
import logging
from datetime import datetime
import MySQLdb as mdb
from constants import *
import numpy as np
from configuration import *

class FAQGenerator:

    def __init__(self):
        self.config_inst = Config()
        #self.logger = Logger()

    def generate_faq_from_questions(self, task):
        # Connect to the database using the specified parameters
        con = mdb.connect(DB_PARAMS['host'], DB_PARAMS['user'], DB_PARAMS['password'])
        cur = con.cursor(mdb.cursors.DictCursor)

        q = "USE {0};".format(task['db_name'])
        cur.execute(q)

        q = "SELECT max(no_upvotes_on_question) AS max_no_upvotes from questions;"    
        cur.execute(q)
        data = cur.fetchall()
        max_upvotes_count = data[0]['max_no_upvotes']

        upvotes_on_que = []
        upvotes_on_i_answer = []
        upvotes_on_s_answer = []
        unique_collaborations = []
        follow_up_thread = []

        for i in range(1, max_upvotes_count+1):
            q = """SELECT distinct count(*) AS count from questions where no_upvotes_on_question = %d """ %(i)
            cur.execute(q)
            data = cur.fetchall()
            count = data[0]['count']
            upvotes_on_que.extend(np.repeat(i, count))

        upvotes_on_que = np.array(upvotes_on_que)     
        threshold_for_upvotes_on_que = np.percentile(upvotes_on_que, self.config_inst.thresholds['upvotes_on_que'])

        print "Done with no_upvotes_on_question"

        q = "SELECT max(no_upvotes_on_i_answer) AS max_no_upvotes from questions;"    
        cur.execute(q)
        data = cur.fetchall()
        max_upvotes_count_on_ianswer = data[0]['max_no_upvotes']
        for i in range(1, max_upvotes_count_on_ianswer+1):
            q = """SELECT distinct count(*) AS count from questions where no_upvotes_on_i_answer = %d """ %(i)
            cur.execute(q)
            data = cur.fetchall()
            count = data[0]['count']
            upvotes_on_i_answer.extend(np.repeat(i,count))

        upvotes_on_i_answer = np.array(upvotes_on_i_answer)     
        threshold_for_upvotes_on_i_answer = np.percentile(upvotes_on_i_answer, self.config_inst.thresholds['upvotes_on_i_answer'])

        print "Done with no_upvotes_on_i_answer"


        q = "SELECT max(no_upvotes_on_s_answer) AS max_no_upvotes from questions;"    
        cur.execute(q)
        data = cur.fetchall()
        max_upvotes_count_on_sanswer = data[0]['max_no_upvotes']
        for i in range(1, max_upvotes_count_on_sanswer+1):
            q = """SELECT distinct count(*) AS count from questions where no_upvotes_on_s_answer = %d """ %(i)
            cur.execute(q)
            data = cur.fetchall()
            count = data[0]['count']
            upvotes_on_s_answer.extend(np.repeat(i,count))

        upvotes_on_s_answer = np.array(upvotes_on_s_answer)     
        threshold_for_upvotes_on_s_answer = np.percentile(upvotes_on_s_answer, self.config_inst.thresholds['upvotes_on_i_answer'])
            
        print "Done with no_upvotes_on_s_answer"


        q = "SELECT max(no_unique_collaborations) AS max_no_unique_collabs from questions;"    
        cur.execute(q)
        data = cur.fetchall()
        max_no_unique_collabs = data[0]['max_no_unique_collabs']

        for i in range(1, max_no_unique_collabs+1):
            q = """SELECT distinct count(*) AS count from questions where no_unique_collaborations = %d """ %(i)
            cur.execute(q)
            data = cur.fetchall()
            count = data[0]['count']
            unique_collaborations.extend(np.repeat(i,count))

        unique_collaborations = np.array(unique_collaborations)     
        threshold_for_unique_collaborations = np.percentile(unique_collaborations, self.config_inst.thresholds['unique_collaborations'])

        print "Done with no_unique_collaborations"

        q = "SELECT max(length_of_follow_up_thread) AS max_length_of_follow_up_thread from questions;"    
        cur.execute(q)
        data = cur.fetchall()
        max_len_follow_up_thread = data[0]['max_length_of_follow_up_thread']
        
        for i in range(1, max_len_follow_up_thread+1):
            q = """SELECT distinct count(*) AS count from questions where length_of_follow_up_thread = %d """ %(i)
            cur.execute(q)
            data = cur.fetchall()
            count = data[0]['count']
            follow_up_thread.extend(np.repeat(i,count))

        follow_up_thread = np.array(follow_up_thread)     
        threshold_for_follow_up_thread= np.percentile(follow_up_thread, self.config_inst.thresholds['follow_up_thread'])
        print "Thresholds are", threshold_for_upvotes_on_que,threshold_for_upvotes_on_i_answer,threshold_for_upvotes_on_s_answer,threshold_for_unique_collaborations, threshold_for_follow_up_thread

        print "Done with length_of_follow_up_thread"

        q = """SELECT distinct count(*) AS count from questions where no_upvotes_on_question >= %d and (no_upvotes_on_i_answer >= %d or no_upvotes_on_s_answer >= %d) and no_unique_collaborations >= %d and length_of_follow_up_thread >= %d and tags NOT LIKE "%%logistics%%" and folders NOT LIKE "%%logistics%%" """ %(threshold_for_upvotes_on_que,threshold_for_upvotes_on_i_answer, threshold_for_upvotes_on_s_answer, threshold_for_unique_collaborations,threshold_for_follow_up_thread )
        cur.execute(q)
        data = cur.fetchall()
        count = data[0]['count']
        print "Count of qualifying questions", count
     
        q = """SELECT question_text, i_answer, s_answer, tags, folders from questions where no_upvotes_on_question >= %d and (no_upvotes_on_i_answer >= %d or no_upvotes_on_s_answer >= %d) and no_unique_collaborations >= %d and length_of_follow_up_thread >= %d and tags NOT LIKE "%%logistics%%" and folders NOT LIKE "%%logistics%%" """ %(threshold_for_upvotes_on_que,threshold_for_upvotes_on_i_answer, threshold_for_upvotes_on_s_answer, threshold_for_unique_collaborations,threshold_for_follow_up_thread)

        cur.execute(q)
        data = cur.fetchall()
        f = open('faq_questions.txt', 'w')

        for i in range(len(data)):
            question = data[i]['question_text']
            if data[i]['i_answer'] != 'None':
                answer = data[i]['i_answer']
            elif data[i]['s_answer'] != 'None':
                answer = data[i]['s_answer']
            else:
                answer = 'None'
            tags = data[i]['tags']
            folders = data[i]['folders']
            f.write("********************Question******************\n")
            f.write(question)
            f.write("\n")
            f.write("********************Response******************\n")
            f.write(answer)
            f.write("\n")
            f.write("********************Tags******************\n")
            f.write(tags)
            f.write("\n")
            f.write("********************Folders******************\n")
            f.write(folders)
            f.write("\n")
        f.close()


    def generate_faq_from_notes(self, task):
        # Connect to the database using the specified parameters
        con = mdb.connect(DB_PARAMS['host'], DB_PARAMS['user'], DB_PARAMS['password'])
        cur = con.cursor(mdb.cursors.DictCursor)

        q = "USE {0};".format(task['db_name'])
        cur.execute(q)

        q = "SELECT max(no_upvotes_on_note) AS max_no_upvotes from notes;"    
        cur.execute(q)
        data = cur.fetchall()
        max_upvotes_count = data[0]['max_no_upvotes']

        upvotes_on_note = []
        unique_collaborations = []
        follow_up_thread = []

        for i in range(1, max_upvotes_count+1):
            q = """SELECT distinct count(*) AS count from notes where no_upvotes_on_note = %d """ %(i)
            cur.execute(q)
            data = cur.fetchall()
            count = data[0]['count']
            upvotes_on_note.extend(np.repeat(i, count))

        upvotes_on_note = np.array(upvotes_on_note)     
        threshold_for_upvotes_on_note = np.percentile(upvotes_on_note, self.config_inst.thresholds['upvotes_on_note'])

        print "Done with no_upvotes_on_note"

        q = "SELECT max(no_unique_collaborations) AS max_no_unique_collabs from notes;"    
        cur.execute(q)
        data = cur.fetchall()
        max_no_unique_collabs = data[0]['max_no_unique_collabs']

        for i in range(1, max_no_unique_collabs+1):
            q = """SELECT distinct count(*) AS count from notes where no_unique_collaborations = %d """ %(i)
            cur.execute(q)
            data = cur.fetchall()
            count = data[0]['count']
            unique_collaborations.extend(np.repeat(i,count))

        unique_collaborations = np.array(unique_collaborations)     
        threshold_for_unique_collaborations = np.percentile(unique_collaborations, self.config_inst.thresholds['unique_collaborations_on_note'])

        print "Done with no_unique_collaborations"

        q = "SELECT max(length_of_follow_up_thread) AS max_length_of_follow_up_thread from notes;"    
        cur.execute(q)
        data = cur.fetchall()
        max_len_follow_up_thread = data[0]['max_length_of_follow_up_thread']
        
        for i in range(1, max_len_follow_up_thread+1):
            q = """SELECT distinct count(*) AS count from notes where length_of_follow_up_thread = %d """ %(i)
            cur.execute(q)
            data = cur.fetchall()
            count = data[0]['count']
            follow_up_thread.extend(np.repeat(i,count))

        follow_up_thread = np.array(follow_up_thread)     
        threshold_for_follow_up_thread= np.percentile(follow_up_thread, self.config_inst.thresholds['follow_up_thread_on_note'])
        print "Thresholds are", threshold_for_upvotes_on_note,threshold_for_unique_collaborations, threshold_for_follow_up_thread

        print "Done with length_of_follow_up_thread"

        q = """SELECT distinct count(*) AS count from notes where no_upvotes_on_note >= %d and no_unique_collaborations >= %d and length_of_follow_up_thread >= %d and tags NOT LIKE "%%logistics%%" and folders NOT LIKE "%%logistics%%" """ %(threshold_for_upvotes_on_note, threshold_for_unique_collaborations,threshold_for_follow_up_thread )

        cur.execute(q)
        data = cur.fetchall()
        count = data[0]['count']
        print "Count of qualifying notes", count
     
        q = """SELECT notes_text, tags, folders from notes where no_upvotes_on_note >= %d and no_unique_collaborations >= %d and length_of_follow_up_thread >= %d and tags NOT LIKE "%%logistics%%" and folders NOT LIKE "%%logistics%%" """ %(threshold_for_upvotes_on_note, threshold_for_unique_collaborations,threshold_for_follow_up_thread)

        cur.execute(q)
        data = cur.fetchall()
        f = open('faq_notes.txt', 'w')

        for i in range(len(data)):
            note = data[i]['notes_text']
            tags = data[i]['tags']
            folders = data[i]['folders']
            f.write("********************Note******************\n")
            f.write(note)
            f.write("\n")
            f.write("********************Tags******************\n")
            f.write(tags)
            f.write("\n")
            f.write("********************Folders******************\n")
            f.write(folders)
            f.write("\n")
        f.close()


        
