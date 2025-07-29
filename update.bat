
@echo off
REM the %0 is the path to the batch file
git add --all
git commit -m %1
git push origin main