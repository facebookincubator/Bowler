
import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  
{
  path: '/',
  component: ComponentCreator('/'),
  exact: true,
  
},
{
  path: '/blog',
  component: ComponentCreator('/blog'),
  exact: true,
  
},
{
  path: '/blog/2018/08/24/launch',
  component: ComponentCreator('/blog/2018/08/24/launch'),
  exact: true,
  
},
{
  path: '/help',
  component: ComponentCreator('/help'),
  exact: true,
  
},
{
  path: '/users',
  component: ComponentCreator('/users'),
  exact: true,
  
},
{
  path: '/docs/:route',
  component: ComponentCreator('/docs/:route'),
  
  routes: [
{
  path: '/docs/api-commands',
  component: ComponentCreator('/docs/api-commands'),
  exact: true,
  
},
{
  path: '/docs/api-filters',
  component: ComponentCreator('/docs/api-filters'),
  exact: true,
  
},
{
  path: '/docs/api-modifiers',
  component: ComponentCreator('/docs/api-modifiers'),
  exact: true,
  
},
{
  path: '/docs/api-query',
  component: ComponentCreator('/docs/api-query'),
  exact: true,
  
},
{
  path: '/docs/api-selectors',
  component: ComponentCreator('/docs/api-selectors'),
  exact: true,
  
},
{
  path: '/docs/basics-intro',
  component: ComponentCreator('/docs/basics-intro'),
  exact: true,
  
},
{
  path: '/docs/basics-refactoring',
  component: ComponentCreator('/docs/basics-refactoring'),
  exact: true,
  
},
{
  path: '/docs/basics-setup',
  component: ComponentCreator('/docs/basics-setup'),
  exact: true,
  
},
{
  path: '/docs/basics-usage',
  component: ComponentCreator('/docs/basics-usage'),
  exact: true,
  
},
{
  path: '/docs/dev-intro',
  component: ComponentCreator('/docs/dev-intro'),
  exact: true,
  
},
{
  path: '/docs/dev-roadmap',
  component: ComponentCreator('/docs/dev-roadmap'),
  exact: true,
  
}],
},
  
  {
    path: '*',
    component: ComponentCreator('*')
  }
];
