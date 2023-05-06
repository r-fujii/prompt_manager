// settings
const commonSettingsArea = document.getElementById("commonSettingsArea");
const temperatureRange = document.getElementById("temperatureRange");

// chat area
const tabLabel = document.getElementById("tabLabel");
const promptTab = document.getElementById("promptTab");
const userMessageTab = document.getElementById("userMessageTab");
const promptArea = document.getElementById("promptArea");
const userMessageArea = document.getElementById("userMessageArea");
const cardArea = document.getElementById("cardArea");
var cardId = 1;

const cardTemplate = `<div id="card-{CARDID}" class="card mb-3 shadow-sm">
    <div class="card-header">
        <h5 class="my-0 ms-2">#{CARDID}</h4>
    </div>
    <div class="card-body d-flex flex-row my-1 mx-2">
        <div>
            <p id="prompt-{CARDID}" class="prompt" style="white-space: pre-wrap; font-size: small">{PROMPT}</p>
        </div>
        <div class="d-flex no-wrap align-items-start ms-auto ps-4">
            <button type="button" class="btn btn-md btn-outline-danger mx-1 text-nowrap" onclick="deletePrompt(this)">Delete</button>
        </div>
    </div>
</div>`

$("#tabToggle").on("click", function() {
    $(".toggle").toggleClass("checked");
    if (!$("input[name='check']").prop("checked")) {
      $(".toggle input").prop("checked", true);
      promptTab.classList.remove("active");
      userMessageTab.classList.add("active");
      tabLabel.textContent = "Write your message :"
    } else {
      $(".toggle input").prop("checked", false);
      userMessageTab.classList.remove("active");
      promptTab.classList.add("active");
      tabLabel.textContent = "Write new prompt :"
    }
  });

function addPrompt() {
    const prompt = promptArea.value.trim().slice(0, 1024);

    if (prompt.length == 0) {
        alert("Please input your prompt.");
        return;
    }

    // count existing prompts
    const prompts = document.querySelectorAll(".prompt");
    if (prompts.length >= 4) {
        alert("Reached the maximum number of prompts. To to add new one, please delete existing prompts.")
        return;
    }

    // clear prompt
    promptArea.value = "";

    cardHTML = cardTemplate.replaceAll("{CARDID}", cardId).replace("{PROMPT}", prompt);
    cardArea.insertAdjacentHTML("beforeend", cardHTML);

    cardId++;
}

function deletePrompt(btn) {
    let card = btn.closest(".card");
    if (window.confirm("Are you sure to delete the prompt?")) {
        card.remove();
    }
}

function countTokens() {
    const prompt = promptArea.value.trim().slice(0, 1024);

    if (prompt.length == 0) {
        alert("Please input your prompt.");
        return;
    }

    const btns = document.querySelectorAll(".btn");
    btns.forEach(x => x.classList.add("disabled"));
    
    const data = JSON.stringify({"prompt": prompt});

    $.ajax({
        url: COUNT_API_URL,
        type: "POST",
        contentType: "application/json",
        data : data
    }).done(function(data) {
        num_tokens = data["num_tokens"]
        alert(`The prompt consists of ${num_tokens} token(s).`)
    }).fail(function() {
        alert("API Error");
    }).always(function() {
        userMessageArea.removeAttribute("disabled");
        btns.forEach(x => x.classList.remove("disabled"));
    });
}

function postMessage() {
    const userMessage = userMessageArea.value.trim().slice(0, 1024);

    if (userMessage.length == 0) {
        alert("Please input your message.");
        return;
    }

    // get candidate prompt suffices (exact prompt sent will be the concatenation of suffix and user message)
    const prompts = document.querySelectorAll(".prompt");
    if (prompts.length == 0) {
        alert("You need at least one prompt added.")
        return;
    }

    var id2prompt = {};
    for (x of prompts) {
        id2prompt[x.id.split("-").pop()] = x.textContent;
    }

    // clear user message
    userMessageArea.value = "";
    userMessageArea.setAttribute("disabled", "true");

    const btns = document.querySelectorAll(".btn");
    btns.forEach(x => x.classList.add("disabled"));

    const data = JSON.stringify({"id2prompt": id2prompt, "user_message": userMessage});

    $.ajax({
        url: MESSAGE_API_URL,
        type: "POST",
        contentType: "application/json",
        data : data
    }).done(function(data) {
        message = data["message"]
        for (x of message) {
            el = document.getElementById(`prompt-${x["elem_id"]}`);

            completionId = `completion-${x["elem_id"]}`;

            if (document.getElementById(completionId) == null) {
                // create a new node for completion (keep original prompt intact)
                completion = el.cloneNode();
                completion.id = completionId;
                completion.classList.remove("prompt");
                completion.classList.add("completion");
                el.after(completion);
                el.style.display = "none";
            } else {
                completion = document.getElementById(completionId);
            }

            completion.innerHTML = `<font color="lightgray">${x["prompt"]}\n\n${x["user_message"]}</font>\n\n${x["completion"]}`;
        }
    }).fail(function() {
        alert("API Error");
    }).always(function() {
        userMessageArea.removeAttribute("disabled");
        btns.forEach(x => x.classList.remove("disabled"));
    });
}

function getStats() {
    const userMessage = userMessageArea.value.trim().slice(0, 1024);

    if (userMessage.length == 0) {
        alert("Please input your message.");
        return;
    }

    // get candidate prompt suffices (exact prompt sent will be the concatenation of suffix and user message)
    const prompts = document.querySelectorAll(".prompt");
    if (prompts.length == 0) {
        alert("You need at least one prompt added.")
        return;
    }

    var id2prompt = {};
    for (x of prompts) {
        id2prompt[x.id.split("-").pop()] = x.textContent;
    }

    // clear user message
    userMessageArea.value = "";
    userMessageArea.setAttribute("disabled", "true");

    const btns = document.querySelectorAll(".btn");
    btns.forEach(x => x.classList.add("disabled"));

    const data = JSON.stringify({"id2prompt": id2prompt, "user_message": userMessage});

    $.ajax({
        url: STATS_API_URL,
        type: "POST",
        contentType: "application/json",
        data : data
    }).done(function(data) {
        try {
            var win = window.open(STATS_URL, "_blank")
            win.onload = function () {
                resultArea = win.document.getElementById("resultArea");
                resultArea.innerHTML = data;
            }
        } catch {
            // ignore exceptions to execute always clause (an exception is raised when popup is blocked by browser policy)
        }
    }).fail(function() {
        alert("API Error");
    }).always(function() {
        userMessageArea.removeAttribute("disabled");
        btns.forEach(x => x.classList.remove("disabled"));
    });
}

function saveSettings() {
    const commonSettings = commonSettingsArea.value.trim().slice(0, 1024);
    const temperature = Math.min(Math.max(parseFloat(temperatureRange.value), 0), 2.0);

    const data = JSON.stringify({"common_settings": commonSettings, "temperature": temperature});

    $.ajax({
        url: SAVE_SETTINGS_URL,
        type: "POST",
        contentType: "application/json",
        data : data
    }).done(function(data) {
        // close modal window
        $("body").removeClass("modal-open");
        $(".modal-backdrop").remove();
        $("#settingsModal").modal("hide");
    }).fail(function() {
        // close modal window, then show alert
        $("body").removeClass("modal-open");
        $(".modal-backdrop").remove();
        $("#settingsModal").modal("hide");
        alert("Save settings failed");
    });
}

// utility function
function writeValueAt(elemId, value) {
    elem = document.getElementById(elemId);
    valueFloat = parseFloat(value).toFixed(2);
    elem.value = valueFloat;
}