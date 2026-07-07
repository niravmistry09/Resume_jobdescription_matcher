const compareForm = document.querySelector("#compare-form");
const resumeFileInput = document.querySelector("#resume-file");
const jdFileInput = document.querySelector("#jd-file");
const jdTextInput = document.querySelector("#jd-text");
const resumeFileName = document.querySelector("#resume-file-name");
const jdFileName = document.querySelector("#jd-file-name");
const compareButton = document.querySelector("#compare-button");
const loadingState = document.querySelector("#loading-state");
const formMessage = document.querySelector("#form-message");
const resultsSection = document.querySelector("#results-section");
const scoreRing = document.querySelector("#score-ring");
const matchScore = document.querySelector("#match-score");
const scoreSummary = document.querySelector("#score-summary");
const matchedSkills = document.querySelector("#matched-skills");
const missingSkills = document.querySelector("#missing-skills");
const suggestionsList = document.querySelector("#suggestions-list");
const aiExplanation = document.querySelector("#ai-explanation");
const analysisSource = document.querySelector("#analysis-source");

const compareEndpointUrl = "/api/v1/compare";

function updateFileName(input, output) {
  const [file] = input.files;
  output.textContent = file ? file.name : "No file selected";
}

function setLoading(isLoading) {
  compareButton.disabled = isLoading;
  loadingState.classList.toggle("d-none", !isLoading);
}

function setMessage(message, isError = false) {
  formMessage.textContent = message;
  formMessage.classList.toggle("error", isError);
}

function renderSkillPills(container, skills) {
  const safeSkills = skills || [];
  container.replaceChildren(
    ...safeSkills.map((skill) => {
      const pill = document.createElement("span");
      pill.className = "skill-pill";
      pill.textContent = skill;
      return pill;
    }),
  );
}

function renderSuggestions(suggestions) {
  const safeSuggestions = suggestions || [];
  suggestionsList.replaceChildren(
    ...safeSuggestions.map((suggestion) => {
      const item = document.createElement("li");
      item.textContent = suggestion;
      return item;
    }),
  );
}

function renderResults(data) {
  const score = Number(data.final_score || 0);
  const scoreDegrees = Math.max(0, Math.min(score, 100)) * 3.6;

  matchScore.textContent = `${score}%`;
  scoreRing.style.background = `conic-gradient(var(--brand) ${scoreDegrees}deg, var(--line) ${scoreDegrees}deg)`;
  scoreSummary.textContent = `Skill overlap: ${data.score_breakdown.skill_overlap_score}%. Semantic similarity: ${data.score_breakdown.semantic_similarity_score}%.`;
  aiExplanation.textContent = data.explanation
    ? data.explanation.explanation
    : data.warnings?.[0] || "AI explanation is not available for this response.";
  analysisSource.textContent = "POST /api/v1/compare";

  renderSkillPills(matchedSkills, data.matched_skills);
  renderSkillPills(missingSkills, data.missing_skills);
  renderSuggestions(data.suggestions || data.explanation?.suggestions || []);

  resultsSection.classList.remove("d-none");
}

async function fetchComparison(formData) {
  const response = await fetch(compareEndpointUrl, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorPayload = await response.json().catch(() => ({}));
    throw new Error(errorPayload.detail || "Unable to compare files.");
  }

  return response.json();
}

resumeFileInput.addEventListener("change", () => updateFileName(resumeFileInput, resumeFileName));
jdFileInput.addEventListener("change", () => updateFileName(jdFileInput, jdFileName));

compareForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!resumeFileInput.files.length) {
    setMessage("Please upload a resume file before comparing.", true);
    return;
  }

  if (!jdFileInput.files.length && !jdTextInput.value.trim()) {
    setMessage("Please upload a JD file or paste job description text.", true);
    return;
  }

  const formData = new FormData();
  formData.append("resume", resumeFileInput.files[0]);
  if (jdTextInput.value.trim()) {
    formData.append("job_description_text", jdTextInput.value.trim());
  } else {
    formData.append("job_description", jdFileInput.files[0]);
  }

  setMessage("");
  setLoading(true);

  try {
    const data = await fetchComparison(formData);
    renderResults(data);
    setMessage(data.warnings?.[0] || "Comparison complete.");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Something went wrong.";
    setMessage(message, true);
  } finally {
    setLoading(false);
  }
});
