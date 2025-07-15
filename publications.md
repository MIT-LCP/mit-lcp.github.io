---
layout: default
title: Publications
---

<div class="container">
  <section class="content-section">
    <h2 class="section-title">
      <span class="title-line-1">Research</span>
      <span class="title-line-2">Publications</span>
    </h2>

    {% assign publications_by_year = site.data.publications | sort: 'year' | reverse %}

    {% for year_data in publications_by_year %}
      <div class="publication-year">
        <h3>{{ year_data.year }}</h3>
        
        {% for pub in year_data.publications %}
          <div class="publication-item">
            <div class="publication-title">
              {% if pub.url %}
                <a href="{{ pub.url }}" target="_blank">{{ pub.title }}</a>
              {% else %}
                {{ pub.title }}
              {% endif %}
            </div>
            
            <div class="publication-authors">{{ pub.authors }}</div>
            
            <div class="publication-details">
              <em>{{ pub.journal }}</em>
              {% if pub.volume %}, {{ pub.volume }}{% endif %}
              {% if pub.pages %}, {{ pub.pages }}{% endif %}
              {% if pub.date %}, {{ pub.date }}{% endif %}
            </div>
            
            <div class="publication-links">
              {% if pub.pdf %}
                <a href="{{ pub.pdf }}" target="_blank">PDF</a>
              {% endif %}
              {% if pub.doi %}
                <a href="https://doi.org/{{ pub.doi }}" target="_blank">DOI</a>
              {% endif %}
              {% if pub.pmid %}
                <a href="https://pubmed.ncbi.nlm.nih.gov/{{ pub.pmid }}/" target="_blank">PubMed</a>
              {% endif %}
            </div>
          </div>
        {% endfor %}
      </div>
    {% endfor %}

  </section>
</div> 