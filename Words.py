import CampaignEmails
import nltk
import bs4

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
   for mc in fdst.most_common(50):
      print(' Word: {} Freq: {}'.format(mc[0], mc[1]))
   return fdst.most_common(50)

def parse(mboxes):
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
                 cands[b.candidate]['before'] += m.body[0].as_string()
                 break
            for am in after_months:
               if am in m.headers['Date']:
                 cands[b.candidate]['after'] += m.body[0].as_string()
                 break

   # get rid of the html
   soup = bs4.BeautifulSoup(cands['Clinton']['before'], 'html.parser')
   cands['Clinton']['before'] = soup.get_text()
   soup = bs4.BeautifulSoup(cands['Clinton']['after'], 'html.parser')
   cands['Clinton']['after'] = soup.get_text()
   soup = bs4.BeautifulSoup(cands['Trump']['before'], 'html.parser')
   cands['Trump']['before'] = soup.get_text()
   soup = bs4.BeautifulSoup(cands['Trump']['after'], 'html.parser')
   cands['Trump']['after'] = soup.get_text()

   print('\nClinton Before:')
   cb = freq_dist(cands['Clinton']['before'])
   print('\nClinton After:')
   ca = freq_dist(cands['Clinton']['after'])
   print('\nTrump Before:')
   tb = freq_dist(cands['Trump']['before'])
   print('\nTrump After:')
   ta = freq_dist(cands['Trump']['after'])

   cb = list(map(lambda x : x[0], cb))
   ca = list(map(lambda x : x[0], ca))
   tb = list(map(lambda x : x[0], tb))
   ta = list(map(lambda x : x[0], ta))

   print('\n Words Clinton Stopped Using')
   for w in cb:
      if w not in ca:
         print(w)

   print('\n Words Trump Stopped Using')
   for w in tb:
      if w not in ta:
         print(w)

def main():
   mboxes = CampaignEmails.extractMboxes('Takeout/Mail/')
   parse(mboxes)
   #tokens = nltk.word_tokenize(para)

if __name__ == '__main__':
   main()
