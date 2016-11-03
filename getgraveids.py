import sys
import os.path
import urllib.request
import sqlite3 as sql
from bs4 import BeautifulSoup
from db import makeGraveDatabase, addRowToDatabase, extractBirth, extractDeath

problemchilds = []
CONNECT = True

if CONNECT:
    if not os.path.isfile('./graves.db'):
        makeGraveDatabase()


def findagravecitation(graveid):
    grave = {}
    grave['id'] = graveid

    url = 'http://www.findagrave.com/cgi-bin/fg.cgi?page=gr&GRid='
    url += str(graveid)
    grave['url'] = url

    with urllib.request.urlopen(url) as html:
        soup = BeautifulSoup(html.read(), "lxml")
    text = 'Find A Grave Memorial #'
    text += str(graveid) + '\nName: '
    name = soup.table.tr.td.find_next_siblings('td')[1].table.tr.get_text()
    text += name + '\nBirth: '
    grave['name'] = name

    # a sponsored grave has an extra row
    checkSponsor = soup.table.tr.td.find_next_siblings('td')[1].table.tr.find_next_siblings('tr')

    if "Birth" in checkSponsor[1].get_text():
        datatable = checkSponsor[1].td.tr.table.tr.find_all('tr')
    else:
        datatable = checkSponsor[2].td.tr.table.tr.find_all('tr')

    birth = datatable[0].find_all('td')[1]
    for i,br in enumerate(birth.find_all('br')):
        if i==0: br.replace_with('\nBirthplace: ')
        else: br.replace_with(', ')
    text += birth.get_text() +'\nDeath: '

    extractBirth(grave, birth.get_text())

    death = datatable[1].find_all('td')[1]
    for i,br in enumerate(death.find_all('br')):
        if i==0: br.replace_with('\nDeath place: ')
        else: br.replace_with(', ')
    text += death.get_text() +'\n'

    extractDeath(grave, death.get_text())

    burialBox = datatable[4].td
    for i,br in enumerate(burialBox.find_all('br')):
        br.replace_with('\n')
    blines = burialBox.get_text().split('\n');
    try:
        burial = blines[2]
        grave['burial'] = burial

        text += "Burial: " + burial
        for line in blines[3:]:
            if "Plot" in line:
                text += '\n' + line
                grave['plot'] = line.replace('Plot: ','')
            elif line != '': text += ', ' + line
    except:
        text += burial.get_text()
        problemchilds.append(graveid)

    if datatable[2].get_text() != '':
        text += '\nMore information available on webpage.'
        grave['more_info'] = True

    if CONNECT:
        addRowToDatabase(grave)

    return text


graveids = []
numcites = 0
numids = 0

# # read from gedcom
# with open('tree.ged', encoding='utf8') as ged:
#     for line in ged.readlines():
#         numcites+=1
#         if '_LINK ' in line and 'findagrave.com' in line:
#             for unit in line.split('&'):
#                 if 'GRid=' in unit:
#                     if unit[5:-1] not in graveids:
#                         graveids.append(unit[5:-1])
#                         #print(graveids[numids])
#                         numids+=1

# read from text file
with open('input.txt', encoding='utf8') as txt:
    for line in txt.readlines():
        numcites+=1
        if 'findagrave.com' in line:
            for unit in line.split('&'):
                if 'GRid=' in unit:
                    if unit[5:-1] not in graveids:
                        graveids.append(unit[5:-1])
                        numids+=1
        elif line not in graveids:
                graveids.append(line)
                numids+=1

parsed = 0
failedids = []
for i,gid in enumerate(graveids):
    try:
        print(str(i+1) + ' of ' + str(numids))
        print(findagravecitation(gid)+'\n\n')
        parsed += 1
    except:
        print('Unable to parse Memorial #'+str(gid)+'!\n\n')
        print("Error:", sys.exc_info()[0])
        failedids.append(gid)

out = 'Successfully parsed ' + str(parsed) + ' of '
out += str(len(graveids))
print(out)
if len(problemchilds)>0:
    print('\nProblem childz were:', problemchilds)

# with open('results.txt', 'w') as f:
#     f.write(out + '\n')
#     f.write('\nProblem childz were:\n')
#     f.write('\n'.join(problemchilds))
#     f.write('\nUnable to parse:\n')
#     f.write('\n'.join(failedids))
