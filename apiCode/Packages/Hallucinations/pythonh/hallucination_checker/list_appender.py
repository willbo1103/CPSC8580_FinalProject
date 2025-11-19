'''
want to be able to read in the current file and compare each package on the current hallucination list to 
all of the packages in the master hallucaination list.

for each line in master read. if this package not on list, appeand to list.

'''

PRIMARY_LIST = "primarylist.txt"
CURRENT_LIST = "../DS3reasonerhalluncinations.txt" # DS3chathalluncinations.txt DS3reasonerhalluncinations.txt

def main():

    writefile = open (PRIMARY_LIST, "r")
    readfile = open (CURRENT_LIST, "r")

    try:
        # open primary list and strip each line
        with open (PRIMARY_LIST, 'r') as primaryread:
            lines_in_primary = set(line.strip() for line in primaryread)

        # open current list for reacing and the primary list for appending
        with open (CURRENT_LIST, 'r') as currentlist, open (PRIMARY_LIST, 'a') as primaryappend:
            primaryappend.write("\n____________\n"+ CURRENT_LIST+ "\n____________\n")
            for current_line in currentlist:
                line_in_current = current_line.strip()
                if line_in_current not in lines_in_primary:
                    primaryappend.write("\n" + '"' + line_in_current + '"'+",")
                    "\"A word that needs quotation marks\""
                    lines_in_primary.add(line_in_current)
    except Exception as e:
        print(f"An error occurred: {e}")



if __name__ == "__main__":
    main()