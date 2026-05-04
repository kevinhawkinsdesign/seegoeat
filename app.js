function stars(rating) {
  return "★".repeat(rating) + "☆".repeat(5 - rating);
}

function renderCard(place) {
  return `
    <article class="card" data-category="${place.category}">
      <div class="card-emoji">${place.emoji}</div>
      <div class="card-body">
        <div class="card-meta">
          <span class="category-badge ${place.category}">${place.category}</span>
          <span class="stars">${stars(place.rating)}</span>
        </div>
        <h2 class="card-name">${place.name}</h2>
        <p class="card-desc">${place.description}</p>
        <p class="card-address">📍 ${place.address}</p>
        <div class="card-tags">
          ${place.tags.map(t => `<span class="tag">${t}</span>`).join("")}
        </div>
        <a class="map-link" href="${place.mapUrl}" target="_blank" rel="noopener">
          Open in Google Maps →
        </a>
      </div>
    </article>
  `;
}

function render(filter) {
  const grid = document.getElementById("places-grid");
  const filtered = filter === "all" ? places : places.filter(p => p.category === filter);
  grid.innerHTML = filtered.length
    ? filtered.map(renderCard).join("")
    : `<p class="empty">No places in this category yet.</p>`;
}

document.querySelectorAll(".filter-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    render(btn.dataset.filter);
  });
});

render("all");
