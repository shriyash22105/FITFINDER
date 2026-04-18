@echo off
cd /d d:\PROJECTS\FITFINDER-

echo Moving documentation files to docs/...
if exist API_DOCUMENTATION.md move API_DOCUMENTATION.md docs\
if exist PROJECT_SYNOPSIS.md move PROJECT_SYNOPSIS.md docs\
if exist INDEX.md move INDEX.md docs\
if exist SYNOPSIS.md move SYNOPSIS.md docs\
if exist TODO.md move TODO.md docs\

echo Moving legacy files to _junk/...
if exist diagrams2 move diagrams2 _junk\
if exist target move target _junk\
if exist uploads move uploads _junk\
if exist __pycache__ move __pycache__ _junk\
if exist test_cloth.jpg move test_cloth.jpg _junk\
if exist test_person.jpg move test_person.jpg _junk\
if exist fitfinder.db move fitfinder.db _junk\
if exist users.mv.db move users.mv.db _junk\
if exist users.trace.db move users.trace.db _junk\
if exist nul move nul _junk\
if exist stop move stop _junk\
if exist generated_outfits move generated_outfits _junk\
if exist tmp move tmp _junk\

echo Organization complete!
dir /b docs\
echo ---
dir /b _junk\