from debug import debug as sj_debug
# -*- coding: utf-8 -*-

import sys
import json
import nltk

# Load in unstructured data from wherever you've saved it
def relavence(documents, terms):
    try:
        QUERY_TERMS = terms.split(',') if isinstance(terms,(str, unicode)) else terms

        activities = [activity.content.lower().split() \
                      for activity in documents \
                        if activity.content != ""]

        # Provides tf/idf/tf_idf abstractions

        tc = nltk.TextCollection(activities)

        relevant_activities = []

        for idx in range(len(activities)):
            score = 0
            for term in [t.lower() for t in QUERY_TERMS]:
                score += tc.tf_idf(term, activities[idx])
            if score > 0:
                relevant_activities.append({'score': score, 'title': documents[idx].title,
                                      'url': documents[idx].url})

        # Sort by score and display results

        relevant_activities = sorted(relevant_activities, key=lambda p: p['score'], reverse=True)
        print relevant_activities
        for activity in relevant_activities:
            print activity['title']
            print '\tLink: %s' % (activity['url'], )
            print '\tScore: %s' % (activity['score'], )
    except Exception as e:
        print e
