---
layout: default
title: People
---

<div class="wrapper">
  <section class="content-section">
    <h1 class="section-title">Our Team</h1>
    <p class="section-subtitle">
      Meet the researchers, scientists, and collaborators of the Laboratory for Computational Physiology.
    </p>

    <div class="people-grid">
      {% for person in site.data.people %}
      <div class="person-card">
        {% if person.image %}
        <img src="{{ '/assets/images/' | append: person.image | relative_url }}" alt="{{ person.name }}" class="person-image">
        {% else %}
        <img src="{{ '/assets/images/missing.jpg' | relative_url }}" alt="{{ person.name }}" class="person-image">
        {% endif %}
        <h3 class="person-name">{{ person.name }}</h3>
        <p class="person-role">{{ person.role }}</p>
        <p>{{ person.bio }}</p>
      </div>
      {% endfor %}
    </div>

    <div style="text-align: center; margin-top: 3rem;">
      <h2 class="section-title">Join Our Lab</h2>
      <p class="section-subtitle">
        We offer research opportunities to MIT students and welcome collaborations with researchers worldwide.
      </p>
      <a href="{{ '/about' | relative_url }}" class="btn-hero" style="background: var(--mit-red); color: white;">Learn About Opportunities</a>
    </div>
  </section>
</div> 