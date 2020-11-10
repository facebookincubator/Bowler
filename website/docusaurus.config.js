/**
 * Copyright (c) 2017-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

// See https://docusaurus.io/docs/site-config.html for all the possible
// site configuration options.

const repoUrl = 'https://github.com/facebookincubator/bowler';
const twitterUsername= 'fbOpenSource';

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

  /* path to images for header/footer */
  favicon: 'img/favicon/Oddy.png',

  // Add custom scripts here that would be placed in <script> tags
  scripts: ['https://buttons.github.io/buttons.js'],
  
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          // docs folder path relative to website dir.
          path: '../docs',
          // sidebars file relative to website dir.
          sidebarPath: require.resolve('./sidebars.js'),
        },
      },
      {
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
  themeConfig: {
    navbar: {
      title: 'Bowler',
      logo: {
        alt: 'Bowler',
        src: 'img/logo/Bowler_FullColor.svg',
      },
      links: [
        {to: 'docs/basics-intro', label: 'Getting Started', position: 'right'},
        {to: 'docs/api-query', label: 'API Reference', position: 'right'},
        {to: 'docs/dev-roadmap', label: 'Roadmap', position: 'right'},
        {
          href: repoUrl,
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      logo: {
        alt: 'Facebook Open Source Logo',
        src: 'img/oss_logo.png',
      },
      copyright: `Copyright © ${new Date().getFullYear()} Facebook, Inc.`,
    }
  },
};

module.exports = siteConfig;
