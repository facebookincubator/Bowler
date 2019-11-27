export default {
  "plugins": [],
  "themes": [],
  "customFields": {},
  "themeConfig": {
    "navbar": {
      "title": "Bowler",
      "logo": {
        "alt": "Bowler",
        "src": "img/logo/Bowler_FullColor.svg"
      },
      "links": [
        {
          "to": "docs/basics-intro",
          "label": "Getting Started",
          "position": "right"
        },
        {
          "to": "docs/api-query",
          "label": "API Reference",
          "position": "right"
        },
        {
          "to": "docs/dev-roadmap",
          "label": "Roadmap",
          "position": "right"
        },
        {
          "href": "https://github.com/facebookincubator/bowler",
          "label": "GitHub",
          "position": "right"
        }
      ]
    },
    "footer": {
      "logo": {
        "alt": "Facebook Open Source Logo",
        "src": "img/oss_logo.png"
      },
      "copyright": "Copyright © 2019 Facebook, Inc."
    }
  },
  "title": "Bowler",
  "tagline": "Safe code refactoring for modern Python",
  "url": "https://pybowler.io",
  "baseUrl": "/",
  "projectName": "bowler",
  "organizationName": "facebookincubator",
  "favicon": "img/favicon/Oddy.png",
  "scripts": [
    "https://buttons.github.io/buttons.js"
  ],
  "presets": [
    [
      "@docusaurus/preset-classic",
      {
        "docs": {
          "path": "../docs",
          "sidebarPath": "/Users/diegoponce/Documents/projects/Bowler/website/sidebars.js"
        }
      },
      {
        "theme": {
          "customCss": "/Users/diegoponce/Documents/projects/Bowler/website/src/css/custom.css"
        }
      }
    ]
  ]
};