# 3. Synthesize event pairs from event sequences in reviews

# -- Get events and types
# -- Order events based on heuristics
# -- Get event pairs (action-problem pairs)
# -- Write results to file


# Retrieve SVM results
import sys
import numpy as np
import csv
import sqlite3

cls_results = []
f = open('data/SVM_Results.csv', 'r')
for row in f:
    items = row.strip().split(',')
    EID = int(items[0])
    probs = [float(x) for x in items[1:]]
    C = np.argmax(probs)
    cls_results.append((EID, probs, C))
sys.stdout.write('# Datapoints: {}\n'.format(len(cls_results)))
sys.stdout.write('Last one: {}\n'.format(cls_results[-1]))
f.close()


# Retrieve events from DB
conn = sqlite3.connect('data/Caspar_Public.db')
curr = conn.cursor()
all_input = []
for x in curr.execute('select EID, SID, sentenceID, verb_type, event_type from Events'):
    all_input.append(x)
conn.close()
sys.stdout.write('#datapoints: {}\n'.format(len(all_input)))


# Get stories (sequences of events) as is

stories = []
curr_SID = 0
story = []
for row in all_input:
    if row[1] != curr_SID:
        if len(story)>0:
            stories.append(story)
        story = []
    curr_SID = row[1]
    story.append(row)
if len(story)>0:
    stories.append(story)
sys.stdout.write('#stories: {}\n'.format(len(stories)))



# Order events based on heuristics

new_stories = []
for raw_story in stories:
    new_story = []
    cur_sent_id = -1
    samesent = []
    story = raw_story[:]
    story.append((0,0,10000,None,None))
    for row in story:
        if row[2]!=cur_sent_id:
            if len(samesent) == 1:
                new_story.append(samesent[0])
            elif len(samesent)>1:
                # Order using Heuristics
                blacksheep = -1
                whitesheep = -1
                for eid, ev in enumerate(samesent):
                    if ev[4] == 'before' or (ev[4]=='when' and ev[3]=='VBG'):
                        blacksheep = eid
                    elif ev[4] != 'out' and ev[4] != ' non':
                        whitesheep = eid
                    else:
                        pass
                if whitesheep>=0:
                    new_story.append(samesent[whitesheep])
                for eid in range(len(samesent)):
                    if eid!=blacksheep and eid != whitesheep:
                        new_story.append(samesent[eid])
                if blacksheep>=0:
                    new_story.append(samesent[blacksheep])
            else:
                pass
            samesent = []
            cur_sent_id = row[2]
        samesent.append(row)
    new_stories.append(new_story)
sys.stdout.write('#correctly ordered stories: {}\n'.format(len(new_stories)))



# Get event pairs
pairs = []
for new_story in new_stories:
    if len(new_story) < 2:
        continue
    for eid in range(len(new_story) - 1):
        e1_id = int(new_story[eid][0])
        e2_id = int(new_story[eid + 1][0])
        e1_cls = cls_results[e1_id - 1][2]
        e2_cls = cls_results[e2_id - 1][2]

        if e1_cls == 1 and e2_cls == 2:
            pairs.append((e1_id, e2_id))
sys.stdout.write('#Ordered pairs: {}\n'.format(len(pairs)))


# Write IDs to file
file_path = 'data/ordered_pairs(SVM).csv'
f = open(file_path, 'w')
for e1_id, e2_id in pairs:
    f.write(str(e1_id)+','+str(e2_id)+'\n')
f.close()
sys.stdout.write('Written to file: {}\n'.format(file_path))




# Write text to file
heads_to_remove = ['to', 'if', 'because', 'since', 'as']
printable_events = []
for row in all_input:
    text = row[3]
    temp = text.lower()
    for head in heads_to_remove:
        if temp.startswith(head + ' '):
            text = text[len(head)+1:]
            break
    if not row[2].startswith('(missing)'):
        subj = row[2].replace('(','').replace(')','')
        if not subj in text:
            text = subj+' '+text
    printable_events.append((row[0],row[1],text))
sys.stdout.write('# Events: {}\n'.format(len(printable_events)))
with open('data/eventpairs.csv', 'w') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for e1, e2 in pairs:
        line = list(printable_events[e1-1]) + list(printable_events[e2-1])
        csvwriter.writerow([str(x) if type(x) is int else x.encode('utf-8', 'ignore') for x in line])
sys.stdout.write('Writen to file.')


