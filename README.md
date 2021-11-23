<div align="center" id="top"> 
  <!--<img src="./.github/app.gif" alt="Wikibase-Bot" />-->

  &#xa0;

  <!-- <a href="https://userscripts.netlify.app">Demo</a> -->
</div>

<h1 align="center">Wikibase-Bot</h1>

<p align="center">
  <img alt="Github top language" src="https://img.shields.io/github/languages/top/MiMoText/Wikibase-Bot?color=56BEB8">

  <img alt="Github language count" src="https://img.shields.io/github/languages/count/MiMoText/Wikibase-Bot?color=56BEB8">

  <img alt="Repository size" src="https://img.shields.io/github/repo-size/MiMoText/Wikibase-Bot?color=56BEB8">

  <!-- <img alt="License" src="https://img.shields.io/github/license/MiMoText/Wikibase-Bot?color=56BEB8"> -->

  <!-- <img alt="Github issues" src="https://img.shields.io/github/issues/MiMoText/Wikibase-Bot?color=56BEB8" /> -->

  <!-- <img alt="Github forks" src="https://img.shields.io/github/forks/MiMoText/Wikibase-Bot?color=56BEB8" /> -->

  <!-- <img alt="Github stars" src="https://img.shields.io/github/stars/MiMoText/Wikibase-Bot?color=56BEB8" /> -->
</p>

<!-- Status -->

<h4 align="center"> 
	🚧  Wikibase-Bot 🚀 Under construction...  🚧
</h4> 

<hr>

<p align="center">
  <a href="#dart-about">About</a> &#xa0; | &#xa0; 
  <!--<a href="#sparkles-features">Features</a> &#xa0; | &#xa0;-->
  <a href="#rocket-technologies">Technologies</a> &#xa0; | &#xa0;
  <a href="#white_check_mark-requirements">Requirements</a> &#xa0; | &#xa0;
  <a href="#checkered_flag-starting">Starting</a> &#xa0; | &#xa0;
  <!--<a href="#memo-license">License</a> &#xa0; | &#xa0;-->
  <a href="https://github.com/MiMoText" target="_blank">Author</a>
</p>

<br>

## About ##

This bot imports all data of MiMoText. 
The data come in TSV files and need a defined header to work.

## Technologies ##

The following tools were used in this project:

- [Python](https://www.python.org/)
- [Pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikibot/de)
- [Wikibase](https://wikiba.se/)

## Requirements ##

Before starting, you need to have [Git](https://git-scm.com) installed.

## Starting ##

Install or clone Pywikibot.
Move to scripts/userscripts in your Pywikibot folder.

```bash
# Clone this project
$ git clone https://github.com/MiMoText/Wikibase-Bot

# Access
$ cd Wikibase-Bot

```
Add a Bot to WikiBase
- Special Pages > Bot passwords
- Enter Bot name > create
- Grant all privileges > create
- copy password
- go to WikiBot/user-password.py 
- add the line 

```bash
('<user>', BotPassword('<bot-name>', '<password>') > save
```
Import data: 

```bash
#Import needs <user>-password authentification
$ python3 ../../../pwb.py login

#Properties
$ python3 ../../../pwb.py importTSV.py <wikibase-shortname> data/ImportProperties.tsv <sparql-endpoint>

#Items
$ python3 ../../../pwb.py importTSV.py <wikibase-shortname> data/ImportItems.tsv <sparql-endpoint>

#Authors
$ python3 ../../../pwb.py importTSV.py <wikibase-shortname> data/Authors.tsv <sparql-endpoint>

#BGRF
$ python3 ../../../pwb.py importTSV.py <wikibase-shortname> data/BGRF_100.tsv <sparql-endpoint>
$ python3 ../../../pwb.py importTSV.py <wikibase-shortname> data/BGRF_2000-100.tsv <sparql-endpoint>

#theme concepts and spatial concepts
$ python3 ../../../pwb.py importTSV.py <wikibase-shortname> data/Themenvokabular.tsv <sparql-endpoint>
$ python3 ../../../pwb.py importTSV.py <wikibase-shortname> data/Raumvokabular.tsv <sparql-endpoint>

#topic label 
$ python3 ../../../pwb.py importTSV.py <wikibase-shortname> data/topic_label.tsv <sparql-endpoint>

# statements
$ python3 ../../../pwb.py importTSV.py <wikibase-shortname> data/bgrf100_about_statements.tsv <sparql-endpoint>
$ python3 ../../../pwb.py importTSV.py <wikibase-shortname> data/bgrf2000-100_about_statements.tsv <sparql-endpoint>
$ python3 ../../../pwb.py importTSV.py <wikibase-shortname> data/mmt_2020-11-19_11-38_statements.tsv <sparql-endpoint>

#narrative form
$ python3 ../../../pwb.py importTSV.py <wikibase-shortname> data/new-items_narrative_form.tsv <sparql-endpoint>
$ python3 ../../../pwb.py importTSV.py <wikibase-shortname> data/BGRF100_narrative_form_edit.tsv <sparql-endpoint>
$ python3 ../../../pwb.py importTSV.py <wikibase-shortname> data/BGRF2000-100_narrative_form_edit.tsv <sparql-endpoint>

#narrative location
$ python3 ../../../pwb.py importTSV.py <wikibase-shortname> data/BGRF_100_narrative-location_reconciled.tsv <sparql-endpoint>
$ python3 ../../../pwb.py importTSV.py <wikibase-shortname> data/BGRF_2000-100_narrative-location.tsv <sparql-endpoint>
$ python3 ../../../pwb.py importTSV.py <wikibase-shortname> data/NER_narrative-loc.tsv <sparql-endpoint>
```



<!-- ## :memo: License ##

This project is under license from MIT. For more details, see the [LICENSE](LICENSE.md) file. -->


Made with :heart: by <a href="https://github.com/Most24" target="_blank">Moritz Steffes</a>

&#xa0;

<a href="#top">Back to top</a>
