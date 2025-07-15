# MIT Laboratory for Computational Physiology Website

This is the Jekyll-based website for the MIT Laboratory for Computational Physiology (LCP), migrated from a Flask application to be hosted on GitHub Pages.

## Overview

The website showcases the research activities of the LCP, including:
- Information about the lab and its members
- Details about MIMIC and PhysioNet projects
- News and publications
- Contact information

## Migration from Flask to Jekyll

This site has been migrated from a Flask application to Jekyll for GitHub Pages hosting. Key changes include:

### Structure Changes
- **Flask templates** → **Jekyll layouts and includes**
- **Flask routes** → **Jekyll pages and collections**
- **Flask `url_for()`** → **Jekyll `relative_url` filter**
- **Flask `sitedata/`** → **Jekyll `_data/`**

### Key Files
- `_config.yml` - Jekyll configuration
- `_layouts/default.html` - Main layout template
- `_includes/` - Reusable components (head, navbar, footer)
- `_data/` - YAML data files (news, people)
- `assets/` - Static files (CSS, JS, images, PDFs)

### Data Migration
- `sitedata/news.yml` → `_data/news.yml`
- `sitedata/people.yml` → `_data/people.yml`
- Static files moved from `static/` to `assets/`

## Local Development

### Prerequisites
- Ruby (2.4 or higher)
- RubyGems
- Bundler

### Setup
1. Install dependencies:
   ```bash
   bundle install
   ```

2. Start the local server:
   ```bash
   bundle exec jekyll serve
   ```

3. Visit `http://localhost:4000` in your browser

## GitHub Pages Deployment

### Automatic Deployment
1. Push this repository to GitHub
2. Go to repository Settings → Pages
3. Select "Deploy from a branch" and choose `main` branch
4. The site will be available at `https://[username].github.io/mit-lcp.github.io`

### Manual Deployment
```bash
bundle exec jekyll build
```

The built site will be in the `_site/` directory.

## Content Management

### Adding News
Edit `_data/news.yml` to add new news items:

```yaml
news_items:
  - date: "2024-01-15"
    front_page: true
    header: "News"
    title: "New Publication"
    content: "Content here..."
    url: "https://example.com"
```

### Adding People
Edit `_data/people.yml` to add lab members:

```yaml
current_members:
  - name: "John Doe"
    image: "john_doe.jpg"
    biog: "Biography here..."
```

### Adding Pages
Create new `.html` files in the root directory with front matter:

```yaml
---
layout: default
title: Page Title
---
```

## Features

- **Responsive Design** - Bootstrap-based layout
- **News System** - YAML-based news management
- **People Directory** - Lab member profiles
- **Publication Archive** - Year-based publication organization
- **Static Asset Management** - Images, PDFs, and other files

## Customization

### Styling
- CSS files are in `assets/css/`
- Main styles: `custom.css`, `template.css`
- Bootstrap is included for responsive design

### Navigation
- Edit `_data/navigation.yml` to modify the main navigation
- Update `_includes/navbar.html` for structural changes

## Notes

- The publications page currently shows placeholder content during migration
- PDF files are preserved in `assets/pdf/`
- All images are in `assets/images/`
- The site maintains the original design and functionality

## Support

For issues or questions about the Jekyll migration, please contact the LCP team.
