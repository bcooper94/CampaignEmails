import json

import CampaignEmails

MM = {
   0: 'Jan',
   1: 'Feb',
   2: 'Mar',
   3: 'Apr',
   4: 'May',
   5: 'Jun',
   6: 'Jul',
   7: 'Aug',
   8: 'Sep',
   9: 'Oct'
}

def count_months(messages):
   months = {
      'Jan': 0,
      'Feb': 0,
      'Mar': 0,
      'Apr': 0,
      'May': 0,
      'Jun': 0,
      'Jul': 0,
      'Aug': 0,
      'Sep': 0,
      'Oct': 0
   }
   for m in messages:
      for k in months.keys():
         if k in m.headers['Date']:
            months[k] = months[k] + 1
   return months

def count_cands(mboxes):
   cands = {}
   for mbox in mboxes:
      cands[mbox.candidate] = count_months(mbox.messages)
   return cands

def main():
   global MM
   mboxes = CampaignEmails.extractMboxes('Takeout1/Mail/')
   email_counts = count_cands(mboxes)
   f = open('./data.json')
   graph_data = json.loads(f.read())
   f.close()

   for g in graph_data:
      for c in email_counts:
         if c in g['candidate']:
            g['z'] = email_counts[c][MM[g['x']]]
   
   f = open('./final_data.json', 'w')
   f.write(json.dumps(graph_data, indent=4))
   f.close()

   #for mbox in mboxes:
   #   print(mbox)
   #   print(mbox.messages[0].headers['Date'])
   #   print(len(mbox.messages))

if __name__ == '__main__':
   main()
