## Datasource


Dataset was acquired from [here](https://research.google/tools/datasets/coached-conversational-preference-elicitation/). It consists of 12,000 annotated
utterances over 502 conversations. The dataset, called ```data.json``` should be
in the ```eval/data``` folder.

Alternatively, ```data_wth_links.json``` file can be used. This file has the
same structure as ```data.json``` with the inclusion of wikipedia links. This links
are linking the annotated named entities with the wikipedia pages they correspond
to. While this is not useful in evaluating the rule-based annotator, it can be used on
any neural annotator that was trained on wikipedia corpus.


## Evaluation usage


The script is run by executing:

```(python)
python evaluation.py
```

If ```annotation.json``` file exists precision, recall and f1 metrics are
displayed. If not, new file is created which contains these metrics in addition
to annotations for all conversations and all erroneous annotations. The slots considered in this evaluation are Title, Genre and Person. Example of the created file is as follows

```(json)
{
	"genres": {
		"duration": 10,
		"metrics": {
			"precision": 0.5127693535514765,
			"recall": 0.749708284714119,
			"f1": 0.6090047393364929,
		}
		"errors": [
			{
				'conversation': 0,
				'utterance': "I like Star Wars a lot.",
				'annotations': {
                        "text": "Wars",
                        "start": 12,
                        "end": 15,
                        "lemma": "war",
                        "is_stopword": false,
                        "annotation_type": "named_entity",
                        "entity_type": "genres"
                    },
				'truth': []
			}
		]
		"annotations": [
			[
				[],
				[{
					"text": "thrillers",
					"start": 7,
					"end": 16,
					"lemma": "thriller",
					"is_stopword": false,
					"annotation_type": "named_entity",
					"entity_type": ""
				}],
				[],
				[],

				...

			]

			...

		]
	}
}
```


## Results


These are the results over all conversations in the data set. Reported values are
for micro-averaged precision, recall and f1 scores.


### Rule-based annotator

```(python)
$ python evaluation.py

Scores for genres:

        Precision (micro-averaged): 0.51277
        Recall (micro-averaged): 0.74971
        F1: 0.609

Annotation took 0.143 minutes

Scores for actors:

        Precision (micro-averaged): 0.25813
        Recall (micro-averaged): 0.80952
        F1: 0.39145

Annotation took 166.354 minutes

Scores for title:

        Precision (micro-averaged): 0.33884
        Recall (micro-averaged): 0.77407
        F1: 0.47135

Annotation took 28.545 minutes
```