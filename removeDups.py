import sys
import os
import csv

if len(sys.argv) == 2:
  file = sys.argv[1]
else:
  print('Datei angeben!')
  exit()

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, file)

with open(filename, 'r', newline='') as tsv_data:
  headReader = csv.reader(tsv_data, delimiter='\t')
  head = next(headReader)
  infos = next(headReader)
  notes = next(headReader)
print(head)

keys = []
entries = []

with open(filename, 'r', newline='') as tsv_data:
  reader = csv.DictReader(tsv_data, delimiter='\t')
  rowcount = 0
  for row in reader:
    if rowcount > 1:
        if row['EN'] not in keys:
            keys.append(row['EN'])
            entries.append(row)
    rowcount += 1 

with open(filename, 'w', newline='') as tsv_data:
    fieldnames = head
    rowwriter = csv.writer(tsv_data, delimiter='\t')
    writer = csv.DictWriter(tsv_data, delimiter='\t', fieldnames=fieldnames)
    writer.writeheader()  
    rowwriter.writerow(infos)
    rowwriter.writerow(notes)
    writer.writerows(entries)

