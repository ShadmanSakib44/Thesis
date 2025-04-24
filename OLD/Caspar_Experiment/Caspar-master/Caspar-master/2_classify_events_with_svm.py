# 2: Classify each event into Action, Problem, or Neither, using SVM
# -- Training set was manually generated
# -- Train classifiers with training set
# -- Classify all events in DB

import sys
import sqlite3
import random
from sklearn import svm

# Retrieve training set
conn = sqlite3.connect('data/Caspar_Public.db')
curr = conn.cursor()
training_raw = []
for x in curr.execute('select EID, EventType, Subject, EventPhrase, Label from ManualLabels'):
    training_raw.append(x)
conn.close()
sys.stdout.write('#datapoints: {}\n'.format(len(training_raw)))

sentences = []
for row in training_raw:
    text = row[3]
    if text.lower().startswith('to ') or text.lower().startswith('if '):
        text = text[3:]
    if not row[2].startswith('(missing)'):
        subj = row[2].replace('(','').replace(')','')
        if not subj in text:
            text = subj+' '+text
    if len(text.split())<=2:
        if not ('crash' in text.lower() or 'lag' in text.lower()):
            continue
    sentences.append((row[0],text,row[4]))
sys.stdout.write('Got the texts: {}\n'.format(len(sentences)))

counts = [0,0,0]
for a, b, c in sentences:
    counts[int(c)]+=1
sys.stdout.write('{}\n'.format(counts))



# Get USE vectors of the events
import tensorflow as tf
import tensorflow_hub as hub
embed = hub.Module("https://tfhub.dev/google/universal-sentence-encoder-large/3")
embeddings = embed([row[1] for row in sentences])

vectors = []
sys.stdout.write('Getting the vectors...\n')

gpu_options = tf.compat.v1.GPUOptions(visible_device_list="0")
sess = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(gpu_options=gpu_options))
sess.run([tf.compat.v1.global_variables_initializer(), tf.compat.v1.tables_initializer()])
vectors = sess.run(embeddings)
sys.stdout.write('Got the vectors.\n')


# Creating training sets for the two SVM classifiers
training_input = []
training_output = []
training_output1 = []
training_output2 = []
count = [0, 0, 0]

sys.stdout.write('Processing...\n')
for ridx in range(len(sentences)):
    training_input.append([x for x in vectors[ridx]])
    row = sentences[ridx]
    #     out = [1,0,0]
    if int(row[2]) == 2:
        #         out = [0,0,1]
        training_output1.append(0)
        training_output2.append(1)
        count[2] += 1
    elif int(row[2]) == 1:
        #         out = [0,1,0]
        training_output1.append(1)
        training_output2.append(0)
        count[1] += 1
    else:
        training_output1.append(0)
        training_output2.append(0)
        count[0] += 1
    training_output.append(int(sentences[ridx][2]))
sys.stdout.write('Done.\n')


combined = list(zip(training_input, training_output, training_output1, training_output2))
random.shuffle(combined)
training_input, training_output, training_output1, training_output2 = zip(*combined)

NUM_EXAMPLES = 1247
testset_input = training_input[NUM_EXAMPLES:]
testset_output = training_output[NUM_EXAMPLES:]
testset_output1 = training_output1[NUM_EXAMPLES:]
testset_output2 = training_output2[NUM_EXAMPLES:]

trainset_input = training_input[:NUM_EXAMPLES]
trainset_output = training_output[:NUM_EXAMPLES]
trainset_output1 = training_output1[:NUM_EXAMPLES]
trainset_output2 = training_output2[:NUM_EXAMPLES]


# Training classifiers
sys.stdout.write('Fitting...\n')
clf1 = svm.SVC(gamma='scale', probability=True)
clf2 = svm.SVC(gamma='scale', probability=True)
clf1.fit(trainset_input, trainset_output1)
clf2.fit(trainset_input, trainset_output2)
sys.stdout.write('Done.\n')

correct_count = [[0,0,0],[0,0,0],[0,0,0]]
for tidx in range(len(testset_input)):
    vector = testset_input[tidx]
    C1 = clf1.predict_proba([vector])[0][1]
    C2 = clf2.predict_proba([vector])[0][1]
    pre = 0
    if C1>0.5:
        if C2>C1:
            pre = 2
        else:
            pre = 1
    else:
        if C2>0.5:
            pre = 2
        else:
            pre = 0
    out = [0,0,0]
    out[int(testset_output[tidx])] = 1
    correct_count[pre] = [correct_count[pre][iii]+out[iii] for iii in [0,1,2]]
for row in correct_count:
    sys.stdout.write('{} {}\n'.format(str(sum(row)).ljust(6), row))


# Predict all events in DB
conn = sqlite3.connect('data/Caspar_Public.db')
curr = conn.cursor()
all_input = []
for x in curr.execute('select EID, event_type, subject, event_phrase from Events'):
    all_input.append(x)
conn.close()
sys.stdout.write('#datapoints: {}\n'.format(len(all_input)))

all_results = []
f = open('data/SVM_Results.csv', 'w')


# Predict, and write results to file
# Format:
# -- ID, P(Neither), P(Action), P(Problem)
BATCH_SIZE = 50000
sys.stdout.write('Processing...\n')
ptr = 0
last = False
while(not last):
    sys.stdout.write('Processing ... offset: {} / {}\n'.format(ptr, len(all_input)))
    if ptr + BATCH_SIZE>=len(all_input):
        last = True
        seg = all_input[ptr:]
    else:
        seg = all_input[ptr:ptr+BATCH_SIZE]
    ptr += BATCH_SIZE

    texts = []
    for row in seg:
        text = row[3]
        if text.lower().startswith('to ') or text.lower().startswith('if '):
            text = text[3:]
        if not row[2].startswith('(missing)'):
            subj = row[2].replace('(','').replace(')','')
            if not subj in text:
                text = subj+' '+text
        texts.append(text)
    embeddings = embed(texts)
    vectors = sess.run(embeddings)

    R1 = clf1.predict_proba(vectors)
    R2 = clf2.predict_proba(vectors)

    for ridx, row in enumerate(seg):
        C1 = R1[ridx][1]
        C2 = R2[ridx][1]
        EID = int(row[0])
        aaa = C1 # Action
        bbb = C2 # Problem
        rrr = 0  # Neither
        if C1 >= 0.5:
            if C2 >= 0.5:
                rrr = 2 * (1 - C1) * (1 - C2)
            else:
                rrr = 1 - C1
        else:
            if C2 >= 0.5:
                rrr = 1 - C2
            else:
                rrr = 0.5
        sss = aaa + bbb + rrr
        aaa /= sss
        bbb /= sss
        rrr /= sss
        f.write(','.join([str(EID), str(rrr), str(aaa), str(bbb)]))
        f.write('\n')
f.close()
sys.stdout.write('Done.\n')