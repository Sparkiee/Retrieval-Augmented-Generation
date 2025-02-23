document.querySelector(".searchbar").addEventListener("input", function () {
    this.style.height = "auto"; // Reset height to auto to calculate the new height
    this.style.height = this.scrollHeight + "px"; // Set the height to the scrollHeight
});

document.querySelector(".searchbar").addEventListener("keydown", function (e) {
    if (e.keyCode === 13) {
        e.preventDefault();
        const query = this.value;
        const userMessage = document.createElement("div");
        userMessage.classList.add("user-message");
        userMessage.textContent = query;
        document.querySelector(".chat-history").appendChild(userMessage);
        this.value = "";

        fetch("/query", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ query }),
        })
            .then((res) => res.json())
            .then((data) => {
                console.log(data);
                const botMessage = document.createElement("div");
                botMessage.classList.add("bot-message");
                botMessage.textContent = data.response;
                document.querySelector(".chat-history").appendChild(botMessage);
            });
    }
});
