const form = document.querySelector("#study-form");
const submitButton = document.querySelector("#submit-button");
const loading = document.querySelector("#loading");
const errorPanel = document.querySelector("#error");
const results = document.querySelector("#results");
const summaryList = document.querySelector("#summary-list");
const quizContainer = document.querySelector("#quiz-container");
const checkButton = document.querySelector("#check-answers");
const scorePanel = document.querySelector("#quiz-score");

let currentQuiz = [];

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  hide(errorPanel);
  hide(results);
  show(loading);
  submitButton.disabled = true;
  submitButton.querySelector("span").textContent = "Working on it…";

 const payload = {
  video_url: form.elements.video_url.value.trim(),
  transcript_text: form.elements.transcript_text.value.trim(),
  language: form.elements.language.value,
  quiz_count: 5,
};

  try {
    const response = await fetch("/api/study", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "The study guide could not be created.");
    }

    renderResults(data);
  } catch (error) {
    errorPanel.textContent = error.message;
    show(errorPanel);
  } finally {
    hide(loading);
    submitButton.disabled = false;
    submitButton.querySelector("span").textContent = "Build my study guide";
  }
});

function renderResults(data) {
  document.querySelector("#result-title").textContent = data.title || "Your study guide";
  const watchLink = document.querySelector("#watch-link");
if (data.video_url) {
  watchLink.href = data.video_url;
  watchLink.classList.remove("hidden");
} else {
  watchLink.classList.add("hidden");
}

  summaryList.replaceChildren();
  for (const point of data.summary || []) {
    const item = document.createElement("li");
    item.textContent = point;
    summaryList.append(item);
  }

  currentQuiz = data.quiz || [];
  quizContainer.replaceChildren();
  hide(scorePanel);
  checkButton.disabled = false;
  checkButton.innerHTML = 'Check my answers <span>→</span>';

  currentQuiz.forEach((question, index) => {
    const wrapper = document.createElement("div");
    wrapper.className = "question";

    const number = document.createElement("div");
    number.className = "question-number";
    number.textContent = `QUESTION ${String(index + 1).padStart(2, "0")}`;

    const title = document.createElement("div");
    title.className = "question-title";
    title.textContent = question.question;

    wrapper.append(number, title);

    question.options.forEach((option, optionIndex) => {
      const label = document.createElement("label");
      label.className = "option";

      const input = document.createElement("input");
      input.type = "radio";
      input.name = `question-${index}`;
      input.value = optionIndex;

      const text = document.createElement("span");
      text.textContent = option;

      label.append(input, text);
      wrapper.append(label);
    });

    quizContainer.append(wrapper);
  });

  show(results);
  results.scrollIntoView({ behavior: "smooth", block: "start" });
}

checkButton.addEventListener("click", () => {
  let score = 0;

  currentQuiz.forEach((question, index) => {
    const selected = document.querySelector(`input[name="question-${index}"]:checked`);
    const optionLabels = document.querySelectorAll(
      `.question:nth-child(${index + 1}) .option`
    );

    optionLabels.forEach((label, optionIndex) => {
      label.classList.remove("correct", "incorrect");
      if (optionIndex === question.answer_index) label.classList.add("correct");
      if (selected && Number(selected.value) === optionIndex &&
          optionIndex !== question.answer_index) {
        label.classList.add("incorrect");
      }
    });

    if (selected && Number(selected.value) === question.answer_index) score++;

    const existing = document.querySelector(`#explanation-${index}`);
    if (existing) existing.remove();

    const explanation = document.createElement("p");
    explanation.id = `explanation-${index}`;
    explanation.className = "explanation";
    explanation.textContent = `Answer: ${question.explanation}`;
    document.querySelectorAll(".question")[index].append(explanation);
  });

  scorePanel.textContent = `You got ${score} out of ${currentQuiz.length} correct.`;
  show(scorePanel);
  checkButton.disabled = true;
  checkButton.textContent = "Answers checked ✓";
});

function show(element) {
  element.classList.remove("hidden");
}

function hide(element) {
  element.classList.add("hidden");
}