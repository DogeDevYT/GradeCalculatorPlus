import csv
import time
from collections import defaultdict
from os.path import exists
from statistics import mean

from selenium import webdriver

summative_weighting_factor = 0.75
formative_weighting_factor = 0.25


# main entering grades loop function
def grade_loop(grade_list):
    while True:
        grade = input('Enter a number grade (no fractions or percentages!) (Type \'stop\' to stop the loop)')
        if grade != 'stop':
            grade_list.append(grade)
        else:
            break
    grade_list = [int(numeric_string) for numeric_string in grade_list]  # convert into integer list
    return grade_list


# function to calculate preEOC Average (also works for non EOC courses since EOC score is averaged with pre eoc average)
def average(summatives, formatives):
    # https://www.wikihow.com/Calculate-Weighted-Average
    return (mean(summatives) * summative_weighting_factor) + (
            mean(formatives) * formative_weighting_factor)


# function to calculate the lowest grade possible and still get the desired score
def lowest_grade(desiredGrade, summatives, formatives):
    # (sum(summatives) + x)/(len(summatives)+1) = desiredGrade

    missing_grade_summative = ((desiredGrade * (len(summatives) + 1)) - sum(summatives))
    missing_grade_formative = ((desiredGrade * (len(formatives) + 1)) - sum(formatives))
    return [missing_grade_summative, missing_grade_formative]


# abstracts the pre EOC grade calculating process to make it easier for me to code
def calculate_grade_final(summatives, formatives, course):
    print('Please enter your FORMATIVE grades:')
    formatives = grade_loop(formatives)
    # formatives = [int(numeric_string) for numeric_string in formatives] #convert into integer list
    print('FORMATIVES for ' + str(course) + ':' + str(formatives))
    print('Please enter your SUMMATIVE grades:')
    summatives = grade_loop(summatives)
    # summatives = [int(numeric_string) for numeric_string in summatives] #convert into integer list
    print('SUMMATIVES for ' + str(course) + ':' + str(summatives))
    # https://www.wikihow.com/Calculate-Weighted-Average
    average_grade = average(summatives, formatives)
    print('Average for ' + str(course) + ':' + str(average_grade))
    desired_end_grade = int(input('What is your LOWEST acceptable end grade for ' + str(course) + '? '))
    lowest_grade_possible = lowest_grade(desired_end_grade, summatives, formatives)
    # print(lowest_grade_possible)
    print('For ' + str(course) + ' the lowest grade you can get on a summative is a ' + str(
        lowest_grade_possible[0]) + ' and the lowest grade you can get on a formative is a ' + str(
        lowest_grade_possible[1]) + ' to get a ' + str(desired_end_grade) + ' in the course')
    save = input('Would you like to save these results? (y/n)')
    if save == 'yes' or save == 'y':
        if exists('results.csv'):
            with open('results.csv', 'a') as results:  # if the file already exists I just append to the end of it
                # with new data instead of overwriting with write file mode
                writer = csv.writer(results)
                # Format: course name, current grade, desired lowest grade, lowest summative, lowest formative,
                # current summatives
                writer.writerow(
                    [str(course), average_grade, desired_end_grade, lowest_grade_possible[0], lowest_grade_possible[1],
                     summatives, formatives])
                print('Results successfully written!')
        else:
            with open('results.csv', 'w') as results:
                writer = csv.writer(results)
                # Format: course name, current grade, desired lowest grade, lowest summative, lowest formative,
                # current summatives
                writer.writerow(
                    ['Course Name', 'Current Grade', 'Desired Lowest Grade', 'Lowest Summative', 'Lowest Formative',
                     'Current Summatives', 'Current Formatives'])
                writer.writerow(
                    [str(course), average_grade, desired_end_grade, lowest_grade_possible[0], lowest_grade_possible[1],
                     summatives, formatives])
                print('Results successfully written!')
    else:
        print('Ok...Not saving results for ' + str(course))
        print('You should consider it though because it allows you to perform EOC analysis later')


def course_loop():
    while True:
        # reset summative and formative grades for every run of course selection
        summatives = []
        formatives = []
        print('Your options include: ')
        for course in courses:
            print(course + ', ', end="")
        print()  # Fix formatting after enabling weird printing
        next_course = input('What course would you like to calculate next? (Type \'stop\' to stop)')
        if next_course == 'stop':
            print('Goodbye!')
            exit(0)
        else:
            final_query = 'https://campus.forsyth.k12.ga.us/campus/nav-wrapper/student/portal/student/classroom' \
                          '/grades/student-grades?' + funky_url_parameters + 'classroomSectionID=' + str(
                courses[next_course])
            driver.get(final_query)
            calculate_grade_final(summatives, formatives, next_course)


def eoc_analysis():
    if exists('results.csv'):
        print('results.csv found, continuing')
        with open('results.csv', 'r') as results_file:
            csv_reader = csv.reader(results_file)
            rows = list(csv_reader)
            for course_data in range(2, len(rows), 2):  # selects only the courses in the csv table
                # current grade + x = desired*2
                # x = desired*2 - current grade
                lowest_grade_eoc = (int((rows[course_data][2])) * 2) - int(float(rows[course_data][1]))  # Have to
                # convert this to a float first because it's too long to be parsed as an int initially
                print('For ' + rows[course_data][0] + ' the lowest grade you can get on its EOC/EOCT is a ' + str(
                    lowest_grade_eoc))
    else:
        print('Did you remember to run the \'calculate your grades\' option first (1)')
        exit('results.csv not found, quitting!')


login_credentials = []

with open('login.txt', 'r') as login_file:
    for line in login_file:
        if line == '\n':  # checking for empty lines which would mean a missing username/password
            exit('Missing/improper configuration of login.txt, Aborting...')
        login_credentials.append(line.strip())  # getting rid of newline character

# parse through courses.txt and input the courses and their ids into a dictionary(<course name>, <course id in
# Infinite Campus>)
courses = defaultdict(list)
with open("courses.txt") as courses_file:
    for line in courses_file:
        course_name, course_id = line.split(":",
                                            1)  # parse through courses.txt and split it at the colon to get the
        # course name and course id on Infinite Campus
        courses[course_name] = course_id.strip()  # I've got to remove the newline character (\n)

# parse through query.txt to get other necessary parameters for the end URL query
funky_url_parameters = ''
with open("query.txt") as query_file:
    for line in query_file:
        funky_url_parameters += line
        funky_url_parameters += "&"

################################
#           TESTING            #
#                              #
#            ZONE              #
#                              #
################################

# EXAMPLE QUERY

# make final query final_query = 'https://campus.forsyth.k12.ga.us/campus/nav-wrapper/student/portal/student
# /classroom/grades/student-grades?' + funky_url_parameters + "classroomSectionID=" + str(courses["AP American Lit
# Lang/Comp"]) open course in selenium driver.get(final_query)


print('Welcome to GradeCalculatorPlus!')
print('You can either calculate your grades (1) or analyze your eoc possibilities (2)')
option = int(input('Which option do you want? (1/2)'))

if option == 1:
    # Create a webdriver object (basically the browser to use)
    # REMEMBER TO DOWNLOAD CHROMEDRIVER EXECUTABLE AND PLACE IT IN THE SAME DIRECTORY AS THE PYTHON SCRIPT!!
    driver = webdriver.Chrome(executable_path='chromedriver.exe')

    # Navigate to the webpage containing the button
    driver.get('https://campus.forsyth.k12.ga.us/campus/portal/students/forsyth.jsp')

    # Locate the button by its ID and click on it to start SSO process
    driver.find_element_by_id('samlLoginLink').click()

    # enter login data and submit
    driver.find_element_by_id('userNameInput').send_keys(login_credentials[0])
    time.sleep(1)
    driver.find_element_by_id('passwordInput').send_keys(login_credentials[1])
    time.sleep(1)
    driver.find_element_by_id('submitButton').click()

    # wait for load
    time.sleep(5)

    # navigate to grades page
    driver.find_element_by_id('menu-toggle-button').click()
    time.sleep(1)
    driver.find_element_by_partial_link_text('Grades').click()
    # I need to put chromedriver script here otherwise the course_loop() function won't be able to find the driver
    # object
    course_loop()
if option == 2:
    eoc_analysis()
