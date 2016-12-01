import CampaignEmails
import nltk
import random

#extract all the emails from the mailbox objects
def getMessages(clinton, trump):
    # mboxes = CampaignEmails.extractMboxes('Takeout1/Mail/')
    # mboxes.extend(CampaignEmails.extractMboxes('Takeout2/Mail/'))
    mboxes = CampaignEmails.extractMboxes('Takeout3/Mail/')

    for mbox in mboxes:
        if mbox.candidate == 'Trump':
            trump.extend([message.body[0].as_string() for message in mbox.messages])
        elif mbox.candidate == 'Clinton':
            clinton.extend([message.body[0].as_string() for message in mbox.messages])

#check if the text contains one of the input characters
def contains(text, chars):
    for char in chars:
        if char in text:
            return True
    return False

#extract adjectives and verbs from an email text
def extract_words(message):
    tagged = nltk.pos_tag(nltk.word_tokenize(message))
    words = set()
    for word in tagged:
        if contains(word[0], ['*', '=', '<', '>', '.', '-', '|', '\\', '/', ':', 'clinton', 'trump', 'republican', 'democratic', 'deductible', 'unsubscribe', 'charset', 'go']):
            continue
        elif word[1] == 'VB' or word[1] == 'JJ':
            words.add(word[0].lower())
    return words




#load and extract clinton and trump messages
clinton = []
trump = []
getMessages(clinton, trump)

# clinton = [extract_words(mess) for mess in clinton]
# trump = [extract_words(mess) for mess in trump]

# clint = []
# for se in clinton:
#     clint.extend(se)
#
# trum = []
# for se in trump:
#     trum.extend(se)

# print(nltk.FreqDist(trum).most_common(10))
# print(nltk.FreqDist(clint).most_common(10))

#create labeled clinton and trump feature sets
clinton = [({word:True for word in extract_words(message)}, 'Clinton') for message in clinton]
trump = [({word:True for word in extract_words(message)}, 'Trump') for message in trump]

print(clinton)
print(trump)

#separate into test and training
training = clinton + trump
random.shuffle(training)
size = int(len(training) * .3)
test = training[:size]
training = training[size:]
print(len(training))
print(training)
print(len(test))
print(test)

classifier = nltk.NaiveBayesClassifier.train(training)
print(nltk.classify.accuracy(classifier, test))

# classifier = nltk.DecisionTreeClassifier.train(training)
# print(nltk.classify.accuracy(classifier, test))

# for mess in trump:
#     print(extract_words(mess))