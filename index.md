IAI MovieBot is a conversational recommender system for movies. It follows a standard task-oriented dialogue system architecture, comprising of natural language understanding (NLU), dialogue manager (DM), and natural language generation (NLG) components. The distinctive features of IAI MovieBot include a task-specific dialogue flow, a multi-modal chat interface, and an effective way to deal with dynamically changing user preferences. While our current focus is limited to movies, the system aims to be a reusable development framework that can support users in accomplishing recommendation-related goals via multi-turn conversations.

## Demo

IAI MovieBot can be tried on the Telegram channel [@IAI_MovieBot](https://t.me/IAI_MovieBot), or by clicking on the chat widget below.

## Contributions

Contributions are welcome. Changes to IAI MovieBot should conform to the IAI Python Style Guide.

## Publication

The system is described in a CIKM'20 demo paper [PDF].

```bibtex
@inproceedings{Habib:2020:IMC,
    author = {Habib, Javeria and Zhang, Shuo and Balog, Krisztian},
    title = {IAI {MovieBot}: {A} Conversational Movie Recommender System},
    year = {2020},
    booktitle = {Proceedings of the 29th ACM International Conference on Information and Knowledge Management},
    publisher = {Association for Computing Machinery},
    address = {New York, NY, USA},
    pages = {3405--3408},
    url = {<https://doi.org/10.1145/3340531.3417433>},
    doi = {10.1145/3340531.3417433},
    series = {CIKM '20}
}
```

## Contributors

Javeria Habib, Shuo Zhang, [Krisztian Balog](krisztianbalog.com), [Ivica Kostric](https://ikostric.github.io/), Nolwenn Bernard, and Weronika Lajewska

<script
  type="text/javascript"
  src="https://cdn.jsdelivr.net/npm/iaigroup-chatwidget@1/build/bundle.min.js"
></script>

<script type="text/javascript">
  ChatWidget({
    name: "MovieBot",
    serverUrl: "gustav1.ux.uis.no",
    socketioPath: "/moviebot/",
    useFeedback: false,
    useLogin: false,
  });
</script>
