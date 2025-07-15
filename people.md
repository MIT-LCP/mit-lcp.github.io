---
layout: default
title: People
---

<div class="container">
  <section class="content-section">
    <h2 class="section-title">
      <span class="title-line-1">Meet our</span>
      <span class="title-line-2">Team</span>
    </h2>

    <div class="people-list">
      {% for person in site.data.people %}
      <div class="person-item">
        <div class="person-photo-container">
          {% if person.image %}
          <img src="{{ '/assets/images/' | append: person.image | relative_url }}" alt="{{ person.name }}" class="person-photo">
          {% else %}
          <img src="{{ '/assets/images/missing.jpg' | relative_url }}" alt="{{ person.name }}" class="person-photo">
          {% endif %}
        </div>
        <div class="person-info">
          <h3 class="person-name">{{ person.name }}</h3>
          <p class="person-title">{{ person.role }}</p>
          <p>{{ person.bio }}</p>
        </div>
      </div>
      {% endfor %}
    </div>

    <div style="text-align: center; margin-top: 3rem;">
      <h2 class="section-title">
        <span class="title-line-1">Collaboration</span>
        <span class="title-line-2">Join Our Lab</span>
      </h2>
      <p>
        We offer research opportunities to MIT students and welcome collaborations with researchers worldwide.
      </p>
      <a href="{{ '/about' | relative_url }}" class="btn">Learn About Opportunities</a>
    </div>
  </section>
</div> 