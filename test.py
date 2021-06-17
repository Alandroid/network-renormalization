
infile = 'karate_network.txt'

links_file = open(infile, 'r+')

new = []
for row in links_file:
    first = row.split(' ')[0]
    second = row.split(' ')[1]
    new.append((int(first)-1, int(second)-1))

with open("karate_network_2.txt", "w") as output:
    for row in new:
        s = " ".join(map(str, row))
        output.write(s+'\n')