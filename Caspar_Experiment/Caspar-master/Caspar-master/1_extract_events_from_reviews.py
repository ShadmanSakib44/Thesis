# 1: Extract events from reviews
# -- This script extracts events from reviews from the shared database
# -- The results are saved into the same database



import sys
import spacy
import sqlite3
if sys.version_info >= (3,):
    import queue
else:
    import Queue as queue

sys.stdout.write('Loading spaCy model...\n')
lg = spacy.load('en')
sys.stdout.write('Loaded.\n')


# Retrieve all reviews from database
conn = sqlite3.connect('data/Caspar_Public.db')
curr = conn.cursor()
all_input = []
for x in curr.execute('select SID, AppId, AppName, Title, Body from OneStarReviews'):
    all_input.append(x)
conn.close()
sys.stdout.write('#datapoints: {}\n'.format(len(all_input)))


# Parse sentences
keyphrases = ['after', 'before', 'as soon as', 'when', 'while', 'whenever', 'every time', 'until', 'then']
kept_verb_deps = ['ROOT', 'advcl', 'conj']
parsed_sents = []

sys.stdout.write('Processing...\n')
for idx, (SID, appid, appname, title, body) in enumerate(all_input):
    if (idx + 1) % 1000 == 0:
        sys.stdout.write('Processing... {} / {}\n'.format((idx + 1), len(all_input)))

    text = body.encode('utf-8', 'ignore').decode("utf-8", 'ignore')
    text = text.replace('as soon as', 'when')
    text = text.replace('As soon as', 'When')
    text = text.replace('every time', 'whenever')
    text = text.replace('Every time', 'Whenever')

    kept_sent_ids = []

    sents = list(lg(text, disable=['ner']).sents)
    for sid, sent in enumerate(sents):
        has_verb = False
        has_advcl = False  # a sentence either has advcl or 'then'
        has_key = False
        has_then = False
        for token in sent:
            if token.tag_.startswith('V') and token.dep_ in kept_verb_deps:
                has_verb = True
                if token.dep_ == 'advcl':
                    has_advcl = True
            if token.text.lower() in keyphrases[:-1]:
                has_key = True
            if token.text.lower() == 'then':
                has_then = True
            if (has_advcl and has_key) or (has_verb and has_then):
                break
        if (has_advcl and has_key) or (has_verb and has_then):
            # also consider surrounding sentences
            kept_sent_ids.append(sid - 1)
            kept_sent_ids.append(sid)
            kept_sent_ids.append(sid + 1)

    one_story = []
    for sid in range(len(sents)):
        if sid in kept_sent_ids:
            # SID is ID for review
            # sid is ID for sentence
            one_story.append((SID, sid, sents[sid]))
    if len(one_story) > 0:
        parsed_sents.append(one_story)
sys.stdout.write('Done. # Kept Stories: {}\n'.format(len(parsed_sents)))



# Extract events
event_sequences = []
sys.stdout.write('Getting event sequences...\n')

for idx, one_story in enumerate(parsed_sents):
    if (idx + 1) % 10000 == 0:
        sys.stdout.write('Processing... {} / {}\n'.format((idx + 1), len(parsed_sents)))

    events = []

    for SID, sid, sent in one_story:
        verbs = []
        for token in sent:
            if token.dep_ in kept_verb_deps:
                verbs.append(token)

        local_events = []
        key_sentence = False
        # dict: verb to key word
        verb_key = {}
        # for each verb, get its children
        for verb in verbs:

            if verb.dep_ == 'conj' and verb.head in verb_key:
                verb_key[verb] = verb_key[verb.head]
            else:
                verb_key[verb] = 'non'

            verb_flags = [verb]
            verb_queue = queue.Queue()
            verb_queue.put(verb)

            while not verb_queue.empty():
                cur = verb_queue.get()
                for t in sent:
                    if t.head == cur and (not t in verbs):
                        if t.dep_ == 'cc' and t.head == verb:
                            continue
                        if t.text.lower() in keyphrases and t.head == verb:
                            verb_key[verb] = t.text.lower()
                            key_sentence = True
                            continue
                        verb_queue.put(t)
                        verb_flags.append(t)
            # remove punctuations and conjunction words
            started = False
            is_question = False
            verb_children = []
            for t in reversed(sent):
                if not t in verb_flags:
                    continue
                if t.tag_ == '_SP':
                    continue
                if t.text == '?':
                    is_question = True
                    break
                if not started:
                    if t.dep_ == 'punct':
                        pass
                    elif t.dep_ == 'cc':
                        pass
                    elif t.tag_ == '.':
                        pass
                    else:
                        started = True
                if started:
                    verb_children.append(t)

            if is_question:
                continue
            if len(verb_children) <= 1:
                continue
            verb_children.reverse()

            # another way to check punctuations
            if verb_children[0].dep_ == 'punct':
                verb_children = verb_children[1:]
            if len(verb_children) <= 1:
                continue

            local_events.append((verb, verb_children, sent))
        if key_sentence:
            for verb in verb_key:
                if verb_key[verb] == 'non':
                    verb_key[verb] = 'out'
        for verb, verb_children, sent in local_events:
            # keep lemma
            events.append((SID, sid, verb, verb_key[verb], verb_children, sent))
    if len(events) > 1:
        event_sequences.append(events)
sys.stdout.write('Done. #Stories: {}'.format(len(event_sequences)))



# Writing results to DB

conn = sqlite3.connect('data/Caspar_Public.db')
curr = conn.cursor()
curr.execute('drop table if exists Events')
curr.execute('CREATE TABLE "Events" (\
	"EID"	INTEGER PRIMARY KEY AUTOINCREMENT, \
	"SID"	INTEGER, \
	"sentenceID"	INTEGER, \
	"verb"	TEXT, \
	"verb_lemma"	TEXT, \
	"verb_type"	TEXT, \
	"event_phrase"	TEXT\
)')
conn.commit()

sys.stdout.write('Writing to DB...\n')
for events in event_sequences:
    for SID, sid, verb, vk, verb_children, sent in events:
        tp = (SID, sid, verb.text, verb.lemma_, vk, ' '.join([t.text for t in verb_children]))
        curr.execute('insert into Events (SID, sentenceID, verb, verb_lemma, verb_type, event_phrase) \
                     values(?,?,?,?,?,?)', tp)
conn.commit()
conn.close()
sys.stdout.write('Written to DB.\n')