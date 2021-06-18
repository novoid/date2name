@ECHO OFF
REM change drive, e.g., D:
%~d1
REM change directory, e.g., D:\data processing\subdir\
cd %~dp1


"C:\Users\rottmrei\OneDrive\Tools\210618-date2name\date2name.exe" --short --dryrun %*

set /p DUMMY=Hit ENTER to continue...