'''
This file executes all functions for processing of courses - cleaning data, inserting into mysql database,
fetching required records, converting them into networks and generating all statisitcs.
The function main takes 2 arguments, namely 'getStats' (set True if we
want to calculate the network statistics for all the courses, stored as 'statistics.csv' under each course
offering in data directory) and 'combine'(set True if we want to compare the stats across various courses
for each network parameter, stored as '{attribute_name}'.csv in data/stats).
All constants are defined in 'constants.py'.
'''

#import getpass
#import argparse
from piazza_data_parser import DataParser, Graph, logger, FAQGenerator
from filter_low_edit_distance import get_minimal_update_pairs

import os
from piazza_analytics.constants import COURSES,DB_PARAMS,DATA_DIRECTORY

def main(generate_network, generate_faq):
    
    script_dir = os.path.dirname(__file__)
    res_dir    = os.path.join(script_dir, '..')
    
    stats_dir    = os.path.join(res_dir,'stats')
    figures_dir  = os.path.join(res_dir,'figures')
    faq_dir      = os.path.join(res_dir,'FAQ')
    data_dir     = DATA_DIRECTORY

    if not os.path.exists(stats_dir):
        os.makedirs(stats_dir)

    if not os.path.exists(figures_dir):
        os.makedirs(figures_dir)

    if not os.path.exists(faq_dir):
        os.makedirs(faq_dir)
        
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    tasks = []
    for c in COURSES:
        print c
        crs_stats_dir = os.path.join(stats_dir, c)
        crs_figures_dir = os.path.join(figures_dir, c)
        crs_faq_dir = os.path.join(faq_dir, c)
        crs_data_dir = os.path.join(data_dir, c)
        
        if not os.path.exists(crs_stats_dir):
            os.makedirs(crs_stats_dir)

        if not os.path.exists(crs_figures_dir):
            os.makedirs(crs_figures_dir)

        if not os.path.exists(crs_faq_dir):
            os.makedirs(crs_faq_dir)
            
        if not os.path.exists(crs_data_dir):
            os.makedirs(crs_data_dir)
            

        for root, dirs, files in os.walk(crs_data_dir):
            for course_dir in sorted(dirs,key=lambda d:d[-2:]):
                print "course_dir", course_dir
                # We append slash only because code we'll call
                # doesn't use join:
                input_dir = os.path.join(root,course_dir) + '/'
                tasks.append({'input':input_dir,'db_name':c+course_dir, 'course':c, 'course_dir': course_dir})
                if not os.path.exists('../figures/'):
                    os.makedirs('../figures/')


    for task in tasks:
        print "Starting phase 1..."
        print "Processing course_dir ", task['course_dir']
        print "Setting up the schema..."
        stats_path = os.path.join(crs_stats_dir, task['course_dir'])
        if not os.path.exists(stats_path):
            os.makedirs(stats_path)
            
        figures_path = os.path.join(crs_figures_dir, task['course_dir'])
        
        if not os.path.exists(figures_path):
            os.makedirs(figures_path)

        endorsement_network_out_file =  os.path.join(stats_path, "endorsement_network.csv")
        upvotes_network_out_file = os.path.join(stats_path, "upvotes_network.csv")
        combined_network_out_file = os.path.join(stats_path, "combined_network.csv")
        endorsement_nodes = os.path.join(stats_path, "endorsement_nodes.csv")
        upvotes_nodes = os.path.join(stats_path,"upvotes_nodes.csv")
        combined_nodes = os.path.join(stats_path,"combined_nodes.csv")
        endorsement_network_filtered_out_file = os.path.join(stats_path, "endorsement_network_filtered.csv")
        upvotes_network_filtered_out_file = os.path.join(stats_path, "upvotes_network_filtered.csv")
        combined_network_filtered_out_file = os.path.join(stats_path, "combined_network_filtered.csv")
        interaction_nodes = os.path.join(stats_path, "interaction_nodes.csv")
        interaction_network_out_file = os.path.join(stats_path, "interaction_network.csv")
        interaction_nodes_flipped = os.path.join(stats_path, "interaction_nodes_flipped.csv")
        interaction_network_flipped_out_file = os.path.join(stats_path, "interaction_network_flipped.csv")
        study_group_out_file = os.path.join(stats_path, "study_group.csv")

        parser = DataParser()
        parser.fetch(task, 
                    endorsement_network_out_file, 
                    upvotes_network_out_file, 
                    combined_network_out_file, 
                    endorsement_nodes, 
                    upvotes_nodes, 
                    combined_nodes, 
                    endorsement_network_filtered_out_file, 
                    upvotes_network_filtered_out_file, 
                    combined_network_filtered_out_file, 
                    interaction_nodes, 
                    interaction_network_out_file, 
                    interaction_nodes_flipped, 
                    interaction_network_flipped_out_file, 
                    study_group_out_file)

        if generate_network:
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

        if generate_faq:
            print "Generating FAQs"
            faq_generator = FAQGenerator()
            faq_generator.generate_faq_from_questions(task)
            faq_generator.generate_faq_from_notes(task)

            faq_generator.generate_faq_from_questions_for_instructors(task)
            faq_generator.generate_faq_from_notes_for_instructors(task)

        low_edit_uids = get_minimal_update_pairs(task)
        low_info_density = stats_path+"low_edit_uids.txt"
        fi = open(low_info_density, "w")
        for k,v in low_edit_uids.items():
            fi.write("Student:")
            fi.write(str(k))
            fi.write("\nEdit distances:\n")
            for item in v:
                fi.write(str(item)+ "    ")
            fi.write("\n")


if __name__ == '__main__':
    main(generate_network= False, generate_faq = True)

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
