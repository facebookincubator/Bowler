/**
 * Copyright (c) 2017-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

const React = require('react');

class Footer extends React.Component {
  docUrl(doc, language) {
    const baseUrl = this.props.config.baseUrl;
    return baseUrl + 'docs/' + (language ? language + '/' : '') + doc;
  }

  imgUrl(img) {
    const baseUrl = this.props.config.baseUrl;
    return baseUrl + 'img/' + img;
  }

  pageUrl(doc, language) {
    const baseUrl = this.props.config.baseUrl;
    return baseUrl + (language ? language + '/' : '') + doc;
  }

  render() {
    const currentYear = new Date().getFullYear();
    let language = this.props.language || '';
    return (
      <footer className="nav-footer" id="footer">
        <section className="sitemap">
          <a
            href="https://code.facebook.com/projects/"
            target="_blank"
            rel="noreferrer noopener"
            className="fbOpenSource">
            <img
              src={this.props.config.baseUrl + 'img/oss_logo.png'}
              alt="Facebook Open Source"
              width="170"
              height="45"
            />
          </a>
          <a href={this.pageUrl('blog', language)}>
            News
          </a>
          <a href={'https://twitter.com/' + this.props.config.twitterUsername}>
            Twitter
          </a>
          <a href={this.props.config.repoUrl}>
            GitHub
          </a>
          <a href={this.docUrl('dev-intro', language)}>
            Contribute to Bowler
          </a>
          <img
            src={this.props.config.baseUrl + this.props.config.footerIcon}
            alt="Bowler"
            height="45"
            />
        </section>

        <section className="copyright">{this.props.config.copyright}</section>
      </footer>
    );
  }
}

module.exports = Footer;
