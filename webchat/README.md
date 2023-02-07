# Webchat widget

## Requirements

`Node.js` and `npm` need to be installed to modify and build the widget. See this [page](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) for installation details.

## Build widget

Execute the following commands to build the widget:

```shell
npm install --legacy-peer-deps
npm run build
```

The widget is put under the folder `dist`.

## Use widget

  * Download `main.css` and `chat-widget.min.js` form the folder `dist`.
  * Add the `main.css` stylesheet to the header of the HTML page as shown below.

```html
<header>
    ...
    <link rel="stylesheet" href="main.css">
    ...
</header>
```

  * Add the JS widget `chat-widget.min.js` at the end of the HTML body. Please change the value of `bot_url` to the chatbot endpoint.

```html
<body>
    ...
    <script type="text/javascript" src="chat-widget.min.js" bot_url="http://127.0.0.1:5001/"></script>
    ...
</body>
```

An example of HTML page using the widget is available [here](example.html).

## Widget structure

All the source code is under the folder `src`:

  * `index.js`: Main JS that add the chatbox to page body.
  * `css`: Folder with the styles for the chatbot.
  * `html`: Folder with the HTML components of the chatbox.
  * `lib`: Folder with feature specific JS scripts.