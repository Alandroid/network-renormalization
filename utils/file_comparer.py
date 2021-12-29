import filecmp
  
f1 = r"C:\Users\alana\Desktop\IC_Brum\Programas\Renormalization\network-renormalization\data\c_elegans_bin_edges_edges_0.txt"
f2 = r"C:\Users\alana\Desktop\IC_Brum\Programas\Renormalization\network-renormalization\data\c_elegans_bin.txt"
  

with open(f1, 'r') as file1:
    with open(f2, 'r') as file2:
        same = set(file1).intersection(file2)

same.discard('\n')

with open('some_output_file.txt', 'w') as file_out:
    for line in same:
        file_out.write(line)