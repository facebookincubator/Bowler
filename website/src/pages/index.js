import React from "react";
import classnames from "classnames";
import Layout from "@theme/Layout";
import Link from "@docusaurus/Link";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import withBaseUrl from "@docusaurus/withBaseUrl";
import styles from "./styles.module.css";

const features = [
  {
    title: <>Flexible</>,
    description: (
      <>
        Use Bowler for automated changes, interactive diffs, or as just another library component in your editor or toolchain.
      </>
    )
  },
  {
    title: <>Fluent</>,
    description: (
      <>
        Designed to enable simple, composable, and reusable refactoring scripts that can provide ongoing utility rather than throwing away after each use.
      </>
    )
  },
  {
    title: <>Future Ready</>,
    description: (
      <>
        Built on standard libraries, to support new versions of Python before they get released, while remaining backward compatible with all previous versions of Python.
      </>
    )
  }
];

const Index = () => {
  const context = useDocusaurusContext();
  const { siteConfig = {} } = context;

  return (
    <Layout
      title={`${siteConfig.title} - ${siteConfig.tagline}`}
      description={siteConfig.tagline}
    >
      <header className={classnames("hero hero--primary", styles.heroBanner)}>
        <div className="container">
          <h1 className="hero__title">{siteConfig.title}</h1>
          <p className="hero__subtitle">{siteConfig.tagline}</p>
          <div className={styles.buttons}>
            <Link
              className={classnames(
                "button button--secondary button--lg",
                styles.getStarted
              )}
              to={withBaseUrl("docs/basics-intro")}
            >
              Get Started
            </Link>
            <Link
              className={classnames(
                "button button--secondary button--lg",
                styles.getStarted
              )}
              to={withBaseUrl("docs/basics-refactoring")}
            >
              How it works
            </Link>
          </div>
        </div>
      </header>
      <main>
        {features && features.length && (
          <section className={styles.features}>
            <div className="container">
              <div className="row">
                {features.map(({ title, description }, idx) => (
                  <div
                    key={idx}
                    className={classnames("col col--4", styles.feature)}
                  >
                    <h3>{title}</h3>
                    <p>{description}</p>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}
      </main>
      <section>
        <div className="container">
          <div className="row">
            <div
              className={classnames("col col--offset-2 col--8")}
            >
              <h3>Bowler</h3>
              <img
                alt="Docusaurus with Keytar"
                src={withBaseUrl('/img/demo.gif')} 
              />
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Index;



// const React = require('react');

// const CompLibrary = require('../../core/CompLibrary.js');
// const MarkdownBlock = CompLibrary.MarkdownBlock; /* Used to read markdown */
// const Container = CompLibrary.Container;
// const GridBlock = CompLibrary.GridBlock;

// const siteConfig = require(process.cwd() + '/siteConfig.js');

// function imgUrl(img) {
//   return siteConfig.baseUrl + 'img/' + img;
// }

// function docUrl(doc, language) {
//   return siteConfig.baseUrl + 'docs/' + (language ? language + '/' : '') + doc;
// }

// function pageUrl(page, language) {
//   return siteConfig.baseUrl + (language ? language + '/' : '') + page;
// }

// class Button extends React.Component {
//   render() {
//     return (
//       <div className="pluginWrapper buttonWrapper">
//         <a className="button" href={this.props.href} target={this.props.target}>
//           {this.props.children}
//         </a>
//       </div>
//     );
//   }
// }

// Button.defaultProps = {
//   target: '_self',
// };

// const SplashContainer = props => (
//   <div className="homeContainer">
//     <div className="homeSplashFade">
//       <div className="wrapper homeWrapper">{props.children}</div>
//     </div>
//   </div>
// );

// const Logo = props => (
//   <div className="projectLogo">
//     <img src={props.img_src} />
//   </div>
// );

// const ProjectTitle = props => (
//   <h2 className="projectTitle">
//     <img src={imgUrl('logo/Bowler_TextOnly_Dark.svg')} height="72" alt="Bowler" />
//     <small>{siteConfig.tagline}</small>
//   </h2>
// );

// const PromoSection = props => (
//   <div className="section promoSection">
//     <div className="promoRow">
//       <div className="pluginRowBlock">{props.children}</div>
//     </div>
//   </div>
// );

// class HomeSplash extends React.Component {
//   render() {
//     let language = this.props.language || '';
//     return (
//       <SplashContainer>
//         <Logo img_src={imgUrl('logo/Bowler_FullColor.svg')} />
//         <div className="inner">
//           <ProjectTitle />
//           <PromoSection>
//             <Button href={docUrl('basics-intro', language)}>Getting Started</Button>
//             <Button href={docUrl('basics-refactoring', language)}>How it Works</Button>
//           </PromoSection>
//         </div>
//       </SplashContainer>
//     );
//   }
// }

// const Block = props => (
//   <Container
//     padding={['bottom', 'top']}
//     id={props.id}
//     background={props.background}>
//     <GridBlock align="left" contents={props.children} layout={props.layout} />
//   </Container>
// );

// class Index extends React.Component {
//   render() {
//     let language = this.props.language || '';

//     return (
//       <div>
//         <HomeSplash language={language} />
//         <div className="mainContainer">
//           <Container padding={['bottom', 'top']} background="light">
//             <GridBlock align="center" layout="fourColumn" contents={[
//                 {
//                   title: 'Flexible',
//                   content: 'Use Bowler for automated changes, interactive diffs, or as just another library component in your editor or toolchain.',
//                   //image: imgUrl('docusaurus.svg'),
//                   //imageAlign: 'top',
//                 },
//                 {
//                   title: 'Fluent',
//                   content: 'Designed to enable simple, composable, and reusable refactoring scripts that can provide ongoing utility rather than throwing away after each use.',
//                   //image: imgUrl('docusaurus.svg'),
//                   //imageAlign: 'top',
//                 },
//                 {
//                   title: 'Future Ready',
//                   content: 'Built on standard libraries, to support new versions of Python before they get released, while remaining backward compatible with all previous versions of Python.',
//                   //image: imgUrl('docusaurus.svg'),
//                   //imageAlign: 'top',
//                 }
//               ]} />
//           </Container>
//           <Container padding={['bottom', 'top']}>
//             <GridBlock align="center" layout="fourColumn" contents={[
//               {
//                 title: 'Bowler in Action',
//                 content: '<script src="https://asciinema.org/a/txpYgkb4tdQxvK2od9evzlVov.js" id="asciicast-txpYgkb4tdQxvK2od9evzlVov" async></script>',
//               }
//             ]} />
//           </Container>
//         </div>
//       </div>
//     );
//   }
// }

// module.exports = Index;
