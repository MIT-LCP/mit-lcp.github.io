---
layout: default
title: News
---

<div class="wrapper">
  <section class="content-section">
    <h1 class="section-title">News & Updates</h1>

    {% for news_item in site.data.news %}
    <div class="news-item">
      <div class="news-date">{{ news_item.date | date: "%B %d, %Y" }}</div>
      <h3 class="news-title">{{ news_item.title }}</h3>
      <div>{{ news_item.content }}</div>
      {% if news_item.url %}
      <p style="margin-top: 1rem;">
        <a href="{{ news_item.url }}" target="_blank" style="color: var(--mit-red); font-weight: 600;">Read full article →</a>
      </p>
      {% endif %}
    </div>
    {% endfor %}

    <div style="text-align: center; margin-top: 3rem;">
      <h2 class="section-title">Stay Connected</h2>
      <p class="section-subtitle">
        Follow our research and get updates on new publications, datasets, and collaborations.
      </p>
      <a href="https://physionet.org" target="_blank" class="btn-hero" style="background: var(--mit-red); color: white;">Visit PhysioNet</a>
    </div>
  </section>
</div> 