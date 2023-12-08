import zipfile
from datetime import datetime
import sys
import os

def get_backup_filename(backup_label):
    # NAME backup_label + "_" current datetime
    
    now = datetime.now() # Get the current dateime
        
    # remove the decimal seconds from now
    now = str(now)
    dt, junk = now.split(".")

    dt = dt.replace(":", "") # remove colons from time portion of dt
    dt = dt.replace(" ", "_") # replaces spaces in dt with underscores

    ret = backup_label + "_" + dt
    return ret


"""
Adds subdirectories to a list to be scanned later
"""
def get_all_files_in_directory_iterative(directory_to_backup):

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


def backup(directory_to_backup, location_to_save_backup, backup_label):
    # ZIP UP directory_to_backup if directory_to_backup exists exists
    dir_exists = os.path.isdir(directory_to_backup)
    if not dir_exists:
        print("Error: directory to backup does not exist")
        sys.exit()
 
    zip_filename_with_path = location_to_save_backup + "/" + get_backup_filename(backup_label) + ".zip"
    
    #print("zip filename with path: "+zip_filename_with_path) # DEBUG

    zip = zipfile.ZipFile(zip_filename_with_path, "w", zipfile.ZIP_DEFLATED)
    
    all_files = get_all_files_in_directory_iterative(directory_to_backup)
    
    for f in all_files:
        #filename_with_path = directory_to_backup+"/"+f 
        try:
            zip.write(f)
        except PermissionError:
            print("Error: could not read file"+f)
        print("added "+f)
    zip.close()



# TODO - BACKUP ROTATION  (e.g. only keep most recent 5 copies) 

# TODO - POSSIBLE TO VERIFY INTEGRITY OF ZIP FILE?

# TODO - SCHEDULING, E.G. RUN AT 2AM, ETC.

# TODO - WOULD BE BETTER TO READ FROM A CONFIG FILE AND LOOP THROUGH...
backup("/path/to/directory_to_backup", "/path/to/save/backup", "Backup Label") 
