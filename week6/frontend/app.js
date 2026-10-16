const form = document.querySelector("#message-form");
const input = document.querySelector("#message-input");
const list = document.querySelector("#message-list");
const statusBadge = document.querySelector("#status");
const errorBox = document.querySelector("#error");

function render(messages) {
  list.replaceChildren(...messages.map((message) => {
    const item = document.createElement("li");
    const text = document.createElement("span");
    const time = document.createElement("time");
    text.textContent = message.content;
    time.textContent = new Date(message.created_at).toLocaleString("zh-TW");
    item.append(text, time);
    return item;
  }));
}

async function loadMessages() {
  try {
    const response = await fetch("/api/messages");
    if (!response.ok) throw new Error("API 回應失敗");
    render(await response.json());
    statusBadge.textContent = "系統正常";
    statusBadge.classList.add("ok");
    errorBox.textContent = "";
  } catch (error) {
    statusBadge.textContent = "無法連線";
    statusBadge.classList.remove("ok");
    errorBox.textContent = error.message;
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorBox.textContent = "";
  try {
    const response = await fetch("/api/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: input.value }),
    });
    const body = await response.json();
    if (!response.ok) throw new Error(body.error || "新增失敗");
    input.value = "";
    await loadMessages();
  } catch (error) {
    errorBox.textContent = error.message;
  }
});

loadMessages();
