# piazza_analytics
### Building meaningful Analytics from Piazza interactions
----------------------------------------------------------------------------------------------------------------------------------------------------------------
### What do we aim to achieve:
- Build a system for awarding fair credit to students based on their Piazza  participation by evaluating their contributions fairly and allowing instructors to configure the weightage given to each of the factors that have been considered for calculating the contribution of each student.
- Apply various techniques to identify "good questions" and "good notes" for building a FAQ that can be useful for subsequent offerings of the course.
- Apply the page rank algorithm in the forum participation setting to further enhance the evaluation of a student's participation

- - -

#### ***How to run this code?***
```
1. Git clone https://github.com/paepcke/piazza_downloads.git
```
```
2. cd piazza_downloads/src
```
```
3. Run this:
	python new_schema_piazza.py --p /path_to_data_folder/ -d database_name
```
_ _ _

*Can you show me an example ?*
```
$ python new_schema_piazza.py -p /Users/xyz/Documents/piazza_downloads/data_folder -d music101_db
```

***What are these arguments --p and --d ?***
- The first argument --p stands for path name and is compulsary and it must be a valid path to a folder containing class_content.json and users.json
- The second argument --d stands for database name and is optional. In case you do not provide the database name, the default database name is piazza_dataset


- - -
#### Now, here is all you need to know about the schema:

There are four tables for each of the courses that we analyze:
- ***class_content table:***
This table contains the entire dataset dump of interactions on Piazza (questions, notes, follow-ups, student responses, instructor responses, feedbacks; literally everything)
Each row of the class_content table contains the following:


| Field_name | Type| Meaning/ interpretation |
|--------|--------|------------|
|id	   |  varchar(255)       | id of the content|
|type  |varchar(255)		 | Type of content : One of the following types - question, s_answer (or student's response), i_answer (or instructor's response) , dupe (duplicate) , note, feedback, followup|
|     created	   | bigint(20)       | Time stamp when the entry was created
|user_id| varchar(255)| User id of the creator of the entry
|     subject	   | longtext       | Subject of the entry (if any)
|content|longtext| Content of the entry
|     status	   | varchar(255)       | Status of the entry e.g. private, active
|nr|int(11) | Unique identifier associated with the entry. Piazza/ Human readable content identifier, e.g. ?cid=421"
|     no_answer_followup   | int(11)       | Number of follow ups posted
|tags|longtext| tags associated with the post/ entry. e.g ["instructor-note", "logistics", "pin"]
|     children  | longtext       | ids of the children of the post/ entry (if any)
|is_root	   |  int(11)       | Denotes if the element if the root of a thread (e.g a note or the opening question of a thread)|
|     change_log_user_ids	   | longtext      | User ids of the poople involved in the thread
|unique_views|int(11)| Number of unique views on the entry/ post
|     no_upvotes_defunct	   | int(11)       | This is an unused field because so far we have only found 0 number of no_upvotes in the dataset.
|no_endorsements|int(11)| Number of endorsements on the post/ entry|
|     endorsers	   | text        | User ids of the endorsers|
|upvoters|text | User ids of the upvoters|
|     folders   |  varchar(255)      | Folders associated with the entry
|no_upvoters|int(11)   | Number of upvotes on the entry (equivalent to thanks)
|     role_of_poster  | varchar(255)       | Role of the poster (student or instructor). Most of the instructors would have been identified. However, because of lack of explicit information in the dataset about the role of the user, some of them are marked as "not available"
|     root_id  |varchar(255)       | Root id of the starting post in order to associate a child with its parent question. This is useful in creating the other tables

- ***users table:***
This table contains all the information about the participants (students/ instructors) in the course.
Each row of the users table contains the following:

| Field_name | Type| Meaning/ interpretation |
|--------|--------|----------------|
|id	   	  |  varchar(255)       | id of the user|
|answers |int(11)		 | Number of answers given by the user|
|asks	 |int(11)      | Number of questions asked by the user|
|posts| int(11)  | Total number of posts (contributions including follow ups and feedbacks) by the user|
|views| int(11)        | Total number of posts viewed by the user
|days_online|int(11)  |Number of days the user was online on the forum
|no_endorsed_answers| int(11)        | Number of answers written by the user that received at least one or more endorsements
|total_no_endorsements|int(11) | Total number of endorsements summed up over all the answers written by the user |
|role| varchar(255)| Role of the user : student / instructor. Since this information is not available explicitly in the database, therefore we have some entries as "not available"
|contribution|int(11) | Total contribution by the user (for assigning credit) based on a lot of factors|



- ***questions table:***
This table contains all the questions and their associated responses, feedbacks/ followups and other relevant statistics.
Each row of the questions table contains the following:

| Field_name | Type| Meaning/ interpretation |
|--------|--------|----------------|
|id	   	  |  varchar(255)       | id of the question|
|question_text |longtext		 | Body of the question|
|role_of_poster	 |varchar(255)       |Indicates whether the question was posted by a student or instructor|
|no_upvotes_on_question| int(11)  | Total number of upvotes on the question (equivalent to "good question" |
|i_answer| longtext       | Intsructor's response for the question (if any)
|s_answer|longtext  |Students' response for the question (if any)
|no_upvotes_on_i_answer| int(11)        |Number of upvotes on the instructor answer
|no_upvotes_on_s_answer|int(11) | Number of upvotes on the student answer
|no_unique_collaborations| int(11)| Number of unique collaborations involved in the thread (how many unique users participated in the thread)
|follow_up_thread|longtext | The entire follow up thread concatenated and separated by a delimiter|
|length_of_follow_up_thread |int(11) | Total number of follow_ups or feedbacks in the thread|
|folders|longtext | Folders associated with the question|
|tags|longtext  | Tags associated with the question|

- ***notes table:***
This table contains all the notes and their feedbacks/ followups and other relevant statistics.
Each row of the notes table contains the following:

| Field_name | Type| Meaning/ interpretation |
|--------|--------|----------------|
|id	   	  |  varchar(255)       | id of the note|
|notes_text |longtext		 | Body of the note|
|role_of_poster	 |varchar(255)       |Indicates whether the note was posted by a student or instructor|
|no_upvotes_on_note| int(11)  | Total number of upvotes on the note (equivalent to "good note" |
|no_unique_collaborations| int(11)| Number of unique collaborations involved in the thread (how many unique users participated in the thread)
|follow_up_thread|longtext | The entire follow up thread concatenated and separated by a delimiter|
|length_of_follow_up_thread |int(11) | Total number of follow_ups or feedbacks in the thread|
|folders|longtext | Folders associated with the note|
|tags|longtext  | Tags associated with the note|

Note: In the Config class, we have a credit dictionary, that is configurable by the instructors. Hence, the instructors can decide how much weightage is to be given to each of the factors that goes into evaluating the holistic contribution of the student in the class, e.g. weightage for number of questions asked, number of questions answered, number of endorsed answers, etc.

<!--just give the command python new_schema_piazza.py with the arguments described below:
		course1

				class_content.json
				users.json
			fall12
				class_content.json
				users.json
			summer13
				class_content.json
				users.json
			fall13
				class_content.json
				users.json
			spring15
				class_content.json
				users.json
			summer15
				class_content.json
				users.json
			fall16
				class_content.json
				users.json
		course2
			fall13
				class_content.json
				users.json
			spring15
				class_content.json
				users.json
	******************************

(where course1,course2,etc. are course names as defined in src/constants.py)-->


