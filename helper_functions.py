# functions I could reuse


def build_pretty_table(json_structure, auto_table):
    '''

    :param json_structure: A json structure converted into a dictionary via json.load like the one used for netstats.
                            Should have leafs mainly
            auto_table: Table in a recursive manner
    :return: a pretty table with all the columns for that json structure

    This would be the code to invoke:

    auto_table = PrettyTable ()
    for stat in theJSON["stats"]:
        for port in stat["ports"]:
            auto_table=helper_functions.build_pretty_table(port, auto_table)

    It will create the table but the challenge is that unless the data is identical the table wont be populated properly

    '''

    from prettytable import PrettyTable



    for key in json_structure.keys():
        if key not in auto_table.field_names:
            auto_table.add_column(key,[])
            #print("Added "+key)




    return(auto_table)

    '''
    If we wanted to dump the pretty table to a csv
 

    if (csv_file):
        print("A file will be created")

    # Dumping pretty table to a csv
    with open ( 'nic_inv.csv', 'w', newline='' ) as f_output:
        f_output.write ( table.get_csv_string () )
 
    '''


def populate_pretty_table(json_structure, auto_table):
    '''
    Receives the table with headers created with build_pretty_table and populates it.
    :param json_structure:
    :param auto_table:
    :return: Fully populated pretty table
    '''

    columns = auto_table.field_names
    #print ( "Columns:", columns )

    my_list=[]

    for key in json_structure.keys():
        #print("Evaluating key "+key)
        if key not in columns:
            print("Error key "+key+" not found")
        else:
            my_list.append(json_structure[key])

    # Adding all the files to the table on a single row
    auto_table.add_row(my_list)



