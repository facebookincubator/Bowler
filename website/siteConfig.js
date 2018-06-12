/**
 * Copyright (c) 2017-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

// See https://docusaurus.io/docs/site-config.html for all the possible
// site configuration options.

/* List of projects/orgs using your project for the users page */
const users = [
  {
    caption: 'Facebook Engineering',
    // You will need to prepend the image path with your baseUrl
    // if it is not '/', like: '/test-site/img/docusaurus.svg'.
    image: '/img/bowler.png',
    infoLink: 'https://code.facebook.com',
    pinned: true,
  },
];

const repoUrl = 'https://github.com/facebookincubator/bowler';

const siteConfig = {
  title: 'Bowler' /* title for your website */,
  tagline: 'Safe code refactoring for modern Python',
  url: 'https://pybowler.io' /* your website url */,
  baseUrl: '/' /* base url for your project */,
  // For github.io type URLs, you would set the url and baseUrl like:
  //   url: 'https://facebook.github.io',
  //   baseUrl: '/test-site/',

  // Used for publishing and more
  projectName: 'bowler',
  organizationName: 'facebookincubator',
  // For top-level user or org sites, the organization is still the same.
  // e.g., for the https://JoelMarcey.github.io site, it would be set like...
  //   organizationName: 'JoelMarcey'

  // For no header links in the top nav bar -> headerLinks: [],
  headerLinks: [
    {doc: 'basics-intro', label: 'Getting Started'},
    {doc: 'api-query', label: 'API Reference'},
    {doc: 'dev-roadmap', label: 'Roadmap'},
    {href: repoUrl, label: 'Github'},
    // {blog: true, label: 'Blog'},
  ],

  // If you have users set above, you add it here:
  users,

  /* path to images for header/footer */
  headerIcon: 'img/logo/Bowler_Light.png',
  footerIcon: 'img/logo/Bowler_Light.svg',
  favicon: 'img/favicon/Oddy.png',

  /* colors for website */
  colors: {
    primaryColor: '#383938',
    // primaryColor: '#3964a8',
    primaryColor: '#20232a',
    secondaryColor: '#3956a6',
  },

  /* custom fonts for website */
  fonts: {
    myFont: [
      "-apple-system",
      "system-ui",
      "sans"
    ],
    myOtherFont: [
      "-apple-system",
      "system-ui"
    ]
  },

  // This copyright info is used in /core/Footer.js and blog rss/atom feeds.
  copyright:
    'Copyright © ' +
    new Date().getFullYear() +
    ' Facebook Inc.',

  highlight: {
    // Highlight.js theme to use for syntax highlighting in code blocks
    theme: 'atom-one-dark',
  },
  usePrism: ['bash', 'python'],

  // Add custom scripts here that would be placed in <script> tags
  scripts: ['https://buttons.github.io/buttons.js'],

  /* On page navigation for the current documentation page */
  onPageNav: 'separate',

  cleanUrl: true,
  scrollToTop: true,

  twitter: true,
  twitterUsername: 'fbOpenSource',

  /* Open Graph and Twitter card images */
  ogImage: 'img/logo/Bowler_FullColor_DarkText.png',
  twitterImage: 'img/logo/Bowler_FullColor_DarkText.png',

  // You may provide arbitrary config keys to be used as needed by your
  // template. For example, if you need your repo's URL...
  repoUrl: repoUrl,
};

module.exports = siteConfig;
