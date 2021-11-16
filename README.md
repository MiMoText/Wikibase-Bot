Import of MiMoText WikiData

This Bot imports all Data of MiMoText. 

*Preparation*
Add Bot to WikiBase
Special Pages > Bot passwords
Enter Bot name > create
MiMoText default: ImportBot
Grant all privileges > create
note password

go to WikiBot/user-password.py 
add the line ('Admin', BotPassword('ImportBot', 'password') > save

Note: First Import needs Admin-Password authentification

*Import*
Properties
python3 pwb.py scripts/userscripts/importTSV.py data/ImportProperties.tsv

Items
python3 pwb.py scripts/userscripts/importTSV.py data/ImportItems.tsv

Authors
python3 pwb.py scripts/userscripts/importTSV.py data/Authors.tsv

Werke
python3 pwb.py scripts/userscripts/importTSV.py data/BGRF_100.tsv

Themenkonzepte und Raumkonzepte
python3 pwb.py scripts/userscripts/importTSV.py data/Themenvokabular.tsv 
python3 pwb.py scripts/userscripts/importTSV.py data/Raumvokabular.tsv

Topic Label 
python3 pwb.py scripts/userscripts/importTSV.py data/topic_label.tsv

Statements
python3 pwb.py scripts/userscripts/importTSV.py data/bgrf100_about_statements.tsv
python3 pwb.py scripts/userscripts/importTSV.py data/mmt_2020-11-19_11-38_statements.tsv

new-items_narrative_form
BGRF100_narrative_form_edit
BGRF2000-100_narrative_form_edit

narrative-loc