import React from "react";
import classnames from "classnames";
import Layout from "@theme/Layout";
import Link from "@docusaurus/Link";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import useBaseUrl from "@docusaurus/useBaseUrl";
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
              to={useBaseUrl("docs/basics-intro")}
            >
              Get Started
            </Link>
            <Link
              className={classnames(
                "button button--secondary button--lg",
                styles.getStarted
              )}
              to={useBaseUrl("docs/basics-refactoring")}
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
                src={useBaseUrl('/img/demo.gif')} 
              />
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Index;