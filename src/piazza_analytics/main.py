'''
This file executes all functions for processing of courses - cleaning data, inserting into mysql database,
fetching required records, converting them into networks and generating all statisitcs.
The function main takes 2 arguments, namely 'getStats' (set True if we
want to calculate the network statistics for all the courses, stored as 'statistics.csv' under each course
offering in data directory) and 'combine'(set True if we want to compare the stats across various courses
for each network parameter, stored as '{attribute_name}'.csv in data/stats).
All constants are defined in 'constants.py'.
'''

import getpass
import argparse
# import progressbar
from piazza_data_parser import *

def main():
    # print 'Fetching records from sql..'
    if not os.path.exists('../stats'):
        os.makedirs('../stats')

    if not os.path.exists('../figures/'):
        os.makedirs('../figures/')

    if not os.path.exists('../FAQ/'):
        os.makedirs('../FAQ/')


    tasks = []
    for c in COURSES:
        print c
        if not os.path.exists('../stats/'+c):
            os.makedirs('../stats/'+c)

        if not os.path.exists('../figures/'+c):
            os.makedirs('../figures/'+c)

        if not os.path.exists('../FAQ/'+c):
            os.makedirs('../FAQ/'+c)

        for root, dirs, files in os.walk(DATA_DIRECTORY+c+'/'):
            for course_dir in sorted(dirs,key=lambda d:d[-2:]):
                print "course_dir", course_dir
                tasks.append({'input':root+course_dir+'/','db_name':c+course_dir, 'course':c, 'course_dir': course_dir})
                if not os.path.exists('../figures/'):
                    os.makedirs('../figures/')

    # bar = progressbar.ProgressBar(maxval=len(tasks), \
    # widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    # bar.start()
    # i=0
    # for task in tasks:
    #     bar.update(i+1)
    #     i+=1
    #     fetch(task)
    # bar.finish()

    # task = { "input": args.path_dataset, "db_name": args.db_name}

    # if not os.path.exists('../stats/'):
    #     os.makedirs('../stats/')

    for task in tasks:
        print "Starting phase 1..."
        print "Processing course_dir ", task['course_dir']
        print "Setting up the schema..."
        stats_path = "../stats/"+ task['course']+ '/' +task['course_dir']
        figures_path = "../figures/"+ task['course']+ '/' +task['course_dir']
        # print"DB", task['course']
        endorsement_network_out_file =  stats_path +"endorsement_network.csv"
        upvotes_network_out_file = stats_path +"upvotes_network.csv"
        combined_network_out_file = stats_path +"combined_network.csv"
        endorsement_nodes = stats_path +"endorsement_nodes.csv"
        upvotes_nodes = stats_path+"upvotes_nodes.csv"
        combined_nodes = stats_path+"combined_nodes.csv"

        # print endorsement_network_out_file
        # upvotes_network_out_file = "../stats/upvotes_network.csv"
        # combined_network_out_file = "../stats/combined_network.csv"
        # endorsement_nodes = "../stats/endorsement_nodes.csv"
        # upvotes_nodes = "../stats/upvotes_nodes.csv"
        # combined_nodes = "../stats/combined_nodes.csv"

        parser = DataParser()
        parser.fetch(task, endorsement_network_out_file, upvotes_network_out_file, combined_network_out_file, endorsement_nodes, upvotes_nodes, combined_nodes)

        print "Starting phase 2..."
        print "Generating the network..."
        endorsed_by_network = Graph(endorsement_network_out_file)

        path = stats_path + "endorsement_page_rank.csv"
        endorsed_by_network.get_page_rank(path)

        path = figures_path + "endorsement_network.png"
        # endorsed_by_network.draw_graph(path)
        logger.info("Created endorsement network")

        upvoted_by_network = Graph(upvotes_network_out_file)
        path = stats_path + "upvotes_page_rank.csv"
        upvoted_by_network.get_page_rank(path)
        path = figures_path + "upvote_network.png"
        # upvoted_by_network.draw_graph(path)
        logger.info("Created upvotes network")

        combined_network = Graph(combined_network_out_file)
        path = stats_path + "combined_page_rank.csv"
        combined_network.get_page_rank(path)
        path =  figures_path + "combined_network.png"
        # combined_network.draw_graph(path)
        logger.info("Created combined network")

        print "Starting phase 3..."
        print "Generating FAQs"
        faq_generator = FAQGenerator()
        faq_generator.generate_faq_from_questions(task)
        faq_generator.generate_faq_from_notes(task)

        faq_generator.generate_faq_from_questions_for_instructors(task)
        faq_generator.generate_faq_from_notes_for_instructors(task)


    # print 'Creating Network-----------------------------------------------'
    # for course in COURSES:
    #     print course
    #     if edgelist:
    #         path = DATA_DIRECTORY+course

    #         for root, dirs, files in os.walk(path):
    #             for course_dir in sorted(dirs,key=lambda d:d[-2:]):
    #                 print course_dir
    #                 convertToEdgeList(root+'/'+course_dir,course+course_dir,True)

    #     if getStats:
    #             print 'Calculating statistics for',course
    #             stats(course,divide=True,all_stats=True)


# if __name__ == '__main__':
#   pwd = DB_PARAMS.get('password', None)
#   if pwd is None:
#     DB_PARAMS['password'] = ''
#   elif len(DB_PARAMS['password']) == 0:
#     DB_PARAMS['password'] = getpass.getpass('MySQL password for user {0}:'.format(DB_PARAMS['user']))
#   main(edgelist=False, getStats=False, changePoint = True)

if __name__ == '__main__':
    main()

    #This part will be used for command line arguments to be used:
    # parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]), formatter_class=argparse.RawTextHelpFormatter)
    # parser.add_argument('-p', '--path-dataset',
    #                     help='Path of the folder containing the dataset eg. /Users/abc/Desktop/piazza_downloads/data_folder',
    #                     dest='path_dataset',
    #                     default=None)
    #
    # parser.add_argument('-d', '--dbname',
    #                     help='Database name',
    #                     dest='db_name',
    #                     default='piazza_dataset');
    #
    # args = parser.parse_args()
    #
    # if not os.path.isfile(args.path_dataset+"class_content.json") or not os.path.isfile(args.path_dataset+"users.json"):
    #     #if the last character in the path is not a forward slash, then we add one to avoid error
    #     if args.path_dataset[-1]!= '/':
    #         args.path_dataset+= '/'
    #     # If there isn't a valid file in the path, we throw an error
    #     if not os.path.isfile(args.path_dataset+"class_content.json") or not os.path.isfile(args.path_dataset+"users.json"):
    #         print "Unable to find valid class_content.json and/or users.json in this location"
    #         exit(1)
