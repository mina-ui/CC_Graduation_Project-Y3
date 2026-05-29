import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm'

const supabaseUrl = "https://yekpasnhsxlhtdzahsme.supabase.co"
const supabaseKey = "sb_publishable_O3f5gU6xQUJbCKOWxP1VxA_bC6uClJv"

const supabase = createClient(supabaseUrl, supabaseKey)

const voiceToText = document.getElementById("voiceToText");
const submitBtn = document.getElementById("submitBtn");
const letterInput = document.getElementById("letterInput");
const authorInput = document.getElementById("authorInput");
const status = document.getElementById("status");

submitBtn.addEventListener("click", submitLetter);

// Speech to text with webkit api
const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
    const recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.lang = navigator.language || "en-GB";

    voiceToText.addEventListener("click", () => {
        recognition.start();
        status.innerText = "Listening...";
    });

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;

        letterInput.value +=
            (letterInput.value ? " " : "") + transcript;

        status.innerText = "Voice captured!";
    };

    recognition.onerror = (event) => {
        status.innerText = "Voice error: " + event.error;
    };

    recognition.onend = () => {
        setTimeout(() => (status.innerText = ""), 2000);
    };

} else {
    voiceToText.style.display = "none";

    status.innerText =
        "Voice input is available in Google Chrome or Microsoft Edge (check if it works in safari etc). You can still type your message.";
}

// Message submission
async function submitLetter() {
    const text = letterInput.value.trim();
    const author = authorInput.value.trim() || "Anonymous";

    if (text.length < 10) {
        status.innerText = "Please write a longer message.";
        return;
    }

    if (text.length > 400) {
        status.innerText = "Letters must be under 400 characters.";
        return;
    }

    const { error } = await supabase
        .from("visitor_letters")
        .insert([
            {
                content: text,
                author: author,
            },
        ]);

    if (error) {
        status.innerText = "Something went wrong.";
        console.error(error);
    } else {
        status.innerText = "Your letter has been added ♥";
        letterInput.value = "";
        authorInput.value = "";
    }
}
