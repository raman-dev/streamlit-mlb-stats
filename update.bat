
@echo off
REM the %0 is the path to the batch file
@echo on
git add --all
git commit -m %1
git push origin main