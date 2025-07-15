---
layout: default
title: Home
---

<!-- Hero Section -->
<section class="hero-section">
  <div class="wrapper">
    <div class="hero-content">
      <h1>Laboratory for Computational Physiology</h1>
      <p class="lead">
        Advancing healthcare through computational physiology, data science, and machine learning at the intersection of medicine and engineering.
      </p>
      <a href="{{ '/about' | relative_url }}" class="btn-hero">Learn More About Our Research</a>
    </div>
  </div>
</section>

<!-- Main Content -->
<div class="wrapper">
  <!-- About Section -->
  <section class="content-section">
    <h2 class="section-title">About Our Lab</h2>
    <p class="section-subtitle">
      The Laboratory for Computational Physiology (LCP), under the direction of Professor Roger Mark, conducts research at the intersection of medicine, engineering, and data science.
    </p>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-top: 2rem;">
      <div class="card">
        <div class="card-header">Research Focus</div>
        <div class="card-body">
          <p>We develop and refine methods for analyzing data from patients in intensive care units and generate predictive models to aid in patient care.</p>
        </div>
      </div>
      
      <div class="card">
        <div class="card-header">Key Projects</div>
        <div class="card-body">
          <p>Our major projects include <a href="https://mimic.physionet.org" target="_blank">MIMIC</a> and <a href="https://physionet.org" target="_blank">PhysioNet</a>, supporting global research in clinical informatics.</p>
        </div>
      </div>
      
      <div class="card">
        <div class="card-header">Collaboration</div>
        <div class="card-body">
          <p>We collaborate with clinicians, data scientists, and engineers worldwide to improve healthcare through open science and reproducible research.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Latest News Section -->
  <section class="content-section">
    <h2 class="section-title">Latest News</h2>
    
    {% for news_item in site.data.news limit:3 %}
    <div class="news-item">
      <div class="news-date">{{ news_item.date | date: "%B %d, %Y" }}</div>
      <h3 class="news-title">{{ news_item.title }}</h3>
      <p>{{ news_item.content | strip_html | truncate: 200 }}</p>
      {% if news_item.url %}
      <a href="{{ news_item.url }}" target="_blank">Read more →</a>
      {% endif %}
    </div>
    {% endfor %}
    
    <div style="text-align: center; margin-top: 2rem;">
      <a href="{{ '/news' | relative_url }}" class="btn-hero" style="background: var(--mit-red); color: white;">View All News</a>
    </div>
  </section>

  <!-- Quick Links -->
  <section class="content-section">
    <h2 class="section-title">Quick Links</h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 2rem;">
      <a href="{{ '/people' | relative_url }}" class="card" style="text-decoration: none; text-align: center;">
        <div class="card-body">
          <h3 style="color: var(--mit-red);">Meet Our Team</h3>
          <p>Learn about our researchers and collaborators</p>
        </div>
      </a>
      
      <a href="{{ '/publications' | relative_url }}" class="card" style="text-decoration: none; text-align: center;">
        <div class="card-body">
          <h3 style="color: var(--mit-red);">Publications</h3>
          <p>Browse our research papers and presentations</p>
        </div>
      </a>
      
      <a href="https://physionet.org" target="_blank" class="card" style="text-decoration: none; text-align: center;">
        <div class="card-body">
          <h3 style="color: var(--mit-red);">PhysioNet</h3>
          <p>Access our open-source physiological data</p>
        </div>
      </a>
      
      <a href="https://mimic.physionet.org" target="_blank" class="card" style="text-decoration: none; text-align: center;">
        <div class="card-body">
          <h3 style="color: var(--mit-red);">MIMIC</h3>
          <p>Explore our critical care database</p>
        </div>
      </a>
    </div>
  </section>
</div>
