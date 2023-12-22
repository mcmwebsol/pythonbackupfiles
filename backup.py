import zipfile
from datetime import datetime
import sys
import os
import csv

def get_backup_filename(backup_label, number_of_copies_to_keep, location_to_save_backup):
    # NAME backup_label + "_" counter : counter, E.G. 1..10
    #print("num to keep: "+str(number_of_copies_to_keep))
    dt = 1
    oldest = 0
    all_copies = []
    if number_of_copies_to_keep:
        for i in range(1, number_of_copies_to_keep+1):
            #print("i:"+str(i))
            f1 = location_to_save_backup + "/" + backup_label + "_" + str(i)+".zip" 
            if os.path.isfile(f1): # file exists
                #print("file exists")
                if i < number_of_copies_to_keep:
                    #print(str(i)+" is less than "+str(number_of_copies_to_keep))
                    if not oldest:
                        oldest = i
                    else:
                        all_copies.append(i)
                    dt = i
                else:
                    all_copies.append(i)
                    if oldest:
                        filename = location_to_save_backup + "/" + backup_label + "_" + str(oldest)+".zip"
                        os.remove(filename) # delete oldest one
                        #print("deleted "+filename)

                        # RENAME OTHERS, E.G. 1..10
                        #print("all_copies:", *all_copies)
                        ct = 1
                        for a in all_copies:
                            # RENAME FILES, E.G. 1..10
                            target = location_to_save_backup + "/" + backup_label + "_" + str(a) + ".zip"
                            destination = location_to_save_backup + "/" + backup_label + "_" + str(ct)+".zip" 
                            os.rename(target, destination)
                            ct += 1


                        # SET dt
                        dt = ct
                        break
            else:
                #print("File "+f1+" does NOT exist")
                dt = i
                break
    #print("dt after: "+str(dt))
                

    ret = backup_label + "_" + str(dt)
    return ret



def get_all_files_in_directory_iterative(directory_to_backup):
    """
    Adds subdirectories to a list to be scanned later
    """

    directores_to_scan = list()
    directores_to_scan.append(directory_to_backup)

    dir_list_new = list()

    ct = 0
    while True:
        #print("ct="+str(ct))
        if ct >= len(directores_to_scan):
            break

        current_directory = directores_to_scan[ct]
        #print("curr dir: "+current_directory)
        try:
            dir_list = os.listdir(current_directory) # returns a list
        except PermissionError:
            print("Error: could not read directory "+current_directory+" access denied")
            continue
        for i in dir_list:
            #print("F: "+current_directory+"/"+i) # DEBUG
            is_dir = os.path.isdir(current_directory+"/"+i)
            if (is_dir):
                directores_to_scan.append(current_directory+"/"+i)               
                #print("Added directory to list: "+current_directory+"/"+i)  
            else:
                dir_list_new.append(current_directory+"/"+i)  #  INCLUDE FULL PATH HERE  
        ct += 1

    return dir_list_new



def backup(directory_to_backup, location_to_save_backup, backup_label, number_of_copies_to_keep=-1):
    """
    Backup

    :param directory_to_backup: directory to backup (target, full path, no trailing slash)
    :type directory_to_backup: str

    :param location_to_save_backup: directory to save backup to (destination, full path, no trailing slash)
    :type location_to_save_backup: str

    :param backup_label: label for backup (name of backup file, excluding .zip at the end)
    :type backup_label: str

    :param number_of_copies_to_keep: maximum number of copies of backup to keep
    :type number_of_copies_to_keep: int (-1 for no limit)

    :return: None
    :rtype: None
    """

    # ZIP UP directory_to_backup if directory_to_backup exists exists
    dir_exists = os.path.isdir(directory_to_backup)
    if not dir_exists:
        print("Error: directory to backup "+directory_to_backup+" does not exist")
        sys.exit()

    zip_filename_with_path = location_to_save_backup + "/" + get_backup_filename(backup_label, number_of_copies_to_keep, location_to_save_backup) + ".zip"
    
    #print("zip filename with path: "+zip_filename_with_path) # DEBUG

    zip = zipfile.ZipFile(zip_filename_with_path, "w", zipfile.ZIP_DEFLATED)
    
    all_files = get_all_files_in_directory_iterative(directory_to_backup)
    
    for f in all_files:
        #filename_with_path = directory_to_backup+"/"+f 
        try:
            zip.write(f)
        except PermissionError:
            print("Error: could not read file"+f)
        #print("added "+f)

    # VERIFY INTEGRITY OF ZIP FILE    
    try:
        # Reads all the files in the archive and check their CRC's and file headers. Returns the name of the first bad file, or else return None.
        zip_okay = zip.testzip()         
        if zip_okay is not None:
            print("Zipfile error in "+zip_okay)  # TODO - IS THIS WORKING CORRECTLY?
    except Exception as ex:
        print("Exception:", ex)
        zip.close()
        sys.exit(1)    

    # CLOSE THE ZIP FILE    
    zip.close()
    



 
# TODO - SCHEDULING, E.G. RUN AT 2AM, ETC.

# READ FROM A CONFIG FILE AND LOOP 
CONFIG_FILENAME = "./mcm_py_backup_config.csv" # NOTE: PATH IS RELATIVE TO DIRECTORY PROGRAM IS RUN IN, NOT RELATIVE TO ACTUAL LOCATION OF THE PROGRAM
try:
    with open(CONFIG_FILENAME, "r") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # skip lines that don't have 4 elements
            # also skip comments (start with #)
            if len(row) == 4 and row[0][0] != "#":
                # READ FROM CONFIG FILE HERE AND FILL IN BELOW 4 VARS:
                #print(row)
                directory_to_backup = row[0] 
                location_to_save_backup = row[1] 
                backup_label = row[2] 
                number_of_copies_to_keep = int(row[3])
                #print("VARS: ", directory_to_backup, location_to_save_backup, backup_label, number_of_copies_to_keep)
                backup(directory_to_backup, location_to_save_backup, backup_label, int(number_of_copies_to_keep))

except FileNotFoundError:
    sys.exit("Configuration file "+CONFIG_FILENAME+" not found")
