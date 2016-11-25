import CampaignEmails
import nltk
import bs4
import random
import math

word_tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')

def freq_dist(words):
   pos = nltk.pos_tag(word_tokenizer.tokenize(words))
   nw = []
   for p in pos:
      for t in ['NN', 'VB', 'JJ']:
         if t in p[1] and len(p[0]) > 3:
            nw.append(p[0].upper())  
            break 
   fdst = nltk.FreqDist(nw)
   fdc = fdst.most_common(100)
   #for mc in fdc:
   #   print(' Word: {} Freq: {}'.format(mc[0], mc[1]))
   return list(map(lambda x : x[0], fdc))

def fdist_parse(mboxes):
   before_months = ['Jan', 'Feb', 'Apr', 'May', 'Jun']
   after_months = ['Jul', 'Aug', 'Sep', 'Oct']

   cands = {
      'Clinton': {
         'before': '',
         'after': ''
      },
      'Trump': {
         'before': '',
         'after': ''
      }
   }

   # get all their messages
   for b in mboxes:
      if b.candidate in cands.keys():
         for m in b.messages:
            for bm in before_months:
               if bm in m.headers['Date']:
                 cands[b.candidate]['before'] += bs4.BeautifulSoup(m.body[0].as_string(),'html.parser').get_text()
                 break
            for am in after_months:
               if am in m.headers['Date']:
                 cands[b.candidate]['after'] += bs4.BeautifulSoup(m.body[0].as_string(),'html.parser').get_text()
                 break
   
   #print('\nClinton Before:')
   cands['Clinton']['before'] = freq_dist(cands['Clinton']['before'])
   #print('\nClinton After:')
   cands['Clinton']['after'] = freq_dist(cands['Clinton']['after'])
   #print('\nTrump Before:')
   cands['Trump']['before'] = freq_dist(cands['Trump']['before'])
   #print('\nTrump After:')
   cands['Trump']['after'] = freq_dist(cands['Trump']['after'])

   print('\nWords Clinton Stopped Using:')
   for w in cands['Clinton']['before']:
      if w not in cands['Clinton']['after']:
         print(' ' + w)

   print('\nWords Trump Stopped Using:')
   for w in cands['Trump']['before']:
      if w not in cands['Trump']['after']:
         print(' ' + w)

   return cands

def extract_features(data):
   features = {}
   words = word_tokenizer.tokenize(data)
   for w in words:
      features['contains({})'.format(w)] = True
   return features

def build_feature_list(data):
   feature_list = []
   for d in data:
      feature_list.append((extract_features(d[0]), d[1]))
   return feature_list

def ml_parse(mboxes):
   
   data = []

   for b in mboxes:
      for m in b.messages:  
         html = m.body[0]
         if type(html) != str:
            html = html.as_string()
         for bm in ['Jan', 'Feb', 'Apr', 'May', 'Jun']:
            if bm in m.headers['Date']:
               data.append((bs4.BeautifulSoup(html,'html.parser').get_text(), 'before'))
               break
         for bm in ['Jul', 'Aug', 'Sep', 'Oct']:
            if bm in m.headers['Date']:
               data.append((bs4.BeautifulSoup(html,'html.parser').get_text(), 'after'))
               break

   return data

def main():
   mboxes = CampaignEmails.extractMboxes('Takeout/Mail/')
   #fdist_parse(mboxes)

   print('\nRunning the classifier:')
   data = ml_parse(mboxes)

   random.shuffle(data)

   sl = math.floor(len(data) * 0.75)

   training_data = data[0:sl]
   test_data = data[sl:len(data)]
 
   training_features = build_feature_list(training_data)
   test_features = build_feature_list(test_data)
   
   classifier = nltk.NaiveBayesClassifier.train(training_features)

   count = 0
   for d in test_data:
      features = extract_features(d[0])
      correct = d[1]
      guess = classifier.classify(features)
      if correct == guess:
         count += 1

   print(' Accuracy: {}'.format(float(count)/len(test_data)))

if __name__ == '__main__':
   main()
