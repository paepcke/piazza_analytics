import json, time
import os
import sys
import logging
from datetime import datetime
import MySQLdb as mdb
from constants import *
import numpy as np
from configuration import *
from clustering import *
from utils import *
import scipy

# from topics_extraction_with_nmf_lda import *
class FAQGenerator:

    def __init__(self):
        self.config_inst = Config()
        self.faq_root_dir = "../FAQ/"
        self.clustering_inst = Clustering()
        #self.logger = Logger()

    def generate_faq_from_questions(self, task):
        print "Generating FAQs for students.."

        # Connect to the database using the specified parameters
        con = mdb.connect(DB_PARAMS['host'], DB_PARAMS['user'], DB_PARAMS['password'])
        cur = con.cursor(mdb.cursors.DictCursor)

        q = "USE {0};".format(task['db_name'])
        cur.execute(q)

        q = "SELECT max(no_upvotes_on_question) AS max_no_upvotes from questions;"
        cur.execute(q)
        data = cur.fetchall()
        max_upvotes_count = data[0]['max_no_upvotes']

        q = "SELECT max(no_upvotes_on_i_answer) AS max_no_upvotes from questions;"
        cur.execute(q)
        data = cur.fetchall()
        max_upvotes_count_on_ianswer = data[0]['max_no_upvotes']

        q = "SELECT max(no_upvotes_on_s_answer) AS max_no_upvotes from questions;"
        cur.execute(q)
        data = cur.fetchall()
        max_upvotes_count_on_sanswer = data[0]['max_no_upvotes']

        q = "SELECT max(no_unique_collaborations) AS max_no_unique_collabs from questions;"
        cur.execute(q)
        data = cur.fetchall()
        max_no_unique_collabs = data[0]['max_no_unique_collabs']

        q = "SELECT max(length_of_follow_up_thread) AS max_length_of_follow_up_thread from questions;"
        cur.execute(q)
        data = cur.fetchall()
        max_len_follow_up_thread = data[0]['max_length_of_follow_up_thread']

        q = "SELECT max(unique_views) AS max_unique_views from questions;"
        cur.execute(q)
        data = cur.fetchall()
        max_unique_views = data[0]['max_unique_views']
        faq_stats = self.faq_root_dir + task['course'] + '/' + 'faq_stats_questions' + task['course_dir'] +'.txt'
        fo = open(faq_stats, 'w')
        if max_upvotes_count != None and max_upvotes_count_on_ianswer != None and max_upvotes_count_on_sanswer != None and max_no_unique_collabs != None and max_len_follow_up_thread != None and max_unique_views != None:
            if max_upvotes_count != 0 and max_upvotes_count_on_ianswer != 0 and max_upvotes_count_on_sanswer != 0 and max_no_unique_collabs != 0 and max_len_follow_up_thread != 0 and max_unique_views != 0:
                upvotes_on_que = []
                upvotes_on_i_answer = []
                upvotes_on_s_answer = []
                unique_collaborations = []
                follow_up_thread = []
                unique_views = []

                for i in range(1, max_upvotes_count+1):
                    q = """SELECT distinct count(*) AS count from questions where no_upvotes_on_question = %d """ %(i)
                    cur.execute(q)
                    data = cur.fetchall()
                    count = data[0]['count']
                    upvotes_on_que.extend(np.repeat(i, count))

                upvotes_on_que = np.array(upvotes_on_que)
                faq_plot_upvotes_on_que = self.faq_root_dir + task['course'] + '/' + 'faq_upvotes_on_ques' + task['course_dir'] +'.png'
                plot_data_distribution(upvotes_on_que,faq_plot_upvotes_on_que)
                fo.write("No_of_upvotes on questions\n")
                fo.write("Skew\n")
                fo.write(str(scipy.stats.skew(upvotes_on_que)))
                fo.write("\nKurtosis\n")
                fo.write(str(scipy.stats.kurtosis(upvotes_on_que))+"\n")
                threshold_for_upvotes_on_que = np.percentile(upvotes_on_que, self.config_inst.thresholds['upvotes_on_que'])

                # print "Done with no_upvotes_on_question"

                for i in range(1, max_upvotes_count_on_ianswer+1):
                    q = """SELECT distinct count(*) AS count from questions where no_upvotes_on_i_answer = %d """ %(i)
                    cur.execute(q)
                    data = cur.fetchall()
                    count = data[0]['count']
                    upvotes_on_i_answer.extend(np.repeat(i,count))

                upvotes_on_i_answer = np.array(upvotes_on_i_answer)
                faq_plot_upvotes_on_i_answer = self.faq_root_dir + task['course'] + '/' + 'faq_upvotes_on_i_answer' + task['course_dir'] +'.png'
                plot_data_distribution(upvotes_on_i_answer,faq_plot_upvotes_on_i_answer)
                fo.write("No_of_upvotes on i answer\n")
                fo.write("Skew\n")
                fo.write(str(scipy.stats.skew(upvotes_on_i_answer)))
                fo.write("\nKurtosis\n")
                fo.write(str(scipy.stats.kurtosis(upvotes_on_i_answer))+"\n")
                threshold_for_upvotes_on_i_answer = np.percentile(upvotes_on_i_answer, self.config_inst.thresholds['upvotes_on_i_answer'])
                # print "Done with no_upvotes_on_i_answer"

                for i in range(1, max_upvotes_count_on_sanswer+1):
                    q = """SELECT distinct count(*) AS count from questions where no_upvotes_on_s_answer = %d """ %(i)
                    cur.execute(q)
                    data = cur.fetchall()
                    count = data[0]['count']
                    upvotes_on_s_answer.extend(np.repeat(i,count))

                upvotes_on_s_answer = np.array(upvotes_on_s_answer)
                faq_plot_upvotes_on_s_answer = self.faq_root_dir + task['course'] + '/' + 'faq_upvotes_on_s_answer' + task['course_dir'] +'.png'
                plot_data_distribution(upvotes_on_s_answer,faq_plot_upvotes_on_s_answer)
                fo.write("No_of_upvotes on s answer\n")
                fo.write("Skew\n")
                fo.write(str(scipy.stats.skew(upvotes_on_s_answer)))
                fo.write("\nKurtosis\n")
                fo.write(str(scipy.stats.kurtosis(upvotes_on_s_answer))+"\n")
                threshold_for_upvotes_on_s_answer = np.percentile(upvotes_on_s_answer, self.config_inst.thresholds['upvotes_on_i_answer'])

                # print "Done with no_upvotes_on_s_answer"

                for i in range(1, max_no_unique_collabs+1):
                    q = """SELECT distinct count(*) AS count from questions where no_unique_collaborations = %d """ %(i)
                    cur.execute(q)
                    data = cur.fetchall()
                    count = data[0]['count']
                    unique_collaborations.extend(np.repeat(i,count))

                unique_collaborations = np.array(unique_collaborations)
                faq_plot_no_unique_collaborations = self.faq_root_dir + task['course'] + '/' + 'faq_unique_collaborations' + task['course_dir'] +'.png'
                plot_data_distribution(upvotes_on_s_answer,faq_plot_upvotes_on_s_answer)
                fo.write("No of unique collaborations\n")
                fo.write("Skew\n")
                fo.write(str(scipy.stats.skew(upvotes_on_s_answer)))
                fo.write("\nKurtosis\n")
                fo.write(str(scipy.stats.kurtosis(upvotes_on_s_answer))+"\n")
                threshold_for_unique_collaborations = np.percentile(unique_collaborations, self.config_inst.thresholds['unique_collaborations'])

                # print "Done with no_unique_collaborations"

                for i in range(1, max_len_follow_up_thread+1):
                    q = """SELECT distinct count(*) AS count from questions where length_of_follow_up_thread = %d """ %(i)
                    cur.execute(q)
                    data = cur.fetchall()
                    count = data[0]['count']
                    follow_up_thread.extend(np.repeat(i,count))

                follow_up_thread = np.array(follow_up_thread)
                faq_plot_follow_up_thread = self.faq_root_dir + task['course'] + '/' + 'faq_follow_up' + task['course_dir'] +'.png'
                plot_data_distribution(follow_up_thread,faq_plot_follow_up_thread)
                fo.write("Length of follow up threads\n")
                fo.write("Skew\n")
                fo.write(str(scipy.stats.skew(follow_up_thread)))
                fo.write("\nKurtosis\n")
                fo.write(str(scipy.stats.kurtosis(follow_up_thread))+"\n")

                threshold_for_follow_up_thread= np.percentile(follow_up_thread, self.config_inst.thresholds['follow_up_thread'])

                for i in range(1, max_unique_views+1):
                    q = """SELECT distinct count(*) AS count from questions where unique_views = %d """ %(i)
                    cur.execute(q)
                    data = cur.fetchall()
                    count = data[0]['count']
                    unique_views.extend(np.repeat(i,count))

                unique_views = np.array(unique_views)

                faq_plot_unique_views= self.faq_root_dir + task['course'] + '/' + 'faq_unique_views' + task['course_dir'] +'.png'
                plot_data_distribution(unique_views,faq_plot_unique_views)
                fo.write("Unique views\n")
                fo.write("Skew\n")
                fo.write(str(scipy.stats.skew(unique_views)))
                fo.write("\nKurtosis\n")
                fo.write(str(scipy.stats.kurtosis(unique_views))+"\n")

                threshold_for_unique_views = np.percentile(unique_views, self.config_inst.thresholds['unique_views'])

                print "Thresholds for number of upvotes on question, number of upvotes on i_answer, number of votes of student answer, number of unique collaborations, length of follow up thread, unique views are:", threshold_for_upvotes_on_que,threshold_for_upvotes_on_i_answer,threshold_for_upvotes_on_s_answer,threshold_for_unique_collaborations, threshold_for_follow_up_thread, threshold_for_unique_views

                q = """SELECT distinct count(*) AS count from questions where no_upvotes_on_question >= %d and (no_upvotes_on_i_answer >= %d or no_upvotes_on_s_answer >= %d) and no_unique_collaborations >= %d and length_of_follow_up_thread >= %d and unique_views >= %d and tags NOT LIKE "%%logistics%%" and folders NOT LIKE "%%logistics%%" and folders NOT LIKE "%%office_hours%%" and tags NOT LIKE "%%office_hours%%" """%(threshold_for_upvotes_on_que,threshold_for_upvotes_on_i_answer, threshold_for_upvotes_on_s_answer, threshold_for_unique_collaborations,threshold_for_follow_up_thread, 3* threshold_for_unique_views)
                cur.execute(q)
                data = cur.fetchall()
                count = data[0]['count']
                print "Number of questions that qualified for student FAQ:", count

                q = """SELECT question_text, subject, i_answer, s_answer, tags, folders from questions where no_upvotes_on_question >= %d and (no_upvotes_on_i_answer >= %d or no_upvotes_on_s_answer >= %d) and no_unique_collaborations >= %d and length_of_follow_up_thread >= %d and unique_views >= %d and tags NOT LIKE "%%logistics%%" and folders NOT LIKE "%%logistics%%" and folders NOT LIKE "%%office_hours%%" and tags NOT LIKE "%%office_hours%%" """%(threshold_for_upvotes_on_que,threshold_for_upvotes_on_i_answer, threshold_for_upvotes_on_s_answer, threshold_for_unique_collaborations,threshold_for_follow_up_thread, 3* threshold_for_unique_views)

                cur.execute(q)
                data = cur.fetchall()
                faq_file = self.faq_root_dir + task['course'] + '/' + 'faq_questions_' + task['course_dir'] +'.txt'
                f = open(faq_file, 'w')
                questions_list = []
                titles_list = []
                for i in range(len(data)):
                    question = data[i]['question_text']
                    refined_question = question.decode("utf8")
                    questions_list.append(refined_question)
                    title = data[i]['subject']
                    try:
                        index_element = title.index("$$")
                    except ValueError:
                        index_element = None

                    if index_element != None:
                        title = title[:index_element-1] +title[index_element+1 :]

                    titles_list.append(title)

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
        # print "Clustering the questions that qualified for FAQs"
        # self.clustering_inst.clustering(task, questions_list, titles_list)
        # topics_extraction(task, questions_list, titles_list)

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

        q = "SELECT max(no_unique_collaborations) AS max_no_unique_collabs from notes;"
        cur.execute(q)
        data = cur.fetchall()
        max_no_unique_collabs = data[0]['max_no_unique_collabs']

        q = "SELECT max(length_of_follow_up_thread) AS max_length_of_follow_up_thread from notes;"
        cur.execute(q)
        data = cur.fetchall()
        max_len_follow_up_thread = data[0]['max_length_of_follow_up_thread']

        q = "SELECT max(unique_views) AS max_unique_views from notes;"
        cur.execute(q)
        data = cur.fetchall()
        max_unique_views = data[0]['max_unique_views']

        faq_stats = self.faq_root_dir + task['course'] + '/' + 'faq_stats_notes' + task['course_dir'] +'.txt'
        fo = open(faq_stats, 'w')
        if max_upvotes_count != None and max_no_unique_collabs != None and max_len_follow_up_thread != None and max_upvotes_count != 0 and max_no_unique_collabs != 0 and max_len_follow_up_thread != 0 and max_unique_views != 0:
            upvotes_on_note = []
            unique_collaborations = []
            follow_up_thread = []
            unique_views = []

            for i in range(1, max_upvotes_count+1):
                q = """SELECT distinct count(*) AS count from notes where no_upvotes_on_note = %d """ %(i)
                cur.execute(q)
                data = cur.fetchall()
                count = data[0]['count']
                upvotes_on_note.extend(np.repeat(i, count))

            upvotes_on_note = np.array(upvotes_on_note)
            faq_plot_upvotes_on_note = self.faq_root_dir + task['course'] + '/' + 'faq_upvotes_on_note' + task['course_dir'] +'.png'
            plot_data_distribution(upvotes_on_note,faq_plot_upvotes_on_note)
            fo.write("No_of_upvotes on notes\n")
            fo.write("Skew\n")
            fo.write(str(scipy.stats.skew(upvotes_on_note)))
            fo.write("\nKurtosis\n")
            fo.write(str(scipy.stats.kurtosis(upvotes_on_note))+"\n")

            threshold_for_upvotes_on_note = np.percentile(upvotes_on_note, self.config_inst.thresholds['upvotes_on_note'])

            # print "Done with no_upvotes_on_note"

            for i in range(1, max_no_unique_collabs+1):
                q = """SELECT distinct count(*) AS count from notes where no_unique_collaborations = %d """ %(i)
                cur.execute(q)
                data = cur.fetchall()
                count = data[0]['count']
                unique_collaborations.extend(np.repeat(i,count))

            unique_collaborations = np.array(unique_collaborations)

            faq_plot_unique_collaborations = self.faq_root_dir + task['course'] + '/' + 'faq_unique_collaborations_note' + task['course_dir'] +'.png'
            plot_data_distribution(unique_collaborations,faq_plot_unique_collaborations)
            fo.write("Unique collaborations on notes\n")
            fo.write("Skew\n")
            fo.write(str(scipy.stats.skew(unique_collaborations)))
            fo.write("\nKurtosis\n")
            fo.write(str(scipy.stats.kurtosis(unique_collaborations))+"\n")

            threshold_for_unique_collaborations = np.percentile(unique_collaborations, self.config_inst.thresholds['unique_collaborations_on_note'])

            # print "Done with no_unique_collaborations"

            for i in range(1, max_len_follow_up_thread+1):
                q = """SELECT distinct count(*) AS count from notes where length_of_follow_up_thread = %d """ %(i)
                cur.execute(q)
                data = cur.fetchall()
                count = data[0]['count']
                follow_up_thread.extend(np.repeat(i,count))

            follow_up_thread = np.array(follow_up_thread)

            faq_plot_follow_up_thread = self.faq_root_dir + task['course'] + '/' + 'faq_follow_up_thread_note' + task['course_dir'] +'.png'
            plot_data_distribution(follow_up_thread,faq_plot_follow_up_thread)
            fo.write("Follow up thread on notes\n")
            fo.write("Skew\n")
            fo.write(str(scipy.stats.skew(follow_up_thread)))
            fo.write("\nKurtosis\n")
            fo.write(str(scipy.stats.kurtosis(follow_up_thread))+"\n")

            threshold_for_follow_up_thread= np.percentile(follow_up_thread, self.config_inst.thresholds['follow_up_thread_on_note'])

            for i in range(1, max_unique_views+1):
                q = """SELECT distinct count(*) AS count from notes where unique_views = %d """ %(i)
                cur.execute(q)
                data = cur.fetchall()
                count = data[0]['count']
                unique_views.extend(np.repeat(i,count))

            unique_views = np.array(unique_views)

            faq_plot_unique_views = self.faq_root_dir + task['course'] + '/' + 'faq_unique_views_note' + task['course_dir'] +'.png'
            plot_data_distribution(unique_views,faq_plot_unique_views)
            fo.write("unique_views on notes\n")
            fo.write("Skew\n")
            fo.write(str(scipy.stats.skew(unique_views)))
            fo.write("\nKurtosis\n")
            fo.write(str(scipy.stats.kurtosis(unique_views))+"\n")

            threshold_for_unique_views= np.percentile(unique_views, self.config_inst.thresholds['unique_views'])
            print "Thresholds for number of upvotes on note, number of unique collaborations, length of follow up thread, unique_views are:", threshold_for_upvotes_on_note,threshold_for_unique_collaborations, threshold_for_follow_up_thread, threshold_for_unique_views

            # print "Done with length_of_follow_up_thread"

            q = """SELECT distinct count(*) AS count from notes where no_upvotes_on_note >= %d and no_unique_collaborations >= %d and length_of_follow_up_thread >= %d and unique_views >= %d and tags NOT LIKE "%%logistics%%" and folders NOT LIKE "%%logistics%%" and folders NOT LIKE "%%office_hours%%" and tags NOT LIKE "%%office_hours%%" """%(threshold_for_upvotes_on_note, threshold_for_unique_collaborations,threshold_for_follow_up_thread, threshold_for_unique_views)

            cur.execute(q)
            data = cur.fetchall()
            count = data[0]['count']
            print "Number of notes that qualified for student FAQ", count

            q = """SELECT notes_text, tags, folders from notes where no_upvotes_on_note >= %d and no_unique_collaborations >= %d and length_of_follow_up_thread >= %d and unique_views >= %d and tags NOT LIKE "%%logistics%%" and folders NOT LIKE "%%logistics%%" and folders NOT LIKE "%%office_hours%%" and tags NOT LIKE "%%office_hours%%" """%(threshold_for_upvotes_on_note, threshold_for_unique_collaborations,threshold_for_follow_up_thread, threshold_for_unique_views)

            cur.execute(q)
            data = cur.fetchall()
            faq_file = self.faq_root_dir + task['course'] + '/' + 'faq_notes_' + task['course_dir'] +'.txt'
            f = open(faq_file, 'w')
            # f = open('faq_notes.txt', 'w')

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


####################################################################################################################

    def generate_faq_from_questions_for_instructors(self, task):
        print "Generating FAQs for insructors..."
        # Connect to the database using the specified parameters
        con = mdb.connect(DB_PARAMS['host'], DB_PARAMS['user'], DB_PARAMS['password'])
        cur = con.cursor(mdb.cursors.DictCursor)

        q = "USE {0};".format(task['db_name'])
        cur.execute(q)

        q = "SELECT max(no_upvotes_on_question) AS max_no_upvotes from questions;"
        cur.execute(q)
        data = cur.fetchall()
        max_upvotes_count = data[0]['max_no_upvotes']

        q = "SELECT max(no_upvotes_on_i_answer) AS max_no_upvotes from questions;"
        cur.execute(q)
        data = cur.fetchall()
        max_upvotes_count_on_ianswer = data[0]['max_no_upvotes']

        q = "SELECT max(no_upvotes_on_s_answer) AS max_no_upvotes from questions;"
        cur.execute(q)
        data = cur.fetchall()
        max_upvotes_count_on_sanswer = data[0]['max_no_upvotes']

        q = "SELECT max(no_unique_collaborations) AS max_no_unique_collabs from questions;"
        cur.execute(q)
        data = cur.fetchall()
        max_no_unique_collabs = data[0]['max_no_unique_collabs']

        q = "SELECT max(length_of_follow_up_thread) AS max_length_of_follow_up_thread from questions;"
        cur.execute(q)
        data = cur.fetchall()
        max_len_follow_up_thread = data[0]['max_length_of_follow_up_thread']

        if max_upvotes_count != None and max_upvotes_count_on_ianswer != None and max_upvotes_count_on_sanswer != None and max_no_unique_collabs != None and max_len_follow_up_thread != None:
            if max_upvotes_count != 0 and max_upvotes_count_on_ianswer != 0 and max_upvotes_count_on_sanswer != 0 and max_no_unique_collabs != 0 and max_len_follow_up_thread != 0:
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
                threshold_for_upvotes_on_que = np.percentile(upvotes_on_que, self.config_inst.thresholds_for_instructors['upvotes_on_que'])

                # print "Done with no_upvotes_on_question"

                for i in range(1, max_upvotes_count_on_ianswer+1):
                    q = """SELECT distinct count(*) AS count from questions where no_upvotes_on_i_answer = %d """ %(i)
                    cur.execute(q)
                    data = cur.fetchall()
                    count = data[0]['count']
                    upvotes_on_i_answer.extend(np.repeat(i,count))

                upvotes_on_i_answer = np.array(upvotes_on_i_answer)
                threshold_for_upvotes_on_i_answer = np.percentile(upvotes_on_i_answer, self.config_inst.thresholds_for_instructors['upvotes_on_i_answer'])

                # print "Done with no_upvotes_on_i_answer"

                for i in range(1, max_upvotes_count_on_sanswer+1):
                    q = """SELECT distinct count(*) AS count from questions where no_upvotes_on_s_answer = %d """ %(i)
                    cur.execute(q)
                    data = cur.fetchall()
                    count = data[0]['count']
                    upvotes_on_s_answer.extend(np.repeat(i,count))

                upvotes_on_s_answer = np.array(upvotes_on_s_answer)
                threshold_for_upvotes_on_s_answer = np.percentile(upvotes_on_s_answer, self.config_inst.thresholds_for_instructors['upvotes_on_i_answer'])

                # print "Done with no_upvotes_on_s_answer"

                for i in range(1, max_no_unique_collabs+1):
                    q = """SELECT distinct count(*) AS count from questions where no_unique_collaborations = %d """ %(i)
                    cur.execute(q)
                    data = cur.fetchall()
                    count = data[0]['count']
                    unique_collaborations.extend(np.repeat(i,count))

                unique_collaborations = np.array(unique_collaborations)
                threshold_for_unique_collaborations = np.percentile(unique_collaborations, self.config_inst.thresholds_for_instructors['unique_collaborations'])

                # print "Done with no_unique_collaborations"

                for i in range(1, max_len_follow_up_thread+1):
                    q = """SELECT distinct count(*) AS count from questions where length_of_follow_up_thread = %d """ %(i)
                    cur.execute(q)
                    data = cur.fetchall()
                    count = data[0]['count']
                    follow_up_thread.extend(np.repeat(i,count))

                follow_up_thread = np.array(follow_up_thread)
                threshold_for_follow_up_thread= np.percentile(follow_up_thread, self.config_inst.thresholds_for_instructors['follow_up_thread'])
                print "Thresholds for number of upvotes on question, number of upvotes on i_answer, number of votes of student answer, number of unique collaborations, length of follow up thread are:", threshold_for_upvotes_on_que,threshold_for_upvotes_on_i_answer,threshold_for_upvotes_on_s_answer,threshold_for_unique_collaborations, threshold_for_follow_up_thread
                # print "Done with length_of_follow_up_thread"


                q = """SELECT distinct count(*) AS count from questions where no_upvotes_on_question >= %d and (no_upvotes_on_i_answer >= %d or no_upvotes_on_s_answer >= %d) and no_unique_collaborations >= %d and length_of_follow_up_thread >= %d""" %(threshold_for_upvotes_on_que,threshold_for_upvotes_on_i_answer, threshold_for_upvotes_on_s_answer, threshold_for_unique_collaborations,threshold_for_follow_up_thread )
                cur.execute(q)
                data = cur.fetchall()
                count = data[0]['count']
                print "Number of questions that qualified for instructors FAQ:", count

                q = """SELECT question_text, subject, i_answer, s_answer, tags, folders from questions where no_upvotes_on_question >= %d and (no_upvotes_on_i_answer >= %d or no_upvotes_on_s_answer >= %d) and no_unique_collaborations >= %d and length_of_follow_up_thread >= %d """ %(threshold_for_upvotes_on_que,threshold_for_upvotes_on_i_answer, threshold_for_upvotes_on_s_answer, threshold_for_unique_collaborations,threshold_for_follow_up_thread)

                cur.execute(q)
                data = cur.fetchall()
                faq_file = self.faq_root_dir + task['course'] + '/' + 'faq_questions_for_instructors' + task['course_dir'] +'.txt'
                f = open(faq_file, 'w')

                for i in range(len(data)):
                    question = data[i]['question_text']
                    title = data[i]['subject']
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

    def generate_faq_from_notes_for_instructors(self, task):

        # Connect to the database using the specified parameters
        con = mdb.connect(DB_PARAMS['host'], DB_PARAMS['user'], DB_PARAMS['password'])
        cur = con.cursor(mdb.cursors.DictCursor)

        q = "USE {0};".format(task['db_name'])
        cur.execute(q)

        q = "SELECT max(no_upvotes_on_note) AS max_no_upvotes from notes;"
        cur.execute(q)
        data = cur.fetchall()
        max_upvotes_count = data[0]['max_no_upvotes']

        q = "SELECT max(no_unique_collaborations) AS max_no_unique_collabs from notes;"
        cur.execute(q)
        data = cur.fetchall()
        max_no_unique_collabs = data[0]['max_no_unique_collabs']

        q = "SELECT max(length_of_follow_up_thread) AS max_length_of_follow_up_thread from notes;"
        cur.execute(q)
        data = cur.fetchall()
        max_len_follow_up_thread = data[0]['max_length_of_follow_up_thread']

        if max_upvotes_count != None and max_no_unique_collabs != None and max_len_follow_up_thread != None and max_upvotes_count != 0 and max_no_unique_collabs != 0 and max_len_follow_up_thread != 0:
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
            threshold_for_upvotes_on_note = np.percentile(upvotes_on_note, self.config_inst.thresholds_for_instructors['upvotes_on_note'])

            # print "Done with no_upvotes_on_note"

            for i in range(1, max_no_unique_collabs+1):
                q = """SELECT distinct count(*) AS count from notes where no_unique_collaborations = %d """ %(i)
                cur.execute(q)
                data = cur.fetchall()
                count = data[0]['count']
                unique_collaborations.extend(np.repeat(i,count))

            unique_collaborations = np.array(unique_collaborations)
            threshold_for_unique_collaborations = np.percentile(unique_collaborations, self.config_inst.thresholds_for_instructors['unique_collaborations_on_note'])

            # print "Done with no_unique_collaborations"

            for i in range(1, max_len_follow_up_thread+1):
                q = """SELECT distinct count(*) AS count from notes where length_of_follow_up_thread = %d """ %(i)
                cur.execute(q)
                data = cur.fetchall()
                count = data[0]['count']
                follow_up_thread.extend(np.repeat(i,count))

            follow_up_thread = np.array(follow_up_thread)
            threshold_for_follow_up_thread= np.percentile(follow_up_thread, self.config_inst.thresholds_for_instructors['follow_up_thread_on_note'])
            print "Thresholds for number of upvotes on note, number of unique collaborations, length of follow up thread are:", threshold_for_upvotes_on_note,threshold_for_unique_collaborations, threshold_for_follow_up_thread

            # print "Done with length_of_follow_up_thread"

            q = """SELECT distinct count(*) AS count from notes where no_upvotes_on_note >= %d and no_unique_collaborations >= %d and length_of_follow_up_thread >= %d """ %(threshold_for_upvotes_on_note, threshold_for_unique_collaborations,threshold_for_follow_up_thread )

            cur.execute(q)
            data = cur.fetchall()
            count = data[0]['count']
            print "Number of notes that qualified for instructors FAQ", count

            q = """SELECT notes_text, tags, folders from notes where no_upvotes_on_note >= %d and no_unique_collaborations >= %d and length_of_follow_up_thread >= %d """ %(threshold_for_upvotes_on_note, threshold_for_unique_collaborations,threshold_for_follow_up_thread)

            cur.execute(q)
            data = cur.fetchall()
            faq_file = self.faq_root_dir + task['course'] + '/' + 'faq_notes_for_instructors' + task['course_dir'] +'.txt'
            f = open(faq_file, 'w')

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
