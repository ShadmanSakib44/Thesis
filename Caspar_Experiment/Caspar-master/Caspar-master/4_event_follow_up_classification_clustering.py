# 4. Classify event pairs

# The training set is generated via negative sampling
# Kmeans was conducted separately
# Using a biLSTM network

## some sample code for SVM
# from sklearn import svm
# sys.stdout.write('Fitting...\n')
# clf = svm.SVC(gamma='scale', probability=True)
# clf.fit(train_input, train_output)
# sys.stdout.write('Done.\n')
# correct_count = [[0,0],[0,0]]
# for tid in range(len(test_input)):
#     pre = clf.predict_proba(test_input[tid:tid+1])[0][1]
#     label = 1 if pre>=0.5 else 0
#     output = [0,0]
#     output[test_output[tid]] = 1
#     correct_count[label] = [correct_count[label][iii]+output[iii] for iii in [0,1]]



TRAINING_RATIO = 0.9
VECSIZE = 300
BATCH_SIZE = 1
NUM_HIDDEN = 256
MAX_LENGTH = 42
epoch = 20



import sys
from datetime import datetime
import random
import spacy
sys.stdout.write('Loading spaCy model...\n')
lg = spacy.load('en_core_web_lg')
sys.stdout.write('Loaded.\n')

sep = lg.vocab.get_vector(u'SEP')
unk = lg.vocab.get_vector(u'UNK')

import csv
training_raw = []
with open('data/eventpairs.csv', 'rb') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',',quotechar = '\"')
    for row in csvreader:
        training_raw.append(row)
sys.stdout.write('#Datapoints: {}\n'.format(len(training_raw)))





f = open('data/kmeans_2.csv','r')
e2_cluster = {}
for row in f:
    items = row.strip().split(',')
    e2_cluster[items[0]] = items[1]
f.close()


# all data points are positive
# need to use random Event 2 as negatives
training_with_label = []
e2s = []
for row in training_raw:
    e2s.append((row[3], row[5]))
for row in training_raw:
    training_with_label.append((row[2], row[5], 1))

    # pick a random e2
    eid2 = str(row[3])
    e2_c = e2_cluster[eid2]
    r = e2_c
    x = -1
    while (r == e2_c):
        x = random.randint(0, len(e2s) - 1)
        r = e2_cluster[str(e2s[x][0])]
    training_with_label.append((row[2], e2s[x][1], 0))

sys.stdout.write('#Training set: {}\n'.format(len(training_with_label)))





# get vectors:
processed_data = []

sys.stdout.write('Processing...\n')
for tid, (e1, e2, LABEL) in enumerate(training_with_label):
    if (tid + 1) % 10000 == 0:
        sys.stdout.write('Processing... {} / {}\n'.format(tid + 1, len(training_with_label)))

    v1 = []
    v2 = []
    tokens_1 = lg(e1.decode('utf-8', 'ignore'), disable=['tagger', 'parser', 'ner'])
    for token in tokens_1:
        v1.append(token.vector)
    tokens_2 = lg(e2.decode('utf-8', 'ignore'), disable=['tagger', 'parser', 'ner'])
    for token in tokens_2:
        v2.append(token.vector)
    output = [0, 0]
    output[LABEL] = 1
    processed_data.append((v1, v2, output))
sys.stdout.write('#Processed dataset: {}\n'.format(len(processed_data)))


# convert event pairs to sequences of vectors
TRAIN_SIZE = int(len(training_with_label)*TRAINING_RATIO)
train_input = []
train_output = []
for v1, v2, output in processed_data[:TRAIN_SIZE]:
    if len(v1)>20:
        v1 = v1[:20]
    if len(v2)>20:
        v2 = v2[:20]

    v = v1[:] + [sep] + v2[:] + [sep]
    v = v + [unk]*MAX_LENGTH
    v = v[:MAX_LENGTH]
    train_input.append(v)
    train_output.append(output)
sys.stdout.write('#Training set: {}\n'.format(len(train_input)))

test_input = []
test_output = []
for v1, v2, output in processed_data[TRAIN_SIZE:]:
    if len(v1)>20:
        v1 = v1[:20]
    if len(v2)>20:
        v2 = v2[:20]
    v = v1[:] + [sep] + v2[:] + [sep]
    v = v + [unk]*MAX_LENGTH
    v = v[:MAX_LENGTH]
    test_input.append(v)
    test_output.append(output)
sys.stdout.write('#Testing set: {}\n'.format(len(test_input)))

combined = zip(train_input, train_output)
random.shuffle(combined)
train_input, train_output = zip(*combined)

combined = zip(test_input, test_output)
random.shuffle(combined)
test_input, test_output = zip(*combined)




# biLSTm
import tensorflow as tf
CLASSES = ['e2_is_good', 'e2_is_random']
# Input data dimension: [batch size, sequence length, input dimension]
data = tf.compat.v1.placeholder(tf.float32, [BATCH_SIZE, None, VECSIZE], name='data')
target = tf.compat.v1.placeholder(tf.float32, [BATCH_SIZE, len(CLASSES)], name='target')
# bidirectional LSTM network
with tf.compat.v1.variable_scope('biLSTM'):
    lstm_fw_cell = tf.nn.rnn_cell.LSTMCell(NUM_HIDDEN, state_is_tuple=True, reuse=tf.compat.v1.AUTO_REUSE)
    lstm_bw_cell = tf.nn.rnn_cell.LSTMCell(NUM_HIDDEN, state_is_tuple=True, reuse=tf.compat.v1.AUTO_REUSE)
    (output, state) = tf.nn.bidirectional_dynamic_rnn(lstm_fw_cell, lstm_bw_cell, data, dtype=tf.float32)

H = tf.concat(output, 2)
optimizer = tf.compat.v1.train.AdamOptimizer(learning_rate=0.0001)
logits = tf.layers.dense(H, 2, activation=tf.nn.sigmoid)
prediction = tf.gather(tf.nn.softmax(logits, axis=2), 0, axis=1, name='prediction')
loss = tf.compat.v1.losses.sigmoid_cross_entropy(multi_class_labels=target, logits=prediction)
predicted_label = tf.argmax(prediction, axis=1, name='predicted_label')
minimize = optimizer.minimize(loss, name='minimize')



# Training
no_of_batches = TRAIN_SIZE//BATCH_SIZE
sess = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto (allow_soft_placement=True))
sess.run(tf.compat.v1.global_variables_initializer())

startTime = datetime.now()
i = 0
while (True):
    sys.stdout.write('Currently working on Epoch {:2d}...\n'.format(i + 1))
    ptr = 0
    for j in range(no_of_batches):
        inp, out = train_input[ptr:ptr + BATCH_SIZE], train_output[ptr:ptr + BATCH_SIZE]
        ptr += BATCH_SIZE
        sess.run(minimize, {data: inp, target: out})
    cen = sess.run(loss, {data: train_input[0:BATCH_SIZE], target: train_output[0:BATCH_SIZE]})

    sys.stdout.write('Epoch - {:2d} Logarithm Loss in the first batch: {:3.4f}\n'.format(i + 1, cen))
    sys.stdout.write('Time elapsed: {}\n'.format(datetime.now() - startTime))
    i = i + 1
    if i >= epoch:
        break

sys.stdout.write('Trained.\n')
sys.stdout.write('Total time taken: {}\n'.format(datetime.now() - startTime))



# Save model to file
sys.stdout.write('Saving model to file...\n')
saver = tf.compat.v1.train.Saver()
save_path = saver.save(sess, 'model/binary_bilstm_clustering.model')
sys.stdout.write('Model saved in file: {}\n'.format(save_path))








# Testing, and writing results to file
f = open('model/log.txt' , 'w')
correct_count = [[0,0],[0,0]]
for tid in range(0, len(test_input)-BATCH_SIZE, BATCH_SIZE):
    pres = sess.run(predicted_label, {data: test_input[tid:tid+BATCH_SIZE]})
    for i in range(BATCH_SIZE):
        pre = pres[i]
        correct_count[pre] = [correct_count[pre][iii]+test_output[tid+i][iii] for iii in [0,1]]

sys.stdout.write('Matrix:\n')
f.write('Matrix:\n')
true_count = [correct_count[0][iii]+correct_count[1][iii] for iii in [0,1]]

sys.stdout.write(''.ljust(6))
sys.stdout.write('{}\n'.format(true_count))
f.write(''.ljust(6))
f.write('{}\n'.format(true_count))

sys.stdout.write('----------------------\n')
f.write('----------------------\n')

for row in correct_count:
    sys.stdout.write('{} {}\n'.format(str(sum(row)).ljust(6), row))
    f.write('{} {}\n'.format(str(sum(row)).ljust(6), row))
f.close()