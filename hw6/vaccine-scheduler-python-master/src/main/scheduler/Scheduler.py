import sys
from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime
import random


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None

#EXTRA CREDIT_PASSWORD CHECKING 

def checking_password(password):

    if len(password) < 8:
        print ("Password at least 8 characters!")
        return False
    #97, 123 lower case
    l_tmp = [ord(s) in range(97,123) for s in password]
    #65,91 upper case
    u_tmp = [ord(s) in range(65,91) for s in password]

    if (any(l_tmp) and any(u_tmp)) == False:
        print ("Password should use both uppercase and lowercase letters!")
        return False
    #48,58 number
    n_tmp = [ord(s) in range(48,58) for s in password]

    if any(n_tmp) == False:
        print ("Password should use at least one number!") 
        return False
    x_tmp = [x in ["!","@","#","?"] for x in password]
    if any(x_tmp) == False:
        print ('Password at least one special character,"!","@","#","?"')
        return False
    return True


def create_patient(tokens):
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    username = tokens[1]
    password = tokens[2]

    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    try:
        patient = Patient(username, salt=salt, hash=hash)
        # save to patient information to our database
        try:
            patient.save_to_db()
        except:
            print("Create failed, Cannot save")
            return
        print(" *** Account created successfully *** ")
    except pymssql.Error:
        print("Create failed")
        return   

def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error:
        print("Error occurred when checking username")
        cm.close_connection()
    cm.close_connection()
    return False


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    username = tokens[1]
    password = tokens[2]
    
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    try:
        caregiver = Caregiver(username, salt=salt, hash=hash)
        # save to caregiver information to our database
        try:
            caregiver.save_to_db()
        except:
            print("Create failed, Cannot save")
            return
        print(" *** Account created successfully *** ")
    except pymssql.Error:
        print("Create failed")
        return


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error:
        print("Error occurred when checking username")
        cm.close_connection()
    cm.close_connection()
    return False


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("Already logged-in!")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        try:
            patient = Patient(username, password=password).get()
        except:
            print("Get Failed")
            return
    except pymssql.Error:
        print("Error occurred when logging in")

    # check if the login was successful
    if patient is None:
        print("Please try again!")
    else:
        print("Patient logged in as: " + username)
        current_patient = patient



def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("Already logged-in!")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        try:
            caregiver = Caregiver(username, password=password).get()
        except:
            print("Get Failed")
            return
    except pymssql.Error:
        print("Error occurred when logging in")

    # check if the login was successful
    if caregiver is None:
        print("Please try again!")
    else:
        print("Caregiver logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    if len(tokens) ==0:
        print("Please try again!")
        return
    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    
    # Show caregivers available for the date
    cm = ConnectionManager(); conn = cm.create_connection(); cursor = conn.cursor(as_dict=True)
    get_caregiver_for_date = "SELECT Username FROM Availabilities WHERE Time = %s"
    try:
        d = datetime.datetime(year, month, day)
        cursor.execute(get_caregiver_for_date,d)
        results = cursor.fetchall()
        if len(results)!=0:
            print('The following caregiver(s) are available for your selected date:')
            for row in results:  
                print("   ", row['Username'])               
        else:
            print('There is no caregiver available for your selected date.')
        cm.close_connection()
    except pymssql.Error:
        print("Error occurred when getting Caregivers")
        cm.close_connection()
    # Show vaccine stock
    cm = ConnectionManager(); conn = cm.create_connection(); cursor = conn.cursor(as_dict=True)
    get_vaccine_stock= "SELECT * FROM Vaccines"
    try:
        cursor.execute(get_vaccine_stock)
        results = cursor.fetchall()
        if len(results)!=0:
            print ('The following vaccine are available currently:')
            for row in results:
                print("   ",row['Name'], " has ", row['Doses'], " doses available")
        else:
            print('There is no vaccine in stock now.')
        cm.close_connection()
    except pymssql.Error:
        print("Error occurred when getting Caregivers")
        cm.close_connection()
        
    # return

def reserve(tokens):
    # check if the current logged-in user is a patient
    global current_patient
    if current_patient is None:
        print("Please login as a patient first!")
        return
    if len(tokens) != 3:
        print("Please try again!")
        return

    date = tokens[1]
    vaccine = tokens[2]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])

    # Check caregiver's availablility
    # Show caregivers available for the date
    cm = ConnectionManager(); conn = cm.create_connection(); cursor = conn.cursor(as_dict=True)

    get_caregiver_for_date = "SELECT Username FROM Availabilities WHERE Time =  %s"
    try:
        d = datetime.datetime(year, month, day)
        cursor.execute(get_caregiver_for_date,d)
        results=cursor.fetchall()
        if len(results)>0:
            caregiver_list = [row['Username'] for row in results]
            caregiver_assigned = random.choice(caregiver_list)             
        else:
            print('There is no caregiver available for your selected date. Please check schedule and choose another date.')
            cm.close_connection()
            return
    except pymssql.Error:
        print("Error occurred when getting Caregivers in reservation")
        cm.close_connection()
        return
    cm.close_connection()  # Close the connection of Availability here
    # Check vaccine's doses
    cm = ConnectionManager(); conn = cm.create_connection(); cursor = conn.cursor()
    get_vaccine = "SELECT Name, Doses FROM Vaccines WHERE Name = %s"
    try:
        cursor.execute(get_vaccine,vaccine)
        records = cursor.fetchall()
        if len(records) == 0:
            print('We do not have the vaccine you chose. Please choose another vaccine.')  # Vaccine name not found
            cm.close_connection()
            return
        for row in records:
            avail_dose = row[1]
            if avail_dose > 0:
                # Update the vaccine's dose, as the reservation will be successful
                update_vaccine_availability = "UPDATE Vaccines SET Doses = " +str(avail_dose-1) +" WHERE name = \'" + vaccine + "\'"
                try:
                    cursor.execute(update_vaccine_availability)
                    conn.commit()
                except pymssql.Error:
                    print("Error occurred when updating vaccine availability after making a reservation")
                    cm.close_connection()
                cm.close_connection()
            else:  # dose = 0
                print('The vaccine you chose is not available. Please choose another vaccine.')  # Vaccine name found but dose is zero
                cm.close_connection()
                return
    except pymssql.Error:
        print("Error occurred when getting Vaccine in reservation")
        cm.close_connection()
    cm.close_connection()

    # All checking passed. Update database.
    # Update caregiver's availability
    cm = ConnectionManager(); conn = cm.create_connection(); cursor = conn.cursor()
    del_availability = "DELETE FROM Availabilities WHERE Username= %s and Time= %s"
    try:
        cursor.execute(del_availability,(caregiver_assigned,d))
        conn.commit()
    except pymssql.Error:
        print("Error occurred when updating caregiver availability after making a reservation")
        cm.close_connection()
    cm.close_connection()

    # Update the appointment table
    # First get the current max id
    cm = ConnectionManager(); conn = cm.create_connection(); cursor = conn.cursor()
    get_max_id = "SELECT MAX(appoint_ID) from Appointments"

    try:
        cursor.execute(get_max_id)
        results=cursor.fetchall()
        if results[0][0] is None:  # Or None. Need to debug
            app_id = 1
        else:
            app_id = int(results[0][0])+1
            print (app_id)
    except pymssql.Error:
        print("Error occurred when updating caregiver availability after making a reservation(get max id)")
        cm.close_connection()
        return
    # Then update appointment with the new id
    add_appointment = "INSERT INTO Appointments values(%d,%s,%s,%s,%s)"  
    try:
        cursor.execute(add_appointment,(app_id, d, caregiver_assigned, current_patient.username,vaccine))
        conn.commit()
    except pymssql.Error:
        print("Error occurred when insert new appointment")
        cm.close_connection()
    cm.close_connection()  
    
    print('You have successfully booked an appointment with caregiver', caregiver_assigned,'with Apointment ID:', str(app_id))


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    
    cm = ConnectionManager(); conn = cm.create_connection(); cursor = conn.cursor(as_dict=True)
    
    check_date = "SELECT Time from Availabilities where Time= %s and Username=%s "
    try:
        d = datetime.datetime(year, month, day)
        cursor.execute(check_date,(d,current_caregiver.username))
        results=cursor.fetchall()
        if len(results) == 0:
            add_availability = "INSERT INTO Availabilities VALUES (%s , %s)"
            try:
                cursor.execute(add_availability, (d, current_caregiver.username))
                conn.commit()
                print("Availability uploaded!")
            except pymssql.Error:
                print("Error occurred when updating caregiver availability")
                cm.close_connection()
            cm.close_connection()
        else:
            print("The date you uploaded already exist") 
            cm.close_connection()   
            return
    except ValueError:
        print("Please enter a valid date!")
    except pymssql.Error as db_err:
        print("Error occurred when uploading availability")
# Extra Credit Question Two
def cancel(tokens):
    global current_caregiver, current_patient
    if len(tokens) != 2:
        print("Please try again!")
        return
    if current_caregiver == None and current_patient == None:
        print('Please log in first!')
        return

    app_id = tokens[1]

    cm = ConnectionManager(); conn = cm.create_connection(); cursor = conn.cursor(as_dict=True)
    get_appointment = "SELECT * FROM Appointments WHERE Appoint_ID =  %s" 
    try:
        cursor.execute(get_appointment,app_id)
        results=cursor.fetchall()
        if len(results) > 0:                
            for row in results:
                caregiver_assigned = row['C_name']
                vaccine = row['V_name']
                date_chosen = row['Time']     
                
                # Update the table of Appointments
                del_appointment = "DELETE FROM Appointments WHERE Appoint_ID=%s" 
                try:
                    cursor.execute(del_appointment,app_id)
                    conn.commit()
                except pymssql.Error:
                    print("Error occurred when updating caregiver availability after making a reservation")
                    cm.close_connection()                
                cm.close_connection()  # Close the connection to Appointments

                # Update the table of Availability
                cm = ConnectionManager(); conn = cm.create_connection(); cursor = conn.cursor()
                ins_availability = "INSERT INTO Availabilities values(%s, %s)"  
                try:
                    cursor.execute(ins_availability,(date_chosen, caregiver_assigned))
                    conn.commit()
                except pymssql.Error:
                    print("Error occurred when updating caregiver availability after cancelling a reservation")
                    cm.close_connection()
                cm.close_connection()

                # update the table of vaccines
                cm = ConnectionManager(); conn = cm.create_connection(); cursor = conn.cursor()
                update_vaccine_availability = "UPDATE Vaccines SET Doses = Doses +1 WHERE name = %s" 
                try:
                    cursor.execute(update_vaccine_availability,vaccine)
                    conn.commit()
                except pymssql.Error:
                    print("Error occurred when updating vaccine availability after making a reservation")
                    cm.close_connection()
                cm.close_connection()      
                print("Your appointment with appointment ID ", app_id, " has been cancelled")      
        else:
            print('There is no appointment with this ID. Please check the appointment ID.')
            cm.close_connection()
            return
    except pymssql.Error:
        print("Error occurred when getting Caregivers in cancelling")
        cm.close_connection()
        return      

def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        try:
            vaccine = Vaccine(vaccine_name, doses).get()
        except:
            print("Failed to get Vaccine!")
            return
    except pymssql.Error:
        print("Error occurred when adding doses")

    # check 3: if getter returns null, it means that we need to create the vaccine and insert it into the Vaccines
    #          table

    if vaccine is None:
        try:
            vaccine = Vaccine(vaccine_name, doses)
            try:
                vaccine.save_to_db()
            except:
                print("Failed To Save")
                return
        except pymssql.Error:
            print("Error occurred when adding doses")
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            try:
                vaccine.increase_available_doses(doses)
            except:
                print("Failed to increase available doses!")
                return
        except pymssql.Error:
            print("Error occurred when adding doses")

    print("Doses updated!")


def show_appointments(tokens):
    global current_caregiver, current_patient

    if current_caregiver == None and current_patient == None:
        print('Please log in first!')
        return
    if current_caregiver != None:  # A caregiver is here
        cm = ConnectionManager(); conn = cm.create_connection(); cursor = conn.cursor(as_dict=True)
        get_app_Cname = "SELECT * from Appointments WHERE C_name=%s" 
        try:
            cursor.execute(get_app_Cname,current_caregiver.username)
            results = cursor.fetchall()
            if len(results) == 0:  # No appointment for the caregiver
                print('You have no appointment yet.')
                cm.close_connection()
                return
            else:
                print('You have the following appointment(s):')
                for row in results:
                    print('Appointment', row['Appoint_ID'], 'with Vaccine' ,row['V_name'], 'on' ,row['Time'],'for patient',row['P_name'])
        except pymssql.Error:
            print("Error occurred when updating getting appointments for caregiver")
            cm.close_connection()
            return
        cm.close_connection()
            
    elif current_patient != None:  # A patient is here
        cm = ConnectionManager(); conn = cm.create_connection(); cursor = conn.cursor(as_dict=True)
        get_app_Pname = "SELECT * from Appointments WHERE P_name=%s" 
        try:
            cursor.execute(get_app_Pname,current_patient.username)
            results = cursor.fetchall()
            if len(results) == 0:  # No appointment for the patient
                print('You have no appointment yet.')
                cm.close_connection()
                return
            else:
                print('You have the following appointment(s):')
                for row in results:
                    print('Appointment', row['Appoint_ID'], 'with Vaccine' ,row['V_name'], 'on' ,row['Time'],'with caregiver',row['C_name'])
        except pymssql.Error:
            print("Error occurred when updating getting appointments for caregiver")
            cm.close_connection()
            return
        cm.close_connection()

def logout(tokens):
    global current_caregiver 
    current_caregiver = None
    global current_patient 
    current_patient = None

def start():
    stop = False
    while not stop:
        print()
        print(" *** Please enter one of the following commands *** ")
        print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
        print("> create_caregiver <username> <password>")
        print("> login_patient <username> <password>")  #// TODO: implement login_patient (Part 1)
        print("> login_caregiver <username> <password>")
        print("> search_caregiver_schedule <date>")  #// TODO: implement search_caregiver_schedule (Part 2)
        print("> reserve <date> <vaccine>") #// TODO: implement reserve (Part 2)
        print("> upload_availability <date>")
        print("> cancel <appointment_id>") #// TODO: implement cancel (extra credit)
        print("> add_doses <vaccine> <number>")
        print("> show_appointments")  #// TODO: implement show_appointments (Part 2)
        print("> logout") #// TODO: implement logout (Part 2)
        print("> Quit")
        print()
        response = ""
        print("> Enter: ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Type in a valid argument")
            break
        tokens = response.split(" ")
        
        #extra credit
        if tokens[0]=="create_caregiver" or tokens[0]=="create_patient":
            if checking_password(tokens[2]) == False:
                continue
                
      
        response = response.lower()
        
        if len(tokens) == 0:
            ValueError("Try Again")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Thank you for using the scheduler, Goodbye!")
            stop = True
        else:
            print("Invalid Argument")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
