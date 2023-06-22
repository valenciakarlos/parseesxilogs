# Perform a diff on files and highlights the differences
import difflib
import sys




def main():
    print("Args #="+str(sys.argv))
    if len(sys.argv) != 3:
        print("Please enter files to compare")
        exit()


    iteration1 = sys.argv[1]
    iteration2 = sys.argv[2]
    print("Comparing files " +iteration1 + " and " + iteration2)


    with open(iteration1) as first_iteration_file:
        lines1 = first_iteration_file.read().splitlines()
  #      lines1 = [line.strip() for line in lines1]
    with open(iteration2) as second_iteration_file:
        lines2 = second_iteration_file.read().splitlines()
   #     lines2 = [line.strip() for line in lines2]


#lines1=file1_text.strip().split('\n')
#lines2=file2_text.strip().split('\n')
# Generate the diff of the two outputs
    differ = difflib.Differ()
    diff = list(differ.compare(lines1, lines2))
    matcher = difflib.SequenceMatcher(None, lines1, lines2)
    #print('Diff:\n'.join(diff))

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        #print(tag)
        if tag=='equal':
            #print(f"equal {lines2[j1:j2]}")
            equal_lines=lines1[i1:i2]
            print('\n'.join(equal_lines))
            #print(f"{lines2[j1:j2]}\n")

        if tag == 'replace':
            # It could be that several lines are different. If we want to get more details we need to process line by line
            final_lines=lines2[j1:j2]
            #print(f"\033[43m{lines2[j1:j2]}\033[0m")
            org_lines=lines1[i1:i2]
            #print('\n'.join(org_lines))
            # Need to figure out a way to do a diff of several lines (i.e. several items on the list)
            #diff_lines=final_lines
            for ctr in range(0, len(final_lines)):
                # These will be two arrays with two elements 1st one name of the variable and second its value
                org_line=org_lines[ctr].split(":")
                final_line=final_lines[ctr].split(":")
                #diff_line=final_line
                if (org_line[0]==final_line[0]):   # Here we really have to mach as the value could be a float
                    org_value=int(org_line[1])
                    final_value=int(final_line[1])
                    diff_value=final_value-org_value
                    final_line[1]=str(diff_value)
                    final_lines[ctr]=':'.join(final_line)



            print('\033[33m' + '\n'.join(final_lines) + '\033[0m')
                    # Let's traverse each different line and find the difference in more detail (how to store so we can calculate difference?)


if __name__ == "__main__":
    main()