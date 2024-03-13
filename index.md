IAI MovieBot is a conversational recommender system for movies. It follows a standard task-oriented dialogue system architecture, comprising natural language understanding (NLU), dialogue manager (DM), and natural language generation (NLG) components. Additionally, it includes a user model and a recommendation engine. Some modules may use different models, which can be trained using the provided training utilities. It also comes with different deployment platforms (such as Telegram and Flask REST).
The distinctive features of IAI MovieBot include a task-specific dialogue flow, a multi-modal chat interface, and an effective way to deal with dynamically changing user preferences. While our current focus is limited to movies, the system aims to be a reusable and extensible development framework that can support users in accomplishing recommendation-related goals via multi-turn conversations.

The v1.0 version of IAI MovieBot has been presented as a demonstration paper at CIKM'20 [[PDF](https://arxiv.org/pdf/2009.03668.pdf)], while the v2.0 version was presented at WSDM'24 [[PDF](https://arxiv.org/pdf/2403.00520.pdf)].

## Demos

### Version 2.0

IAI MovieBot v2.0 can be tried [here](https://gustav1.ux.uis.no/moviebotv2/).

### Version 1.1

<div id=chatWidgetContainer></div>
<script
  type="text/javascript"
  src="https://cdn.jsdelivr.net/npm/iaigroup-chatwidget@latest/build/bundle.min.js"
></script>

<script type="text/javascript">
  ChatWidget({
    name: "MovieBot",
    serverUrl: "https://gustav1.ux.uis.no",
    socketioPath: "/moviebot",
    useFeedback: false,
    useLogin: false,
  });
</script>

## Contributions

Contributions are welcome. Changes to IAI MovieBot should conform to the [IAI Python Style Guide](https://github.com/iai-group/guidelines/tree/main/python#readme).

## Citation

For the most recent version (v2.0) of IAI MovieBot, please cite:

```bibtex
@inproceedings{Bernard:2024:WSDM,
    author = {Bernard, Nolwenn and Kostric, Ivica and Balog, Krisztian},
    title = {IAI MovieBot 2.0: An Enhanced Research Platform with Trainable Neural Components and Transparent User Modeling},
    year = {2024},
    doi = {10.1145/3616855.3635699},
    booktitle = {Proceedings of the 17th ACM International Conference on Web Search and Data Mining},
    series = {WSDM '24}
}
```

For the v1.0 version of IAI MovieBot, please cite:

```bibtex
@inproceedings{Habib:2020:CIKM,
    author = {Habib, Javeria and Zhang, Shuo and Balog, Krisztian},
    title = {IAI {MovieBot}: {A} Conversational Movie Recommender System},
    year = {2020},
    booktitle = {Proceedings of the 29th ACM International Conference on Information and Knowledge Management},
    pages = {3405--3408},
    doi = {10.1145/3340531.3417433},
    series = {CIKM '20}
}
```

## Contributors

IAI MovieBot is developed and maintained by the [IAI group](https://iai.group/) at the University of Stavanger.

(Alphabetically ordered by last name)

  * Javeria Habib (2020)
  * Krisztian Balog (2020-present)
  * Nolwenn Bernard (2022-present)
  * Ivica Kostric (2021-present)
  * Weronika Łajewska (2022-present)
  * Martin G. Skjæveland (2022)
  * Shuo Zhang (2020)
