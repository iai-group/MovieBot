# IAI MovieBot

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://readthedocs.org/projects/iai-moviebot/badge/?version=latest)](https://iai-moviebot.readthedocs.io/en/latest/?badge=latest)
![Tests](https://img.shields.io/github/workflow/status/iai-group/moviebot/Deploy?label=Tests)
![Coverage Badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/IKostric/4f783c1a3358dbd1e01d44f9656676a0/raw/coverage.moviebot.main.json)

IAI MovieBot is a conversational recommender system for movies.  It follows a standard task-oriented dialogue system architecture, comprising of natural language understanding (NLU), dialogue manager (DM), and natural language generation (NLG) components.  The distinctive features of IAI MovieBot include a task-specific dialogue flow, a multi-modal chat interface, and an effective way to deal with dynamically changing user preferences.  While our current focus is limited to movies, the system aims to be a reusable development framework that can support users in accomplishing recommendation-related goals via multi-turn conversations.

## Demo

IAI MovieBot can be tried on the Telegram channel [@IAI_MovieBot](https://t.me/IAI_MovieBot).


## Installation and documentation

The installation instructions and documentation can be found on [Read the Docs](https://iai-moviebot.readthedocs.io/).

## Contributions

Contributions are welcome. Changes to IAI MovieBot should conform to the [IAI Python Style Guide](https://github.com/iai-group/guidelines/tree/main/python).


## Publication

The system is described in a CIKM'20 demo paper [[PDF](https://arxiv.org/pdf/2009.03668.pdf)]. 

```
@inproceedings{Habib:2020:IMC,
    author = {Habib, Javeria and Zhang, Shuo and Balog, Krisztian},
    title = {IAI {MovieBot}: {A} Conversational Movie Recommender System},
    year = {2020},
    booktitle = {Proceedings of the 29th ACM International Conference on Information and Knowledge Management},
    publisher = {Association for Computing Machinery},
    address = {New York, NY, USA},
    pages = {3405--3408},
    url = {https://doi.org/10.1145/3340531.3417433},
    doi = {10.1145/3340531.3417433},
    series = {CIKM '20}
}
```

## Contributors

Javeria Habib, Shuo Zhang, Krisztian Balog, and Ivica Kostric.
