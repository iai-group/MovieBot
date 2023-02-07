import html from '../html/chat.html';
import '../css/chat.scss';
import getBrowserFingerprint from 'get-browser-fingerprint';

var $ = require("jquery");
window.jQuery = $;
window.$ = $;

const fingerprint = getBrowserFingerprint();

const botUrl = document.currentScript.getAttribute("bot_url") || (function () {
    var scripts = document.getElementsByTagName("script");
    return scripts[scripts.length - 1].getAttribute("bot_url");
})();

class ChatBox extends HTMLElement {
    constructor() {
        super();

        this.innerHTML = html.toString()

        this.send = this.send.bind(this);
        this.keyPressed = this.keyPressed.bind(this);
    }

    connectedCallback() {
        const button = this.querySelector("#send");
        button.onclick = this.send;

        const input = this.querySelector("#msg_text")
        input.onkeypress = this.keyPressed;
    }

    send() {
        const text = $("#msg_text").val();

        if (text) {
            sendMessage(text);
        }
        $("#msg_text").val("");
    }

    keyPressed(event) {
        if (event.keyCode == 13) {
            $("#send").click();
        }
    }
}

function displayMessage(message, sender) {
    let msgInfo = {
        bgType: sender === "user" ? "bg-dark text-light bg-opacity-75" : "bg-light text-dark",
        icon: sender === "user" ? "bi-person-fill" : "bi bi-robot",
        style: sender === "user" ? "margin-left: 30%; " : "margin-right:30%; ",
        msg: message.text,
    };

    var msgDiv = document.createElement("div");
    msgDiv.setAttribute("class", "chat_msg " + msgInfo.bgType + '"');
    msgDiv.setAttribute("style", msgInfo.style + " word-wrap: break-word;");
    var icon = document.createElement("i");
    icon.setAttribute("class", "bi " + msgInfo.icon);
    msgDiv.appendChild(icon);
    msgDiv.appendChild(document.createElement("br"))

    if ("attachment" in message) {
        switch (message.attachment.type) {
            case "buttons":
                displayAction(message.attachment);
                break;
            case "images":
                console.log(message.attachment);
                var imagesDiv = displayImages(message.attachment);
                console.log(imagesDiv);
                msgDiv.appendChild(imagesDiv);
                break;
        }
    } else {
        $("#action-buttons").empty();
    }

    msgDiv.append(msgInfo.msg);
    $("#msg-box").append(msgDiv);
}

function displayAction(attachment) {
    attachment.payload.buttons.forEach(button => {
        const htmlButton = document.createElement("button");
        htmlButton.setAttribute("type", "button");
        htmlButton.setAttribute("class", "btn btn-outline-secondary");
        htmlButton.innerText = button.title;
        htmlButton.onclick = function () { sendAction(button.payload); };
        $("#action-buttons").append(htmlButton);
    });
}

function createImageElement(imageSrc, active) {
    var imageDiv = document.createElement("div");
    if (active === true) {
        imageDiv.setAttribute("class", "carousel-item active");
    } else {
        imageDiv.setAttribute("class", "carousel-item");
    }
    var image = document.createElement("img");
    image.setAttribute("src", imageSrc);
    image.setAttribute("class", "d-block w-100");
    image.setAttribute("height", "300px");
    image.style = "object-fit:contain;";
    imageDiv.appendChild(image);
    return imageDiv;
}
function displayImages(attachment) {
    var imagesDiv = document.createElement("div");
    imagesDiv.setAttribute("id", "imagesCarousel");
    imagesDiv.setAttribute("class", "carousel slide");
    var carouselDiv = document.createElement("div");
    carouselDiv.setAttribute("class", "carousel-inner");
    var htmlNavigationButtons = "";
    if (attachment.payload.images.length === 1) {
        var image = attachment.payload.images[0]
        carouselDiv.appendChild(createImageElement(image, true));
    } else {
        attachment.payload.images.forEach((image, index) => {
            if (index === 0) {
                carouselDiv.appendChild(createImageElement(image, true));
            } else {
                carouselDiv.appendChild(createImageElement(image, false));
            }
        });
        htmlNavigationButtons = '<button class="carousel-control-prev" type="button" data-bs-target="#imagesCarousel" data-bs-slide="prev"><span class="carousel-control-prev-icon" aria-hidden="true"></span><span class="visually-hidden">Previous</span></button><button class="carousel-control-next" type="button" data-bs-target="#imagesCarousel" data-bs-slide="next"><span class="carousel-control-next-icon" aria-hidden="true"></span><span class="visually-hidden">Next</span></button>';
    }
    imagesDiv.appendChild(carouselDiv);
    imagesDiv.innerHTML = imagesDiv.innerHTML + htmlNavigationButtons;

    return imagesDiv;
}

function sendAction(payload) {
    sendMessage(payload);
}

function sendMessage(text) {
    let msg2server = {
        "entry": [{
            "messaging": [
                {
                    "message": { "text": text },
                    "sender": { "id": fingerprint },
                }
            ]
        }]
    };

    $.ajax({
        type: "POST",
        url: botUrl || "http://127.0.0.1:5001/",
        contentType: "application/json;charset=UTF-8",
        data: JSON.stringify(msg2server),
        beforeSend: displayMessage(msg2server.entry[0].messaging[0].message, "user"),
        success: function (data) {
            displayMessage(data.message, "bot");
        },
        error: function () {
            alert("Something went wrong. Please check that the attribute bot_url is correct.");
        },
        complete: function () {
            var msgBox = document.getElementById("msg-box");
            msgBox.scrollTop = msgBox.scrollHeight;
        }
    });
}


export default ChatBox;