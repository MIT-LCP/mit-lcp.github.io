---
layout: default
title: Home
---

<!-- Main Content -->
<div class="container">
  <!-- Welcome Section -->
  <section class="content-section">
    <h2 class="section-title">
      <span class="title-line-1">Welcome to</span>
      <span class="title-line-2">MIT-LCP</span>
    </h2>
    
    <div style="display: flex; gap: 2rem; margin-bottom: 2rem; align-items: flex-start;">
      <div style="flex: 1;">
        <p>
          The MIT Laboratory for Computational Physiology (MIT-LCP), under the direction of Professor Roger Mark, conducts research at the intersection of <span class="key-term">medicine</span>, <span class="key-term">engineering</span>, and <span class="key-term">data science</span>.
        </p>
        
        <p>
          Our laboratory focuses on developing computational methods and tools for analyzing physiological signals and clinical data, with particular emphasis on critical care medicine and patient monitoring systems.
        </p>
      </div>
      
      <div style="flex-shrink: 0; width: 300px; margin-top: 0; padding-top: 0;">
        <img src="{{ '/assets/images/lab1.jpg' | relative_url }}" alt="MIT LCP Laboratory" style="width: 100%; height: auto; border-radius: 8px; box-shadow: 0 3px 6px rgba(0,0,0,0.15); display: block; margin: 0; padding: 0;">
      </div>
    </div>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-top: 2rem;">
      <div class="card">
        <h3>Our Mission</h3>
        <p>To advance healthcare through <span class="key-term">open science</span>, <span class="key-term">reproducible research</span>, and innovative computational methods that improve patient outcomes in critical care settings.</p>
      </div>
      
      <div class="card">
        <h3>Key Projects</h3>
        <p>Our major projects include <a href="https://mimic.physionet.org" target="_blank">MIMIC</a> and <a href="https://physionet.org" target="_blank">PhysioNet</a>, supporting global research in <span class="key-term">clinical informatics</span>.</p>
      </div>
    </div>
  </section>

  <!-- Latest News Section -->
  <section class="content-section">
    <h2 class="section-title">
      <span class="title-line-1">Stay Updated</span>
      <span class="title-line-2">Latest News</span>
    </h2>
    
    {% for news_item in site.data.news limit:3 %}
    <div class="news-item">
      <div class="news-date">{{ news_item.date | date: "%B %d, %Y" }}</div>
      <h3 class="news-title">{{ news_item.title }}</h3>
      <p>{{ news_item.content | strip_html | truncate: 200 }}</p>
      {% if news_item.url %}
      <a href="{{ news_item.url }}">Read more →</a>
      {% endif %}
    </div>
    {% endfor %}
    
    <div style="text-align: center; margin-top: 2rem;">
      <a href="{{ '/news' | relative_url }}" class="btn">View All News</a>
    </div>
  </section>

  <!-- Quick Links -->
  <section class="content-section">
    <h2 class="section-title">
      <span class="title-line-1">Explore Our</span>
      <span class="title-line-2">Resources</span>
    </h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 2rem;">
      <a href="{{ '/people' | relative_url }}" class="card" style="text-decoration: none; text-align: center;">
        <h3>Meet Our Team</h3>
        <p>Learn about our researchers and collaborators</p>
      </a>
      
      <a href="{{ '/publications' | relative_url }}" class="card" style="text-decoration: none; text-align: center;">
        <h3>Publications</h3>
        <p>Browse our research papers and presentations</p>
      </a>
      
      <a href="https://physionet.org" target="_blank" class="card" style="text-decoration: none; text-align: center;">
        <h3>PhysioNet</h3>
        <p>Access our open-source physiological data</p>
      </a>
      
      <a href="https://mimic.physionet.org" target="_blank" class="card" style="text-decoration: none; text-align: center;">
        <h3>MIMIC</h3>
        <p>Explore our critical care database</p>
      </a>
    </div>
  </section>
</div>
