@ECHO OFF

pushd %~dp0

REM Command file for Sphinx landing page documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=source
set OUTPUTDIR=../../docs
set DOCTREEDIR=.doctrees

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.https://www.sphinx-doc.org/
	exit /b 1
)

if "%1" == "" goto html
if "%1" == "html" goto html

:html
%SPHINXBUILD% -b html -d %DOCTREEDIR% %SPHINXOPTS% %SOURCEDIR% %OUTPUTDIR%
goto end

:end
popd
